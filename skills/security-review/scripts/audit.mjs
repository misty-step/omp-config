#!/usr/bin/env node
import { execSync } from "node:child_process";
import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { tmpdir } from "node:os";

// Frontier Reasoning Models on OpenRouter
const MODELS = {
  glm: {
    id: "z-ai/glm-5.3",
    name: "GLM 5.3"
  },
  kimi: {
    id: "moonshotai/kimi-k3",
    name: "Kimi K3"
  },
  deepseek: {
    id: "deepseek/deepseek-v4-pro-0813",
    name: "DeepSeek V4 Pro 0813"
  }
};

function getOpenRouterToken() {
  if (process.env.OPENROUTER_API_KEY && process.env.OPENROUTER_API_KEY.trim().length > 0) {
    return process.env.OPENROUTER_API_KEY.trim();
  }
  try {
    const token = execSync("omp token openrouter", { stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
    if (token) return token;
  } catch {}
  throw new Error("Unable to retrieve OpenRouter API key. Set OPENROUTER_API_KEY or configure OpenRouter in OMP.");
}

function collectTargetContent(args) {
  if (args.diff) return args.diff;
  if (args.staged) {
    return execSync("git diff --cached", { encoding: "utf-8" });
  }
  if (args.commit) {
    return execSync(`git show ${args.commit}`, { encoding: "utf-8" });
  }
  if (args.files && args.files.length > 0) {
    let combined = "";
    for (const f of args.files) {
      try {
        if (existsSync(f)) {
          const raw = readFileSync(f, "utf-8");
          combined += `\n--- File: ${f} ---\n` + raw;
        } else {
          const diffContent = execSync(`git diff HEAD -- "${f}"`, { encoding: "utf-8" });
          if (diffContent.trim()) {
            combined += `\n--- Diff for ${f} ---\n` + diffContent;
          }
        }
      } catch (err) {
        console.error(`Warning: Could not read target '${f}':`, err.message);
      }
    }
    return combined;
  }

  // Default fallback: unstaged working tree diff, or last commit if clean
  let diff = "";
  try {
    diff = execSync("git diff HEAD", { encoding: "utf-8" });
    if (!diff.trim()) {
      diff = execSync("git diff HEAD~1 HEAD", { encoding: "utf-8" });
    }
  } catch {}
  return diff;
}

const SYSTEM_PROMPT = `You are a Principal Security Engineer and elite adversarial vulnerability researcher.

Perform a deep, exhaustive, and rigorous security audit across the entire provided codebase / diff.
Investigate the full spectrum of vulnerabilities with extreme depth:
1. Sinks & Injections: OS command injection, SQLi, NoSQLi, Template Injection (SSTI), ReDoS, prototype pollution, dangerous deserialization, memory/arithmetic corruption.
2. Taint Flow & Boundary Violations: Untrusted data propagation across interfaces, lack of input sanitization/validation, escaping errors.
3. Access Control & Authentication: IDOR, privilege escalation (horizontal & vertical), broken authentication, token handling, session fixation, timing attacks.
4. Business Logic & State Machines: Step-skipping, balance/quantity manipulation, race conditions (TOCTOU), invalid state transitions.
5. Threat Modeling & Architecture: Trust boundary breaches, hardcoded credentials/secrets, cryptographic misuse, Denial of Service (DoS) amplification, blast radius.

For every issue found:
- Trace the complete source-to-sink exploit path step-by-step.
- Detail the exact blast radius and security impact.
- Provide a concrete, robust, production-grade remediation.

Report ONLY real, provable vulnerabilities with credible execution paths. Ignore cosmetic issues, styling, or unverified speculative theories.

Output your audit strictly as a valid JSON object matching this schema:
{
  "verdict": "clean" | "vulnerable",
  "summary": "<2-3 sentence executive assessment of security posture>",
  "findings": [
    {
      "id": "SEC-01",
      "title": "<Concise imperative vulnerability title, <= 80 chars>",
      "severity": "critical" | "high" | "medium" | "low",
      "confidence": "high" | "medium" | "low",
      "cwe": "CWE-XXX",
      "file_path": "<relative/file/path>",
      "line_start": <number>,
      "line_end": <number>,
      "attack_path": "<Step-by-step exploit mechanism: source -> propagation -> sink>",
      "impact": "<Concrete blast radius and security consequence>",
      "remediation": "<Concrete code-level fix or defense-in-depth mitigation>"
    }
  ]
}

If no vulnerabilities exist, return "verdict": "clean" and "findings": [].
Output JSON only.`;

async function queryModel(token, modelKey, modelConfig, targetContent, timeoutMs = 120000) {
  const t0 = Date.now();
  const userPrompt = `Target Scope for Deep Security Audit:\n\n\`\`\`\n${targetContent.slice(0, 120000)}\n\`\`\``;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mistystep.io",
        "X-Title": "Misty Step OMP Security Reviewer"
      },
      body: JSON.stringify({
        model: modelConfig.id,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: userPrompt }
        ],
        max_tokens: 6000,
        temperature: 0.1
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errText = await response.text();
      return {
        key: modelKey,
        name: modelConfig.name,
        success: false,
        error: `HTTP ${response.status}: ${errText}`,
        elapsedMs: Date.now() - t0
      };
    }

    const data = await response.json();
    const message = data.choices?.[0]?.message;
    const rawContent = message?.content || "";
    const reasoning = message?.reasoning || "";

    let parsed = null;
    try {
      const jsonMatch = rawContent.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        parsed = JSON.parse(jsonMatch[0]);
      }
    } catch (e) {
      parsed = { parseError: e.message, raw: rawContent };
    }

    return {
      key: modelKey,
      name: modelConfig.name,
      success: true,
      data: parsed,
      rawContent,
      reasoningLength: reasoning.length,
      usage: data.usage,
      elapsedMs: Date.now() - t0
    };
  } catch (err) {
    clearTimeout(timeoutId);
    return {
      key: modelKey,
      name: modelConfig.name,
      success: false,
      error: err.name === "AbortError" ? `Timeout after ${timeoutMs / 1000}s` : err.message,
      elapsedMs: Date.now() - t0
    };
  }
}

function synthesizeFindings(results) {
  const allFindings = [];
  const modelSummaries = {};

  for (const res of results) {
    if (!res.success || !res.data || !res.data.findings) {
      modelSummaries[res.key] = {
        name: res.name,
        verdict: res.success ? (res.data?.verdict || "clean") : "error",
        summary: res.success ? (res.data?.summary || "No findings reported.") : (res.error || "Query failed"),
        count: 0
      };
      continue;
    }

    modelSummaries[res.key] = {
      name: res.name,
      verdict: res.data.verdict || (res.data.findings.length > 0 ? "vulnerable" : "clean"),
      summary: res.data.summary || "",
      count: res.data.findings.length
    };

    for (const f of res.data.findings) {
      allFindings.push({
        ...f,
        modelKey: res.key,
        modelName: res.name
      });
    }
  }

  const consolidated = [];
  const visited = new Set();

  for (let i = 0; i < allFindings.length; i++) {
    if (visited.has(i)) continue;
    const base = allFindings[i];
    visited.add(i);

    const group = [base];
    for (let j = i + 1; j < allFindings.length; j++) {
      if (visited.has(j)) continue;
      const cand = allFindings[j];

      const sameFile = base.file_path && cand.file_path && (
        base.file_path === cand.file_path ||
        base.file_path.endsWith(cand.file_path) ||
        cand.file_path.endsWith(base.file_path)
      );

      const lineOverlap = sameFile && Math.abs((base.line_start || 0) - (cand.line_start || 0)) <= 8;
      const sameCwe = base.cwe && cand.cwe && base.cwe.toUpperCase().trim() === cand.cwe.toUpperCase().trim();

      const baseWords = (base.title || "").toLowerCase().split(/\W+/).filter(w => w.length > 3);
      const candWords = (cand.title || "").toLowerCase().split(/\W+/).filter(w => w.length > 3);
      const sharedKeywords = baseWords.filter(w => candWords.includes(w)).length >= 2;

      // Group if matching vulnerability across models
      const shouldGroup = (sameFile && sameCwe) ||
        (sameFile && lineOverlap && sharedKeywords) ||
        (sameCwe && sharedKeywords);

      if (shouldGroup) {
        group.push(cand);
        visited.add(j);
      }
    }

    const reportingModels = Array.from(new Set(group.map(g => g.modelName)));
    const consensus = reportingModels.length >= 3 ? "Tri-Model Consensus (3/3)"
      : reportingModels.length === 2 ? "Dual-Model Consensus (2/3)"
      : "Solo Model Finding (1/3)";

    const rankMap = { critical: 4, high: 3, medium: 2, low: 1 };
    let topSeverity = "low";
    let topRank = 0;
    for (const g of group) {
      const r = rankMap[g.severity?.toLowerCase()] || 1;
      if (r > topRank) {
        topRank = r;
        topSeverity = g.severity?.toLowerCase() || "low";
      }
    }

    consolidated.push({
      id: `SEC-${String(consolidated.length + 1).padStart(2, "0")}`,
      title: base.title,
      severity: topSeverity,
      confidence: reportingModels.length > 1 ? "high" : (base.confidence || "medium"),
      consensus,
      models: reportingModels,
      cwe: base.cwe,
      file_path: base.file_path,
      line_start: base.line_start,
      line_end: base.line_end,
      attack_path: group.map(g => `**[${g.modelName}]**: ${g.attack_path}`).join("\n\n"),
      impact: base.impact || group.find(g => g.impact)?.impact || "Security integrity compromise.",
      remediation: group.map(g => `**[${g.modelName}]**: ${g.remediation}`).join("\n\n")
    });
  }

  return { consolidated, modelSummaries };
}

function generateMarkdownReport(targetLabel, results, synthesis) {
  const date = new Date().toISOString().split("T")[0];
  const { consolidated, modelSummaries } = synthesis;

  let md = `# Security Audit Report: Tri-Model Council
- **Target**: ${targetLabel}
- **Date**: ${date}
- **Models**: GLM 5.3 (\`z-ai/glm-5.3\`), Kimi K3 (\`moonshotai/kimi-k3\`), DeepSeek V4 Pro 0813 (\`deepseek/deepseek-v4-pro-0813\`)
- **Total Unique Vulnerabilities**: ${consolidated.length}

---

## 1. Council Summaries

| Model | Verdict | Findings Identified | Latency |
|---|---|---|---|
`;

  for (const res of results) {
    const sum = modelSummaries[res.key];
    md += `| **${res.name}** | \`${sum?.verdict || "unknown"}\` | ${sum?.count || 0} | ${(res.elapsedMs / 1000).toFixed(1)}s |\n`;
  }

  md += `\n### Model Assessments\n`;
  for (const res of results) {
    const sum = modelSummaries[res.key];
    md += `- **${res.name}**: ${sum?.summary || "No summary provided."}\n`;
  }

  md += `\n---\n\n## 2. Synthesized Vulnerabilities\n\n`;

  if (consolidated.length === 0) {
    md += `No actionable security vulnerabilities identified across all three models.\n`;
  } else {
    for (const v of consolidated) {
      md += `### ${v.id}: ${v.title}
- **Severity**: \`${v.severity.toUpperCase()}\` | **Confidence**: \`${v.confidence.toUpperCase()}\` | **Consensus**: **${v.consensus}** (${v.models.join(", ")})
- **Location**: \`${v.file_path || "unknown"}:${v.line_start || 0}-${v.line_end || 0}\`
- **CWE**: \`${v.cwe || "N/A"}\`

#### Attack Mechanism & Exploit Path
${v.attack_path}

#### Impact
${v.impact}

#### Remediation
${v.remediation}

---
`;
    }
  }

  md += `\n## 3. Operator Triage Gate

Before applying repairs:
1. Verify each exploit mechanism against the real runtime interface.
2. Filter ungrounded solo findings without concrete source-to-sink proof.
3. Use \`skill://hunk\` walkthrough to review line annotations with the operator.
`;

  return md;
}

function generateHunkWalkthrough(consolidated) {
  const comments = [];
  for (let i = 0; i < consolidated.length; i++) {
    const v = consolidated[i];
    if (!v.file_path) continue;
    comments.push({
      filePath: v.file_path,
      newLine: v.line_start || 1,
      summary: `[${i + 1}/${consolidated.length}] [${v.severity.toUpperCase()}] ${v.title}`,
      rationale: `**${v.consensus}** (${v.models.join(", ")})\n\n**CWE**: ${v.cwe || "N/A"}\n\n**Attack Path:**\n${v.attack_path}\n\n**Remediation:**\n${v.remediation}`
    });
  }
  return {
    comments,
    meta: {
      generatedBy: "security-reviewer",
      timestamp: new Date().toISOString(),
      count: comments.length
    }
  };
}

async function main() {
  const rawArgs = process.argv.slice(2);
  const args = {
    staged: rawArgs.includes("--staged"),
    diff: null,
    commit: null,
    files: [],
    jsonOutput: rawArgs.includes("--json")
  };

  for (let i = 0; i < rawArgs.length; i++) {
    if (rawArgs[i] === "--commit" && rawArgs[i + 1]) {
      args.commit = rawArgs[++i];
    } else if (rawArgs[i] === "--file" && rawArgs[i + 1]) {
      args.files.push(rawArgs[++i]);
    } else if (rawArgs[i] === "--diff" && rawArgs[i + 1]) {
      args.diff = rawArgs[++i];
    }
  }

  const token = getOpenRouterToken();
  const targetContent = collectTargetContent(args);

  if (!targetContent || !targetContent.trim()) {
    console.error("Error: No target code or diff found to review.");
    process.exit(1);
  }

  const targetLabel = args.commit ? `Commit ${args.commit}`
    : args.staged ? "Staged changes"
    : args.files.length > 0 ? `Files: ${args.files.join(", ")}`
    : "Working tree diff";

  if (!args.jsonOutput) {
    console.log(`[security-reviewer] Initiating Full-Spectrum Security Audit for: ${targetLabel}`);
    console.log(`[security-reviewer] Payload size: ${targetContent.length} bytes`);
    console.log(`[security-reviewer] Launching concurrent audits (GLM 5.3, Kimi K3, DeepSeek V4 Pro 0813 via OpenRouter)...\n`);
  }

  const promises = [
    queryModel(token, "glm", MODELS.glm, targetContent),
    queryModel(token, "kimi", MODELS.kimi, targetContent),
    queryModel(token, "deepseek", MODELS.deepseek, targetContent)
  ];

  const results = await Promise.all(promises);

  if (!args.jsonOutput) {
    for (const res of results) {
      if (res.success) {
        console.log(`✓ [${res.name}] Completed in ${(res.elapsedMs / 1000).toFixed(1)}s (Reasoning: ${res.reasoningLength} chars, Findings: ${res.data?.findings?.length || 0})`);
      } else {
        console.error(`✗ [${res.name}] Failed in ${(res.elapsedMs / 1000).toFixed(1)}s: ${res.error}`);
      }
    }
    console.log(`\n[security-reviewer] Synthesizing cross-model findings...`);
  }

  const synthesis = synthesizeFindings(results);
  const reportId = Date.now().toString(36);
  const mdReport = generateMarkdownReport(targetLabel, results, synthesis);
  const hunkSidecar = generateHunkWalkthrough(synthesis.consolidated);

  const reportPath = resolve(tmpdir(), `security-review-${reportId}.md`);
  const sidecarPath = resolve(tmpdir(), `security-walkthrough-${reportId}.json`);
  const jsonPath = resolve(tmpdir(), `security-findings-${reportId}.json`);

  writeFileSync(reportPath, mdReport, "utf-8");
  writeFileSync(sidecarPath, JSON.stringify(hunkSidecar, null, 2), "utf-8");
  writeFileSync(jsonPath, JSON.stringify({ results, synthesis }, null, 2), "utf-8");

  if (args.jsonOutput) {
    console.log(JSON.stringify({
      reportId,
      reportPath,
      sidecarPath,
      jsonPath,
      results,
      synthesis
    }, null, 2));
  } else {
    console.log(`[security-reviewer] Synthesized ${synthesis.consolidated.length} unique finding(s).`);
    console.log(`\n======================================================`);
    console.log(`Security Review Artifacts:`);
    console.log(`- Markdown Report:   ${reportPath}`);
    console.log(`- Hunk Walkthrough:  ${sidecarPath}`);
    console.log(`- Raw JSON Data:     ${jsonPath}`);
    console.log(`======================================================\n`);
    console.log(mdReport);
  }
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
