import type { AgentRef, AgentSession, ExtensionAPI, ExtensionContext, ToolDefinition } from "@oh-my-pi/pi-coding-agent";
import { AgentLifecycleManager } from "@oh-my-pi/pi-coding-agent/registry/agent-lifecycle";
import { registerPersistedSubagents } from "@oh-my-pi/pi-coding-agent/registry/persisted-agents";
import { TASK_SUBAGENT_LIFECYCLE_CHANNEL, type SubagentLifecyclePayload } from "@oh-my-pi/pi-coding-agent/task";
import {
	Admission, assertExecutiveTool, EXECUTIVE_TOOLS, executivePrompt, LIMITS, MAX_PLAN_CHARS, PLAN_ENTRY, type Role,
} from "./policy.ts";

/**
 * Native OMP 18.1.16 authoring contract:
 * - ExtensionAPI tool_call is fail-closed, ordinary event callbacks are NOT.
 * - Agent.addBeforeModelCallHook is an awaited, throwing execution gate; it
 *   covers initial prompts, queued continuations, and warm/cold IRC revival.
 * - AgentRegistry + session_init identify roles; displayName/hasUI do not.
 * - ctx.invokeTool delegates to the original same-name native tool after our
 *   final-argument checks. task execution/integration remain entirely native.
 * - AgentLifecycleManager.release(..., { tombstone:true }) preserves native
 *   terminal identity across restart; AsyncJob.promise is the settlement proof.
 * These are public package exports, including the registry/* subpath exports.
 *
 * Operator opt-out: set OMP_EXECUTIVE_POLICY=off BEFORE launching omp. The
 * decision is captured on module import, not read from model-callable input or
 * changed by executive_control. User slash commands/shell remain operator
 * authority. This trusted-extension/worker policy prevents accidental role
 * drift; arbitrary trusted JS/extensions/workers are not an OS security sandbox.
 * Native readers may write caches/WAL bookkeeping or issue network GETs. Native
 * task patch/branch application is explicitly permitted delegated implementation.
 *
 * OMP collects missing/broken extension-load errors instead of stopping startup.
 * An operator must attest loading (executive_control status) before relying on
 * this policy. A policy that never loaded CANNOT enforce a startup failure.
 */
const ENABLED = process.env.OMP_EXECUTIVE_POLICY !== "off";
const STATE_KEY = Symbol.for("misty-step.omp-config.executive.runtime.v1");
const CANCEL_TIMEOUT_MS = 15_000;

type Registry = ReturnType<ExtensionAPI["pi"]["AgentRegistry"]["global"]>;
type NativeTool = NonNullable<ReturnType<AgentSession["getToolByName"]>>;
type Job = ReturnType<NonNullable<AgentSession["asyncJobManager"]>["getAllJobs"]>[number];

type Binding = {
	ref: AgentRef;
	session: AgentSession;
	rootSessionId: string;
	ready: boolean;
	failure?: string;
	disposeHooks: () => void;
};
type Cancellation = {
	owner: AgentRef;
	ownerSessionId: string;
	target?: AgentRef;
	refs: Set<AgentRef>;
	sessions: Map<AgentRef, AgentSession>;
	jobs: Set<Job>;
	settled: boolean;
	error?: string;
	completion: Promise<void>;
};
type Runtime = {
	admission: Admission;
	bindings: WeakMap<AgentSession, Binding>;
	cancellations: Set<Cancellation>;
	taskCalls: Map<AgentRef, Set<Promise<unknown>>>;
};

function runtime(registry: Registry): Runtime {
	const host = registry as Registry & { [STATE_KEY]?: Runtime };
	return host[STATE_KEY] ??= {
		admission: new Admission(), bindings: new WeakMap(), cancellations: new Set(), taskCalls: new Map(),
	};
}

function roleOf(ref: AgentRef): Role {
	if (ref.kind === "main" && ref.id === "Main") return "main";
	if (ref.kind !== "sub") throw new Error("Executive policy: unsupported native agent identity.");
	const entries = ref.session?.sessionManager.getEntries();
	if (entries) {
		for (let i = entries.length - 1; i >= 0; i--) {
			const entry = entries[i];
			if (entry.type === "session_init" && typeof entry.agent === "string") {
				return entry.agent === "executive" ? "executive" : "worker";
			}
		}
		// A live session without its native contract is NOT presumed to be a worker.
		throw new Error("Executive policy: native session_init agent identity is unavailable.");
	}
	if (ref.history?.agent) return ref.history.agent === "executive" ? "executive" : "worker";
	throw new Error(`Executive policy: agent ${ref.id} has no authoritative role metadata.`);
}

function lineage(registry: Registry, ref: AgentRef): AgentRef[] {
	const ancestors: AgentRef[] = [];
	const seen = new Set<AgentRef>();
	let current: AgentRef | undefined = ref;
	while (current) {
		if (seen.has(current)) throw new Error("Executive policy: cyclic native parent identity.");
		seen.add(current);
		ancestors.push(current);
		if (current.kind === "main" && current.id === "Main") return ancestors;
		current = current.parentId ? registry.get(current.parentId) : undefined;
	}
	throw new Error(`Executive policy: ${ref.id} is not attached to native Main's tree.`);
}

function rootOf(registry: Registry, ref: AgentRef): AgentRef {
	return lineage(registry, ref).at(-1)!;
}

function belongsToCurrentRoot(registry: Registry, ref: AgentRef): boolean {
	let root: AgentRef;
	try { root = rootOf(registry, ref); } catch { return false; }
	if (!root.session || root.session.isDisposed) return false;
	if (root === ref) return true;
	const rootFile = root.session.sessionManager.getSessionFile();
	if (rootFile && ref.sessionFile && !ref.sessionFile.startsWith(`${rootFile.replace(/\.jsonl$/, "")}/`)) return false;
	const bound = ref.session ? runtime(registry).bindings.get(ref.session) : undefined;
	return !bound || bound.rootSessionId === root.session.sessionManager.getSessionId();
}

function owned(registry: Registry, owner: AgentRef, ref: AgentRef): boolean {
	if (owner === ref || ref.kind !== "sub" || !belongsToCurrentRoot(registry, ref)) return false;
	try { return lineage(registry, ref).includes(owner); } catch { return false; }
}

function caller(registry: Registry, ctx: ExtensionContext): AgentRef {
	const sessionId = ctx.sessionManager.getSessionId();
	const matches = registry.list().filter(ref => ref.session?.sessionManager.getSessionId() === sessionId);
	if (matches.length !== 1) throw new Error("Executive policy: calling native registry identity is missing or ambiguous.");
	return matches[0];
}

function isClosing(state: Runtime, ref: AgentRef): boolean {
	for (const cancel of state.cancellations) {
		if (!cancel.settled && (cancel.target === ref || cancel.refs.has(ref) ||
			(!cancel.target && cancel.owner === ref && cancel.ownerSessionId === ref.session?.sessionManager.getSessionId()))) return true;
	}
	return false;
}

function assertLive(registry: Registry, state: Runtime, ref: AgentRef, allowOwnerRecovery = false): void {
	if (registry.get(ref.id) !== ref || !ref.session || ref.session.isDisposed || ref.status === "aborted") {
		throw new Error("Executive policy: this native agent generation is no longer live.");
	}
	if (!belongsToCurrentRoot(registry, ref)) {
		throw new Error("Executive policy: this descendant belongs to a different Main session; resume its owner first.");
	}
	const recovering = allowOwnerRecovery && [...state.cancellations].some(cancel => cancel.owner === ref &&
		cancel.ownerSessionId === ref.session!.sessionManager.getSessionId() && !cancel.target && !cancel.settled);
	if (lineage(registry, ref).some(parent => isClosing(state, parent) && !(recovering && parent === ref))) {
		throw new Error("Executive policy: this owned scope is closing; new activity is rejected.");
	}
}

function prunePermits(registry: Registry, state: Runtime): void {
	for (const session of state.admission.executives) {
		if (session.isDisposed || registry.get(session.getAgentId() ?? "")?.session !== session) state.admission.leave(session);
	}
	for (const session of state.admission.workers) {
		if (!session.isStreaming || session.isDisposed || registry.get(session.getAgentId() ?? "")?.session !== session) {
			state.admission.endTurn(session);
		}
	}
}

function brief(ctx: ExtensionContext): string | null {
	const entries = ctx.sessionManager.getBranch();
	for (let i = entries.length - 1; i >= 0; i--) {
		const entry = entries[i];
		if (entry.type === "custom" && entry.customType === PLAN_ENTRY && typeof entry.data === "string") return entry.data;
	}
	return null;
}

function result(details: Record<string, unknown>, isError = false) {
	return { content: [{ type: "text" as const, text: JSON.stringify(details, null, 2) }], details, ...(isError ? { isError: true } : {}) };
}

function status(registry: Registry, state: Runtime, ref: AgentRef, ctx: ExtensionContext): Record<string, unknown> {
	prunePermits(registry, state);
	const descendants = registry.list().filter(child => owned(registry, ref, child));
	const ids = new Set([ref.id, ...descendants.map(child => child.id)]);
	const binding = ref.session ? state.bindings.get(ref.session) : undefined;
	const ready = binding?.ready === true && binding.ref === ref && !ref.session!.isDisposed &&
		registry.get(ref.id) === ref && belongsToCurrentRoot(registry, ref);
	return {
		role: roleOf(ref), agent: ref.id, policy: ENABLED ? (ready ? "enforced" : "not-ready") : "operator-opt-out",
		ready, failure: binding?.failure ?? null,
		limits: LIMITS,
		usage: { activeWorkerTurns: state.admission.workers.size, liveExecutives: state.admission.executives.size },
		plan: brief(ctx),
		ownedDescendants: descendants.map(child => {
			let role: Role | "unknown" = "unknown";
			try { role = roleOf(child); } catch { /* Historical rows can lack session_init. Do not invent a role. */ }
			return { agent: child.id, parent: child.parentId, role, status: child.status, running: registry.isRunning(child), closing: isClosing(state, child) };
		}),
		remaining: {
			jobs: (ref.session?.asyncJobManager?.getRunningJobs() ?? []).filter(job => job.ownerId && ids.has(job.ownerId)).map(job => ({ id: job.id, agent: job.agentId, owner: job.ownerId, queued: job.queued === true })),
			cancellations: [...state.cancellations].filter(cancel => cancel.owner === ref &&
				cancel.ownerSessionId === ctx.sessionManager.getSessionId()).map(cancel => ({ agent: cancel.target?.id ?? null, settled: cancel.settled, error: cancel.error ?? null })),
		},
		// Registry state proves activity, NOT successful acceptance. Dormant peers
		// remain explicitly visible instead of being silently counted complete.
		scopeState: isClosing(state, ref) ? "closing" : "open",
	};
}

function assertPeerTarget(registry: Registry, ref: AgentRef, input: Record<string, unknown>): void {
	if (input.op !== "send") return;
	const to = (input.to as string).trim();
	const peers = to === "all" ? registry.listVisibleTo(ref.id) : [registry.get(to)];
	if (peers.some(peer => !peer || !belongsToCurrentRoot(registry, peer))) {
		throw new Error("Executive policy: peer sends may only wake agents in the current protected native tree.");
	}
}

async function awaitWithin(completion: Promise<void>, timeoutMs: number): Promise<boolean> {
	let timer: ReturnType<typeof setTimeout> | undefined;
	try {
		return await Promise.race([
			completion.then(() => true),
			new Promise<false>(resolve => { timer = setTimeout(() => resolve(false), timeoutMs); }),
		]);
	} finally {
		if (timer) clearTimeout(timer);
	}
}

async function cancelScope(registry: Registry, state: Runtime, owner: AgentRef, target?: AgentRef): Promise<Cancellation> {
	const ownerSessionId = owner.session!.sessionManager.getSessionId();
	const duplicate = [...state.cancellations].find(cancel => !cancel.settled && cancel.owner === owner &&
		cancel.ownerSessionId === ownerSessionId && cancel.target === target);
	if (duplicate && duplicate.error === undefined) return duplicate;
	const manager = owner.session?.asyncJobManager;
	if (!manager) throw new Error("Executive policy: native async job manager is unavailable; cancellation cannot be confirmed.");
	const lifecycle = AgentLifecycleManager.global();
	if (!lifecycle.manages(registry)) throw new Error("Executive policy: native lifecycle registry does not match.");
	const cancel: Cancellation = duplicate ?? {
		owner, ownerSessionId, target, refs: new Set(), sessions: new Map(), jobs: new Set(), settled: false, completion: Promise.resolve(),
	};
	state.cancellations.add(cancel);
	cancel.error = undefined;
	cancel.completion = (async () => {
		try {
			// Retry retained refs/sessions too: release can detach before native
			// persistence or disposal fails. Never discard that cleanup evidence.
			const released = new Set<AgentRef>();
			const reaped = new Set<Job>();
			for (;;) {
				if (owner.session?.sessionManager.getSessionId() !== ownerSessionId) {
					throw new Error("Cancellation owner switched sessions; resume its original session before retrying cleanup.");
				}
				const refs = new Set([
					...cancel.refs,
					...registry.list().filter(ref => ref === target || (target ? owned(registry, target, ref) : owned(registry, owner, ref))),
				]);
				const ids = new Set([...refs].map(ref => ref.id));
				if (!target) ids.add(owner.id);
				const fresh = [...refs].filter(ref => !released.has(ref));
				for (const ref of fresh) {
					cancel.refs.add(ref);
					released.add(ref);
					if (ref.session) {
						cancel.sessions.set(ref, ref.session);
						ref.session.beginDispose();
					}
				}
				for (const job of manager.getAllJobs()) {
					if ((job.ownerId && ids.has(job.ownerId)) || (job.agentId && ids.has(job.agentId))) cancel.jobs.add(job);
				}
				const newJobs = [...cancel.jobs].filter(job => !reaped.has(job));
				for (const job of newJobs) {
					reaped.add(job);
					if (manager.getJob(job.id) === job) manager.cancel(job.id, { ownerId: job.ownerId });
				}
				const calls = [...refs].flatMap(ref => [...(state.taskCalls.get(ref) ?? [])]);
				if (!target) calls.push(...(state.taskCalls.get(owner) ?? []));
				if (!fresh.length && !newJobs.length && !calls.length) break;
				const releases = fresh.map(async ref => {
					const session = cancel.sessions.get(ref);
					try {
						await lifecycle.release(ref.id, ref, { tombstone: true });
					} finally {
						// Native release logs disposal failures. Await its idempotent
						// disposal promise ourselves so failure cannot attest settlement.
						if (session) {
							try { await session.dispose(); } finally { await session.waitForIdle(); }
						}
					}
				});
				// An aborted task call may reject normally. Every started operation
				// must settle before a cleanup failure becomes safely retryable.
				const outcomes = await Promise.allSettled([...releases, ...newJobs.map(job => job.promise), Promise.allSettled(calls)]);
				const failed = outcomes.find(outcome => outcome.status === "rejected");
				if (failed?.status === "rejected") throw failed.reason;
				// Re-snapshot: a task already past tool_call may have attached a
				// child during cleanup. Its admission sees the same closing barrier.
			}
			for (const ref of cancel.refs) {
				if (ref.session || cancel.sessions.get(ref)?.isStreaming || (registry.get(ref.id) === ref && ref.status !== "aborted")) {
					throw new Error(`Native cancellation did not leave ${ref.id} terminal and detached.`);
				}
			}
			// This single transition releases this cancellation's barriers only
			// after every check. Overlapping unsettled records keep theirs closed.
			cancel.settled = true;
			cancel.sessions.clear();
		} catch (error) {
			// Keep admission closed, but leave status and same-scope retry usable.
			cancel.error = error instanceof Error ? error.message : String(error);
		}
	})();
	return cancel;
}

export default function executiveExtension(pi: ExtensionAPI): void {
	const registry = pi.pi.AgentRegistry.global();
	const state = runtime(registry);
	let binding: Binding | undefined;
	let wrappedSession: AgentSession | undefined;

	function resolve(ctx: ExtensionContext, allowOwnerRecovery = false): AgentRef {
		const ref = caller(registry, ctx);
		if (ENABLED) {
			assertLive(registry, state, ref, allowOwnerRecovery);
			const active = state.bindings.get(ref.session!);
			if (!active?.ready) throw new Error(active?.failure ?? "Executive policy has not finished native initialization.");
		}
		return ref;
	}

	function registerWrapper(name: "hub" | "task" | "read" | "grep" | "glob", session: AgentSession) {
		const native = session.getToolByName(name);
		if (!native) return; // Respect native depth/tool grants; never add absent task.
		if (!session.extensionRunner?.hasNativeTool(name)) throw new Error(`Executive policy: native ${name} delegation is unavailable.`);
		const definition: ToolDefinition & Pick<NativeTool, "concurrency" | "interruptible"> = {
			name, label: native.label, description: native.description, parameters: native.parameters,
			strict: native.strict, loadMode: native.loadMode, approval: native.approval,
			concurrency: native.concurrency, interruptible: native.interruptible,
			async execute(_callId, params, signal, onUpdate, ctx) {
				const ref = resolve(ctx);
				if (ENABLED) {
					assertExecutiveTool(roleOf(ref), name, params);
					if (roleOf(ref) !== "worker" && name === "hub") assertPeerTarget(registry, ref, params);
				}
				if (!ctx.invokeTool) throw new Error(`Executive policy: native ${name} invocation is unavailable.`);
				const call = ctx.invokeTool(params, { signal, onUpdate });
				if (name !== "task" || !ENABLED) return call;
				let pending = state.taskCalls.get(ref);
				if (!pending) state.taskCalls.set(ref, pending = new Set());
				pending.add(call);
				try { return await call; } finally {
					pending.delete(call);
					if (!pending.size) state.taskCalls.delete(ref);
				}
			},
		};
		pi.registerTool(definition);
		return { name, native, definition };
	}

	async function selectTools(ctx: ExtensionContext, force = false): Promise<void> {
		const ref = caller(registry, ctx);
		const active = pi.getActiveTools();
		const role = roleOf(ref);
		const selected = ENABLED && role !== "worker"
			? [...active.filter(name => EXECUTIVE_TOOLS.has(name)), "executive_control"]
			: active.filter(name => name !== "executive_control");
		if (role !== "worker" && !selected.includes("executive_control")) selected.push("executive_control");
		const unique = [...new Set(selected)];
		if (force || unique.length !== active.length || unique.some(name => !active.includes(name))) await pi.setActiveTools(unique);
	}

	async function initialize(ctx: ExtensionContext): Promise<void> {
		const ref = caller(registry, ctx);
		const session = ref.session!;
		const prior = state.bindings.get(session);
		if (prior) prior.ready = false;
		prior?.disposeHooks();
		const root = rootOf(registry, ref);
		binding = { ref, session, rootSessionId: root.session!.sessionManager.getSessionId(), ready: false, disposeHooks: () => {} };
		state.bindings.set(session, binding);
		const current = binding;
		const disposers: Array<() => void> = [];
		current.disposeHooks = () => { for (const dispose of disposers.splice(0)) dispose(); };
		try {
			if (ENABLED) {
				// This is NOT an extension event callback. Native Agent awaits this
				// hook and turns a thrown refusal into a terminal error without a
				// provider call. Ordinary event-handler exceptions are swallowed.
				if (typeof session.agent.addBeforeModelCallHook !== "function") {
					throw new Error("Native Agent.addBeforeModelCallHook is required for safe recursive admission.");
				}
				disposers.push(session.agent.addBeforeModelCallHook(() => {
					if (ref.session !== session || state.bindings.get(session) !== current || !current.ready) {
						throw new Error(current.failure ?? "Executive policy initialization incomplete or superseded.");
					}
					assertLive(registry, state, ref, true);
					prunePermits(registry, state);
					state.admission.enter(roleOf(ref), session);
				}));
				disposers.push(session.subscribeRunState(runState => {
					if (runState === "idle") state.admission.endTurn(session);
				}));
				// Native task starts are emitted after session attachment but before
				// the first prompt. Ordinary children replace this temporary gate in
				// session_start; plan-mode workers load no extensions, so retain it.
				disposers.push(pi.events.on(TASK_SUBAGENT_LIFECYCLE_CHANNEL, data => {
					const event = data as Partial<SubagentLifecyclePayload> | null;
					if (!event || event.status !== "started" || typeof event.id !== "string") return;
					const child = registry.get(event.id);
					if (!child?.session || !owned(registry, ref, child) || state.bindings.has(child.session)) return;
					const childSession = child.session;
					const inherited: Binding = {
						ref: child, session: childSession, rootSessionId: current.rootSessionId,
						ready: false, disposeHooks: () => {},
					};
					const childDisposers: Array<() => void> = [];
					inherited.disposeHooks = () => { for (const dispose of childDisposers.splice(0)) dispose(); };
					state.bindings.set(childSession, inherited);
					try {
						childDisposers.push(childSession.agent.addBeforeModelCallHook(() => {
							if (child.session !== childSession || state.bindings.get(childSession) !== inherited) {
								throw new Error("Executive policy: inherited worker generation was superseded.");
							}
							assertLive(registry, state, child);
							// session_init exists by model dispatch, not at the start
							// notification. Never derive a role from displayName.
							if (roleOf(child) !== "worker") throw new Error("Executive policy: child scope must initialize its own executive extension.");
							prunePermits(registry, state);
							state.admission.enter("worker", childSession);
						}));
						childDisposers.push(childSession.subscribeRunState(runState => {
							if (runState === "idle") state.admission.endTurn(childSession);
						}));
					} catch (error) {
						inherited.failure = error instanceof Error ? error.message : String(error);
						childSession.beginDispose();
						throw error;
					}
				}));
				assertLive(registry, state, ref, true);
				if (roleOf(ref) === "executive") state.admission.enter("executive", session);
			}
			if (ENABLED && wrappedSession !== session) {
				const wrappers = (["hub", "task", "read", "grep", "glob"] as const).map(name => registerWrapper(name, session));
				// OMP 18.1.16 supports session_start registration. setActiveTools
				// awaits its native registration barrier even if selection is equal.
				await selectTools(ctx, true);
				for (const wrapper of wrappers) {
					if (wrapper && (session.getToolByName(wrapper.name) === wrapper.native ||
						session.extensionRunner?.getRegisteredTool(wrapper.name)?.definition !== wrapper.definition)) {
						throw new Error(`Executive policy: native ${wrapper.name} wrapper activation failed.`);
					}
				}
				wrappedSession = session;
			} else {
				await selectTools(ctx);
			}
			current.ready = true;
		} catch (error) {
			current.failure = error instanceof Error ? error.message : String(error);
			current.ready = false;
			// A loaded policy without its hard runtime seam must not silently
			// continue. beginDispose synchronously closes deferred admission.
			session.beginDispose();
			if (ref.kind === "sub") {
				await AgentLifecycleManager.global().release(ref.id, ref, { tombstone: true });
			} else {
				ctx.ui.notify(current.failure, "error");
				ctx.shutdown();
			}
			throw error;
		}
	}

	pi.on("session_start", (_event, ctx) => initialize(ctx));
	pi.on("session_switch", async (_event, ctx) => {
		// Root identity is the attached live session, not its old JSONL path.
		// Child bindings from the old root remain old and cannot be revived into
		// the new scope merely because their parent string is still "Main".
		if (binding) state.admission.leave(binding.session);
		await initialize(ctx);
	});
	pi.on("session_branch", (_event, ctx) => initialize(ctx));
	pi.on("session_tree", (_event, ctx) => selectTools(ctx));
	pi.on("session_shutdown", () => {
		if (!binding) return;
		binding.ready = false;
		binding.disposeHooks();
		state.admission.leave(binding.session);
		if (state.bindings.get(binding.session) === binding) state.bindings.delete(binding.session);
	});
	pi.on("before_agent_start", async (event, ctx) => {
		if (!ENABLED) return;
		const ref = resolve(ctx, true);
		await selectTools(ctx);
		if (roleOf(ref) !== "worker") return { systemPrompt: executivePrompt(event.systemPrompt) };
	});
	pi.on("tool_call", (event, ctx) => {
		if (!ENABLED) return;
		try {
			const isControl = event.toolName === "executive_control";
			const ref = isControl && event.input.op === "status" ? caller(registry, ctx) :
				resolve(ctx, isControl && event.input.op === "cancel");
			assertExecutiveTool(roleOf(ref), event.toolName, event.input);
		} catch (error) {
			return { block: true, reason: error instanceof Error ? error.message : String(error) };
		}
	});

	const z = pi.zod;
	pi.registerTool({
		name: "executive_control", label: "Executive Scope", loadMode: "essential", defaultInactive: true, approval: "read",
		description: "Inspect this native scope, persist its brief, or cancel only owned descendant scopes. op: status | plan | cancel; plan updates this node only; cancel optionally selects one owned descendant agent, otherwise all descendants. Cancellation reports settled only after native jobs and sessions settle. This cannot change policy, execute code, or manage arbitrary processes.",
		parameters: z.object({ op: z.enum(["status", "plan", "cancel"]), plan: z.string().max(MAX_PLAN_CHARS).optional(), agent: z.string().optional() }),
		async execute(_callId, params, signal, _onUpdate, ctx) {
			const ref = caller(registry, ctx);
			if (roleOf(ref) === "worker") throw new Error("Executive control is available only to Main and executive scopes.");
			if (params.op === "status") return result(status(registry, state, ref, ctx));
			resolve(ctx, params.op === "cancel");
			signal?.throwIfAborted();
			if (params.op === "plan") {
				if (params.agent !== undefined || typeof params.plan !== "string") throw new Error("Plan requires plan and cannot target another agent.");
				pi.appendEntry(PLAN_ENTRY, params.plan);
				// Custom entries alone do not cross native lazy session persistence.
				const manager = ref.session!.sessionManager;
				await manager.ensureOnDisk();
				await manager.flush();
				return result(status(registry, state, ref, ctx));
			}
			if (params.plan !== undefined) throw new Error("Cancel does not accept a plan.");
			if (isClosing(state, ref) && params.agent !== undefined) throw new Error("This scope is closing; retry its all-descendants cancellation without agent.");
			// Load the native persisted roster before deciding ownership, so a
			// parked grandchild after restart cannot be omitted from cancellation.
			const root = rootOf(registry, ref);
			const rootSessionId = root.session!.sessionManager.getSessionId();
			await registerPersistedSubagents(registry, root.session!.sessionManager.getSessionFile(), { hydrateHistory: false });
			if (root.session?.sessionManager.getSessionId() !== rootSessionId) throw new Error("Main switched sessions during cancellation preflight.");
			resolve(ctx, true);
			const previous = params.agent === undefined ? undefined : [...state.cancellations].find(cancel =>
				!cancel.settled && cancel.owner === ref && cancel.ownerSessionId === ctx.sessionManager.getSessionId() && cancel.target?.id === params.agent);
			const liveTarget = params.agent === undefined ? undefined : registry.get(params.agent);
			const target = previous?.target ?? liveTarget;
			if (previous && liveTarget && liveTarget !== target) throw new Error("Cancellation target generation changed; the previous cleanup cannot target its replacement.");
			if (params.agent !== undefined && (!target || (!previous && !owned(registry, ref, target)))) throw new Error("Cancellation target must be an owned descendant of this native scope.");
			const cancellation = await cancelScope(registry, state, ref, target);
			await awaitWithin(cancellation.completion, CANCEL_TIMEOUT_MS);
			return result({
				op: "cancel", agent: params.agent ?? null, settled: cancellation.settled,
				cancelled: [...cancellation.refs].map(child => child.id), jobs: [...cancellation.jobs].map(job => job.id),
				error: cancellation.error ?? null,
				...(!cancellation.settled ? { remaining: "Native cleanup is not confirmed; admission remains closed. Inspect status; retry the same cancel scope if cleanup failed." } : {}),
			}, !cancellation.settled);
		},
	});
}
