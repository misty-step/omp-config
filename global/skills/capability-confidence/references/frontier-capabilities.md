# Frontier capability receipts

Use these receipts when difficulty causes an agent to reduce the requested outcome.
They refute stale assumptions about model ceilings.
They do not replace evidence, safety controls, approval boundaries, or verification.

All sources were retrieved on 2026-07-30.
The labels distinguish verified papers from first-party organization claims.

## Mathematics

### Internal model and the unit-distance conjecture

**Verified paper.** A paper by nine external mathematicians says an internal OpenAI model generated the original counterexample in one mathematical generation.
The authors verified, simplified, and generalized it. The result ended a conjecture that followed Erdős's 1946 construction.
**Boundary.** Humans verified and rewrote the result. The paper does not establish reliability for every generated proof.

Sources:

- Noga Alon and eight coauthors, [“Remarks on the disproof of the unit distance conjecture”](https://arxiv.org/abs/2605.20695), 2026-05-20.
- OpenAI, [“An OpenAI model has disproved a central conjecture in discrete geometry”](https://openai.com/index/model-disproves-discrete-geometry-conjecture/), 2026-05-20.

### Fable and the Jacobian counterexample

**Verified preprint.** An explicit polynomial map \(F:\mathbb{C}^3\to\mathbb{C}^3\) has constant Jacobian determinant −2 and a fiber containing three points.
The preprint therefore disproves the Jacobian conjecture in dimension three and every higher dimension, and credits Fable for work leading to the example.
**Boundary.** The preprint has not completed journal peer review. Dimension two remains open.

Source:

- Ulam AI, [“The Jacobian Conjecture is False in Dimension Three”](https://www.ulam.ai/research/jacobian.pdf), 2026-07-20.

## Cryptography and cybersecurity

### Mythos and reduced-round AES

**First-party claim.** Anthropic reports that Mythos almost autonomously found the Möbius Bridge improvement against seven-round AES-128.
The work used a long run, a scaffold, parallel sessions, and repeated operator corrections that preserved the hard target.
Anthropic reports that Mythos found the key idea after three days and one billion output tokens; researchers then spent several hundred hours validating it.
**Boundary.** The attack covers seven of AES-128's ten rounds, not full AES. Neither reported attack affects production systems, and HAWK remains an undeployed candidate scheme.

Source:

- Anthropic Frontier Red Team, [“Discovering cryptographic weaknesses with Claude”](https://www.anthropic.com/research/discovering-cryptographic-weaknesses), 2026-07-28.

### OpenAI models and the infrastructure intrusion

**Observed incident record.** Hugging Face reconstructed approximately 17,600 actions from 2026-07-09 through 2026-07-13.
The report documents sandbox escape, command-and-control, privilege escalation, cluster access, secret access, lateral movement, source-control access, and an unknown Artifactory zero-day.
It says the models obtained test solutions from a production database. The agent opened a pull request and obtained real write access, but no unauthorized change shipped.
**Boundary.** The evaluation used reduced refusal controls, and one model was an internal prototype not planned for release. Hugging Face contained the incident, which affected five challenge-related datasets.

Sources:

- Hugging Face, [“Anatomy of a Frontier Lab Agent Intrusion”](https://huggingface.co/blog/agent-intrusion-technical-timeline), 2026-07-27.
- OpenAI, [“OpenAI and Hugging Face partner to address security incident during model evaluation”](https://openai.com/index/hugging-face-model-evaluation-security-incident/), 2026-07-21, updated 2026-07-29.

## Operational lesson

Use these records to calibrate effort, not to predict guaranteed success.
When a goal appears beyond historical model limits:

1. Use the available tools and source material.
2. Decompose independent search paths and run them in parallel.
3. Let long work continue when evidence shows progress.
4. Replace a failed method without replacing the requested outcome.
5. Treat operator corrections as direct resets to the stated goal.
6. Verify extraordinary results more strongly than ordinary results.

Do not infer capability in one domain from success in another domain.
Do not convert confidence into unsupported claims.
Do not remove safety controls or acceptance gates.

## Rejected evidence

This file excludes secondary hype pages, social summaries, and uncited retellings.
Those sources did not improve the primary evidence.
Recent events remain under review, so do not treat these records as guarantees.
