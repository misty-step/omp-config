# Voice And Raw-Transcript Premise Metadata

Use this reference only when a `/groom` premise source is voice-derived or a
raw transcript excerpt.
Use it to preserve provenance and uncertainty.
Do not store raw audio or treat transcript text as user-authored input.

Place the block inside `## Premise Source`, after the `Premise Source:` line:

```markdown
Voice Transcript Metadata:
- source_kind: voice
- source_hash: sha256:<digest>
- transcript_model: unknown
- transcript_confidence: unknown
- audio_duration_seconds: unknown
- redaction_status: redacted
- redaction_tool: agent-transcript
- created_at: 2026-06-04T00:00:00Z
- residual_risk: Transcript accuracy is unverified.
```

## Fields

| Field | Required | Allowed values | Privacy class | Notes |
|---|---|---|---|---|
| `source_kind` | yes | `voice`, `raw_transcript` | internal | Use only for voice-derived or raw-transcript premise artifacts. |
| `source_hash` | yes | `sha256:<64 hex>` | internal | Must match the `Premise Source:` digest. |
| `transcript_model` | yes | model id or `unknown` | internal | Use `unknown` only when you state it explicitly. |
| `transcript_confidence` | yes | `0..1` or `unknown` | sensitive | This is metadata, not accuracy proof. |
| `audio_duration_seconds` | yes | non-negative number or `unknown` | sensitive | Do not retain raw audio just to compute this. |
| `redaction_status` | yes | `redacted`, `sanitized` | internal | Do not store raw or unredacted transcript text. |
| `redaction_tool` | yes | tool name or `unknown` | internal | Redact private transcript excerpts before inclusion; never embed raw logs. |
| `created_at` | yes | ISO-8601 timestamp, not future | internal | Record the timestamp for the transcript or premise artifact metadata. |
| `residual_risk` | yes | substantive text | internal | Name uncertainty, especially transcript accuracy and omitted context. |

## Rules

- Treat missing metadata fields as failures.
  Spell unknown model, confidence, or duration as `unknown`. Do not omit them.
- Reject raw audio paths such as `.wav`, `.mp3`, `.m4a`, `.flac`, `.aac`, `.aiff`,
  or `.ogg`. This ticket does not permit raw audio retention in the repo, even
  with a waiver.
- Make `source_hash` match the digest in the `Premise Source:` line.
- Use the block to prove provenance and uncertainty only.
  Do not use it to prove transcript accuracy, speaker identity, consent, or
  completeness.
