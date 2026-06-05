# Network security controls & DDoS playbook

Defensive detail (End-to-End Network Security; DDoS Handbook; Security+). All defensive/operational.

## Segmentation patterns
- **Tiered:** Internet → DMZ (web/reverse-proxy) → app tier → data tier, each separated by firewall rules; data tier never reachable from the internet.
- **By trust/role:** separate VLANs for corporate, servers, **guest**, **IoT/OT**, VoIP, and **management**. Guest/IoT get internet-only, isolated from internal.
- **Microsegmentation (zero-trust):** per-workload allow-lists for east-west traffic; identity-based, not IP-based.
- **Management plane:** out-of-band or a locked-down jump network; MFA; never internet-exposed.

## Firewalls & filtering
- **Stateful** firewall tracks connection state (allows return traffic for established flows). **NGFW** adds app-ID, user-ID, IPS, and TLS inspection.
- **Rule hygiene:** default-deny inbound; least-privilege allow-lists; specific src/dst/port; remove stale rules; log denies; no `any any`. Order matters (first match).
- **Host firewalls** (nftables/Windows Firewall) for per-endpoint defense-in-depth.
- **Egress filtering** — restrict outbound to break C2/exfiltration; allow-list where feasible.
- **ACLs** on routers/switches for coarse, high-throughput filtering.

## IDS / IPS
- **IDS** detects & alerts (out-of-band, tap/SPAN); **IPS** is inline and blocks. 
- **Signature-based** (known patterns) + **anomaly/behavioral** (deviation from baseline). 
- Placement: perimeter, between segments, in front of critical assets. **Tune** to control false positives (alert fatigue kills IDS value). Feed alerts to the SIEM.

## VPN / encrypted access
- **IPsec** — site-to-site tunnels and remote access (IKEv2); ESP for confidentiality+integrity. 
- **TLS VPN** — client-friendly, port 443. **WireGuard** — modern, small, fast, simple keys.
- **NAC / 802.1X** — authenticate device/user before LAN access (EAP); posture check; dynamic VLAN. 
- **Remote access:** MFA everywhere; bastion/jump host; just-in-time, time-boxed access; never expose RDP/SSH/admin directly.

## DDoS taxonomy & mitigation
| Class | Examples | Mitigation |
|------|----------|-----------|
| **Volumetric** | UDP/ICMP flood; **amplification/reflection** (DNS, NTP, memcached, SSDP) | mitigate **upstream**: cloud scrubbing (Cloudflare/AWS Shield/Akamai), ISP filtering, **anycast** to spread load, BGP blackhole/flowspec; overprovision |
| **Protocol / state** | SYN flood, ACK flood, fragmented packets, Smurf | **SYN cookies**, stateful firewall protections, connection rate limits, drop malformed/fragments |
| **Application (L7)** | HTTP flood, **Slowloris** (low-and-slow), cache-busting | **WAF**, request rate limiting, behavioral/bot detection, CAPTCHA, connection timeouts, caching/CDN |

**Principles:** you cannot absorb a large volumetric attack at your own edge — push it **upstream/cloud**. Have a **runbook** (who to call, how to enable scrubbing, how to shed load). Build for **graceful degradation** ([[site-reliability-engineering]]): rate-limit, queue, serve cached/static, shed non-critical features. Reflection/amplification also means: **don't run open resolvers/NTP** that others abuse (be a good citizen).

## DNS & email controls
- DNS: filtering/sinkholing of malicious domains, DoT/DoH, DNSSEC for integrity; protect against cache poisoning; rate-limit to avoid being an amplifier.
- Email: **SPF + DKIM + DMARC**, attachment/link filtering, anti-phishing (the #1 initial-access vector).

## Wireless
WPA3 (or WPA2-AES) — never WEP/WPA/TKIP; 802.1X/EAP enterprise auth or strong PSK; separate **guest/IoT SSIDs** mapped to isolated VLANs; disable WPS; rogue-AP detection; minimize SSID broadcast leakage. 

## Monitoring & detection
Centralize logs (firewall, flow, DNS, endpoint, auth) in a **SIEM**; baseline normal; alert on: traffic spikes, port scans, new/unexpected flows, beaconing (regular small outbound = C2), lateral movement, auth anomalies/impossible travel, data egress spikes. **NetFlow/sFlow** for traffic visibility; full packet capture at choke points for forensics.

## Incident response (NIST 800-61)
1. **Prepare** — plan, contacts, tooling, runbooks, backups.
2. **Detect & analyze** — confirm, scope, triage severity.
3. **Contain** — isolate affected segments/hosts (segmentation pays off); preserve evidence.
4. **Eradicate** — remove the foothold, patch the entry.
5. **Recover** — restore from known-good, monitor for recurrence.
6. **Lessons learned** — blameless postmortem ([[site-reliability-engineering]]); fix the systemic cause.

## Quick review checklist (for the network-security-reviewer use case)
Default-deny firewall? least-privilege rules, no any-any? management plane isolated & MFA'd? segmentation between user/server/IoT/guest? IDS/IPS tuned & logging to SIEM? VPN/encrypted access with MFA? no internet-exposed RDP/SSH/admin? DDoS plan (upstream scrubbing)? egress filtering? WPA3 + isolated guest/IoT Wi-Fi? logging/alerting on the golden signals? IR runbook tested?
