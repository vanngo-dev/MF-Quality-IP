# ADR 0004 — AI Investigation Summary

## Decision

Use a mock-first provider architecture for AI-assisted investigation summaries.

The default provider is:

```text
AI_SUMMARY_PROVIDER=mock
```

The backend exposes:

```text
POST /api/v1/investigations/{id}/ai-summary
```

Generated summaries are saved as structured JSON in:

```text
investigations.ai_summary
```

## Context

Quality engineers need help organizing investigation evidence from alerts, defects, sensor readings, station events, and investigation notes. The platform should demonstrate AI-assisted investigation support, but it must remain runnable without paid APIs or external keys.

## Why Mock Provider First

The mock provider keeps the project:

- deterministic
- testable
- demoable offline
- safe from accidental external network calls
- independent of paid API keys

It also forces the summary contract to be explicit before adding a real provider.

## Why Evidence Grounding Matters

Manufacturing quality decisions can affect people, equipment, and production flow. A summary must be grounded in platform evidence and must not invent a root cause.

Phase 12 uses only available records:

- linked alert details
- alert `evidence_json`
- related defects
- related sensor readings
- related station events
- investigation notes
- root-cause hypothesis
- investigation `evidence_json`

## Why External API Is Optional

Local development and portfolio demos should work with:

```text
AI_SUMMARY_PROVIDER=mock
```

Future external APIs can be added behind the same provider interface, but they are not required for the application to boot, test, or demonstrate the workflow.

## Guardrails Against Hallucinated Root Cause

Summaries must:

- use only available evidence
- include limitations
- call out missing evidence
- avoid certainty
- avoid invented root cause claims
- use cautious language such as `may indicate`, `possible`, and `based on available evidence`
- avoid recommending production shutdown unless existing evidence clearly supports it

AI is an assistant, not an authority. Engineers remain responsible for confirming root cause.

## Future OpenAI-Compatible Provider Plan

The placeholder provider reserves this configuration:

```text
AI_SUMMARY_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=
OPENAI_COMPATIBLE_API_KEY=
OPENAI_COMPATIBLE_MODEL=
```

Future implementation should:

- send only curated evidence context
- preserve the same structured response schema
- keep limitations mandatory
- reject responses that omit required fields
- keep tests network-free through mocks

## Tradeoffs

Mock-first summaries are less fluent than a production LLM, but they are predictable and safe for local development.

Persisting summaries as JSON avoids a new table in Phase 12, but it means summary history is not tracked yet.

Evidence grounding limits speculation, but that is the correct tradeoff for a manufacturing quality workflow where unsupported claims can mislead engineers.
