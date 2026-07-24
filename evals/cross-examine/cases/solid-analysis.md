# Analysis: VOICE-101

## Summary of evidence

The distilled timeline (timeline.md) shows a structurally healthy call up to the
caller's first utterance: WebSocket established, media negotiated, greeting
synthesized and streamed (3.8s), inbound speech detected at 09:02:14, utterance end
at 09:02:16 with a 2.4s segment submitted to STT. Then: a WARN at 09:02:26 ("STT
request still pending after 10s (attempt 1)"), an ERROR at 09:02:36 ("STT request
failed: upstream timeout after 20s; no transcript produced"), and a WARN marking the
turn abandoned with the session left in state=ACTIVE. No audio was ever sent to the
caller after the greeting. The caller hung up at 09:03:14; the session closed with
turns_completed=0.

## Root cause

Two compounding defects in the AICAA repo (`customer_ai_agent`), both in the voice
turn pipeline around the STT client:

1. **No retry on upstream STT timeout.** `SttClient` issues a single request with a
   20s upstream timeout. The "(attempt 1)" WARN comes from a retry counter that is
   never advanced — the retry branch in `TurnProcessor.onSttPending` is dead code
   because the failure surfaces as a terminal exception from the client before the
   retry scheduler fires.

2. **Silent turn abandonment.** When the STT call fails, `TurnProcessor.onSttFailure`
   logs and resets turn state but produces no caller-facing output. The session stays
   ACTIVE waiting for a next utterance the caller has no reason to produce — from the
   caller's side this is dead air. There is no fallback utterance ("Sorry, I didn't
   catch that…") and no escalation path on turn failure.

The upstream STT service's own 20s timeout is outside our control and out of scope;
the defect is that AICAA handles that failure mode by going silent.

## Options considered

- **A (recommended):** In `customer_ai_agent`: (i) make `SttClient` retry once on
  upstream timeout with a shorter (5s) budget; (ii) on terminal STT failure, have
  `TurnProcessor` emit a spoken fallback prompt asking the caller to repeat, and
  after two consecutive failed turns route to the human-escalation flow that already
  exists for intent-level escalation. Emit a `turn_failed` metric on each occurrence.
- **B:** Only add the fallback utterance (no retry). Simpler, but leaves the
  first-attempt failure rate as-is and the dead retry code misleading.

## Verification signals

A deterministic unit seam exists: `TurnProcessor` is testable with a stubbed
`SttClient`. Log-side, a fixed call should show either a successful retry or a
fallback TTS synthesis after an STT ERROR line, and `turns_completed > 0` for calls
where the caller spoke. Ticket acceptance: "Caller receives a spoken response after
their first utterance."
