import type { AgentSession } from "@oh-my-pi/pi-coding-agent";

export type Role = "main" | "executive" | "worker";

// These are concurrency limits, not dollar/request budgets. Main is not a
// worker and does not occupy an executive slot. Waiting executives retain a
// scope slot but NEVER acquire a worker-turn slot. No queue is added here.
export const LIMITS = Object.freeze({ activeWorkerTurns: 4, liveExecutives: 4 });
export const PLAN_ENTRY = "misty-step.omp-config.executive.plan";
export const MAX_PLAN_CHARS = 8_000;

export const EXECUTIVE_TOOLS: ReadonlySet<string> = new Set([
	"read", "grep", "glob", "ast_grep", "web_search", "task", "hub", "todo", "ask", "yield", "executive_control",
]);

const PEER_FIELDS: Readonly<Record<string, ReadonlySet<string>>> = {
	send: new Set(["op", "to", "message", "replyTo", "await", "timeoutMs"]),
	wait: new Set(["op", "from", "ids", "timeoutMs"]),
	inbox: new Set(["op", "peek"]),
	list: new Set(["op", "status", "limit"]),
	jobs: new Set(["op"]),
	cancel: new Set(["op", "ids"]),
};

/** Validate the object that will execute, not only the original tool_call event. */
export function assertPeerHub(input: Record<string, unknown>): void {
	const fields = typeof input.op === "string" ? PEER_FIELDS[input.op] : undefined;
	if (!fields) throw new Error("Executive policy: hub only permits peer messaging and owned-job coordination.");
	for (const key of Object.keys(input)) {
		// Intent is native harness metadata, never a process argument. Nulls are
		// emitted by some provider schemas; they carry no dispatch value.
		if (key !== "i" && input[key] != null && !fields.has(key)) {
			throw new Error(`Executive policy: hub argument ${key} is outside the peer-only contract.`);
		}
	}
	if (input.op === "send" && (typeof input.to !== "string" || !input.to.trim())) {
		throw new Error("Executive policy: hub send requires an explicit peer recipient.");
	}
}

const READ_SCHEMES = new Set([
	"http", "https", "artifact", "local", "skill", "rule", "agent", "history", "omp", "issue", "pr", "attachment",
]);

/** Native read/search bookkeeping is allowed; this is not a zero-I/O sandbox. */
export function assertReadTarget(input: Record<string, unknown>): void {
	if (input.path == null) return;
	if (typeof input.path !== "string") throw new Error("Executive policy: read/search path must be a string.");
	for (const target of input.path.split(";")) {
		let decoded: string;
		try {
			decoded = decodeURIComponent(target.trim());
		} catch {
			throw new Error("Executive policy: malformed encoded read/search path.");
		}
		const scheme = /^([a-z][a-z0-9+.-]*):\/\//i.exec(decoded)?.[1]?.toLowerCase();
		if (scheme && !READ_SCHEMES.has(scheme)) {
			throw new Error(`Executive policy: ${scheme} resources must be inspected by a worker.`);
		}
		// SQLite's native reader can create WAL bookkeeping and accepts raw SQL.
		// Delegate SQL, including encoded selectors, rather than treat it as pure.
		if (/\.(?:sqlite3?|db3?)(?=[:?#]|$)/i.test(decoded) && /[?&]q=/i.test(decoded)) {
			throw new Error("Executive policy: raw SQLite queries must be delegated to a worker.");
		}
	}
}

export function assertExecutiveTool(role: Role, name: string, input: Record<string, unknown>): void {
	if (role === "worker") return;
	if (!EXECUTIVE_TOOLS.has(name)) {
		throw new Error(`Executive policy: ${name} is not an executive capability; delegate implementation to a worker.`);
	}
	if (name === "hub") assertPeerHub(input);
	if (name === "read" || name === "grep" || name === "glob") assertReadTarget(input);
}

/** Only permit leases are held here; identities/status/results remain native. */
export class Admission {
	readonly workers = new Set<AgentSession>();
	readonly executives = new Set<AgentSession>();

	enter(role: Role, session: AgentSession): void {
		if (role === "main") return;
		const slots = role === "executive" ? this.executives : this.workers;
		const limit = role === "executive" ? LIMITS.liveExecutives : LIMITS.activeWorkerTurns;
		if (slots.has(session)) return;
		if (slots.size >= limit) {
			throw new Error(`Executive policy: ${role === "executive" ? "live executive scope" : "active worker turn"} limit reached (${limit}); retry only after an existing scope/turn settles.`);
		}
		slots.add(session);
	}

	endTurn(session: AgentSession): void {
		this.workers.delete(session);
	}

	leave(session: AgentSession): void {
		this.workers.delete(session);
		this.executives.delete(session);
	}
}

const POLICY_START = "<executive-scope-policy>";
const POLICY_END = "</executive-scope-policy>";
const ROLE_POLICY = `${POLICY_START}
This node is a delegating scope owner, whether native Main or a nested executive. This role policy explicitly supersedes conflicting default Role, Delegation, Workflow, and worker-agent directions requiring inline implementation, forbidding a single delegated slice, requiring two slices before delegation, or requiring you to perform verification/cleanup commands yourself. All generated safety, approval, user-intent, context, evidence, and nonconflicting engineering rules remain in force.
Own the user's outcome: clarify acceptance, inspect enough read-only evidence to decompose, delegate implementation and executable verification through native task, judge results, reassign failures, and integrate the accepted outcome. One bounded worker is correct for one implementation slice; use another executive only when it owns a genuinely independently decomposable outcome. Do not forward a task without making the scope/acceptance decision yourself. Read-only answers need not spawn workers.
Each assignment carries goal, constraints, ownership, acceptance criteria, evidence format, and stop/escalation conditions. Parallelize independent work; serialize only true dependencies/shared mutation. Native task/hub own execution, deliveries, isolated patch integration, parking and revival; do not build another scheduler or launch another omp/Herdr executor. Default depth is operator-configured, not a promise of unlimited recursion.
Your tools are native read/search, task, peer-only hub, ask, todo when native permits it, yield for native child completion, and executive_control. You cannot implement directly via writes, shell, eval, browser/computer, devices, process hub operations, or unknown tools. Delegate runnable changes and checks; do not hide implementation inside a bookkeeping brief. Workers keep their ordinary tool contracts.
The protected process-local tree admits at most 4 active worker turns and 4 live executive scopes excluding Main. Waiting executives use no worker permit. Excess activity, including revival, is rejected rather than queued or silently granted. These are concurrency limits, not a monetary budget. Close an unused executive with executive_control cancel before replacing it when the scope limit is full.
Use executive_control plan to persist only this node's concise remaining-scope brief. Status reads native descendants/jobs and reports truth, not acceptance; rely on enforcement only when ready is true and policy is enforced. Completion requires judging deliverable evidence, accounting for owned work and reporting failures/blockers. Cancel only an owned descendant subtree (or all owned descendants); await confirmed settlement. If cleanup fails, inspect status and retry the same cancellation scope; do not resume other activity while admission remains closed. A plain turn abort is NOT a whole-tree stop. Wait only when genuinely blocked; no continuation loop. Finish when acceptance is met; resume only for actual new input or native results.
${POLICY_END}`;

/** Preserve generated blocks; replace only this extension's own prior block on cold revival. */
export function executivePrompt(blocks: string[]): string[] {
	const prior = /<executive-scope-policy>[\s\S]*?<\/executive-scope-policy>/g;
	return [...blocks.map(block => block.replace(prior, "")).filter(block => block.length > 0), ROLE_POLICY];
}
