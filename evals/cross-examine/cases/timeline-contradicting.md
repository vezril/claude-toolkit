# Timeline: VOICE-101

## Scope
- Identifiers used: sess-9f31c2, window 2026-07-10T09:02:00Z..09:04:00Z
- Services covered: AICAA, AudioConnector (AISM: no matching lines)
- Log stores queried: platform CLI (full window in retention)

## Timeline
| Time (UTC) | Service | Event | Evidence |
|------------|---------|-------|----------|
| 09:02:03.114 | AudioConnector | WebSocket opened from telephony edge | E1 |
| 09:02:03.610 | AICAA | agent pipeline ready, state=ACTIVE | E2 |
| 09:02:04.002 | AICAA | TTS synthesis started (greeting) | E3 |
| 09:02:07.881 | AICAA | TTS synthesis complete, 3.8s audio streamed | E4 |
| 09:02:14.310 | AICAA | inbound audio energy detected, VAD=speech | E5 |
| 09:02:16.702 | AICAA | utterance end, 2.4s segment submitted to STT | E6 |
| 09:02:26.703 | AICAA | WARN STT request still pending after 10s (attempt 1) | E7 |
| 09:02:31.120 | AICAA | STT retry submitted (attempt 2, 5s budget) | E8 |
| 09:02:36.704 | AICAA | ERROR STT failed after retry: upstream timeout; no transcript | E9 |
| 09:02:37.230 | AICAA | TTS synthesis started (fallback: ask caller to repeat) | E10 |
| 09:02:40.115 | AICAA | TTS synthesis complete, 2.6s audio streamed | E11 |
| 09:02:41.020 | AudioConnector | outbound audio frames delivered to telephony edge | E12 |
| 09:03:14.118 | AudioConnector | close message received (reason=client hangup) | E13 |
| 09:03:14.290 | AICAA | session closed, duration=71s, turns_completed=0 | E14 |

## Anomalies
- The fallback prompt was synthesized and delivered (09:02:37-09:02:41) but the caller still hung up 33s later with no further inbound speech detected.
- No inbound audio energy events after 09:02:16 despite the session staying ACTIVE.

## Evidence
- **E8** `2026-07-10T09:02:31.120Z AICAA INFO [sess-9f31c2] STT retry submitted (attempt 2, budget 5s)`
- **E10** `2026-07-10T09:02:37.230Z AICAA INFO [sess-9f31c2] TTS synthesis started (fallback prompt: ask caller to repeat)`
- **E11** `2026-07-10T09:02:40.115Z AICAA INFO [sess-9f31c2] TTS synthesis complete, 2.6s audio streamed`
- **E12** `2026-07-10T09:02:41.020Z AudioConnector INFO [sess-9f31c2] outbound audio frames delivered`
- **E14** `2026-07-10T09:03:14.290Z AICAA INFO [sess-9f31c2] AudioSessionEntity closed, duration=71s, turns_completed=0`

## Gaps
- No inbound-audio diagnostics from the telephony edge; cannot see whether the caller's audio reached AudioConnector after 09:02:16.
