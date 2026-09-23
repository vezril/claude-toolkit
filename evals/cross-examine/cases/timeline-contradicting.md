# Timeline: VOICE-101

## Scope
- Identifiers used: sess-9f31c2, window 2026-07-10T09:02:00Z..09:04:00Z
- Services covered: voice-agent, audio-bridge (session-manager: no matching lines)
- Log stores queried: platform CLI (full window in retention)

## Timeline
| Time (UTC) | Service | Event | Evidence |
|------------|---------|-------|----------|
| 09:02:03.114 | audio-bridge | WebSocket opened from telephony edge | E1 |
| 09:02:03.610 | voice-agent | agent pipeline ready, state=ACTIVE | E2 |
| 09:02:04.002 | voice-agent | TTS synthesis started (greeting) | E3 |
| 09:02:07.881 | voice-agent | TTS synthesis complete, 3.8s audio streamed | E4 |
| 09:02:14.310 | voice-agent | inbound audio energy detected, VAD=speech | E5 |
| 09:02:16.702 | voice-agent | utterance end, 2.4s segment submitted to STT | E6 |
| 09:02:26.703 | voice-agent | WARN STT request still pending after 10s (attempt 1) | E7 |
| 09:02:31.120 | voice-agent | STT retry submitted (attempt 2, 5s budget) | E8 |
| 09:02:36.704 | voice-agent | ERROR STT failed after retry: upstream timeout; no transcript | E9 |
| 09:02:37.230 | voice-agent | TTS synthesis started (fallback: ask caller to repeat) | E10 |
| 09:02:40.115 | voice-agent | TTS synthesis complete, 2.6s audio streamed | E11 |
| 09:02:41.020 | audio-bridge | outbound audio frames delivered to telephony edge | E12 |
| 09:03:14.118 | audio-bridge | close message received (reason=client hangup) | E13 |
| 09:03:14.290 | voice-agent | session closed, duration=71s, turns_completed=0 | E14 |

## Anomalies
- The fallback prompt was synthesized and delivered (09:02:37-09:02:41) but the caller still hung up 33s later with no further inbound speech detected.
- No inbound audio energy events after 09:02:16 despite the session staying ACTIVE.

## Evidence
- **E8** `2026-07-10T09:02:31.120Z voice-agent INFO [sess-9f31c2] STT retry submitted (attempt 2, budget 5s)`
- **E10** `2026-07-10T09:02:37.230Z voice-agent INFO [sess-9f31c2] TTS synthesis started (fallback prompt: ask caller to repeat)`
- **E11** `2026-07-10T09:02:40.115Z voice-agent INFO [sess-9f31c2] TTS synthesis complete, 2.6s audio streamed`
- **E12** `2026-07-10T09:02:41.020Z audio-bridge INFO [sess-9f31c2] outbound audio frames delivered`
- **E14** `2026-07-10T09:03:14.290Z voice-agent INFO [sess-9f31c2] SessionEntity closed, duration=71s, turns_completed=0`

## Gaps
- No inbound-audio diagnostics from the telephony edge; cannot see whether the caller's audio reached audio-bridge after 09:02:16.
