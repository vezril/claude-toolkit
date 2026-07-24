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
| 09:02:36.704 | AICAA | ERROR STT failed: upstream timeout after 20s; no transcript | E8 |
| 09:02:36.705 | AICAA | WARN turn abandoned, awaiting next utterance, state=ACTIVE | E9 |
| 09:03:14.118 | AudioConnector | close message received (reason=client hangup) | E10 |
| 09:03:14.290 | AICAA | session closed, duration=71s, turns_completed=0 | E11 |

## Anomalies
- No TTS synthesis events between the greeting completion (09:02:07.881) and session close; the caller received no audio after the greeting.
- STT retry counter shows "attempt 1" but no attempt 2 appears before the terminal error.
- Session remained state=ACTIVE for 37s after the failed turn with no outbound activity.

## Evidence
- **E1** `2026-07-10T09:02:03.114Z AudioConnector INFO [sess-9f31c2] WebSocket connection opened`
- **E4** `2026-07-10T09:02:07.881Z AICAA INFO [sess-9f31c2] TTS synthesis complete, 3.8s audio streamed`
- **E8** `2026-07-10T09:02:36.704Z AICAA ERROR [sess-9f31c2] STT request failed: upstream timeout after 20s; no transcript produced`
- **E9** `2026-07-10T09:02:36.705Z AICAA WARN [sess-9f31c2] turn abandoned, awaiting next utterance, state=ACTIVE`
- **E11** `2026-07-10T09:03:14.290Z AICAA INFO [sess-9f31c2] AudioSessionEntity closed, duration=71s, turns_completed=0`

## Gaps
- None material to this window.
