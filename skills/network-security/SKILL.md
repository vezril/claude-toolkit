---
name: network-security
description: Defensive network and infrastructure security — protecting networks, traffic, and perimeters — distilled from *End-to-End Network Security*, the *DDoS Handbook*, and CompTIA Security+ network domains. Covers defense-in-depth and zero-trust, network segmentation (VLANs/subnets/DMZ/microsegmentation), firewalls (stateful, NGFW, host firewalls) and ACLs, IDS/IPS, VPNs and encrypted transport (IPsec, TLS, WireGuard), secure remote access and NAC/802.1X, secure DNS and email controls, DDoS attack types (volumetric, protocol, application-layer) and mitigation (rate limiting, scrubbing, anycast, upstream/cloud protection), monitoring & detection (logging, NetFlow, SIEM, the golden signals of attack), wireless security, and incident response basics. Strictly defensive/operational — understanding attacks in order to detect and mitigate them, not to launch them. Use when designing or reviewing network defenses, segmentation, firewall/VPN configs, DDoS resilience, IDS/IPS, or secure remote access. Complements secure-coding (application/code security) and cryptography (the primitives); pairs with network-engineering, computer-networks, site-reliability-engineering, and the network-security-reviewer use case.
---

# Network Security

**Defending networks and infrastructure** — the security layer that sits on top of [[computer-networks]] / [[network-engineering]] / [[tcp-ip]]. Distilled from ***End-to-End Network Security*** (Santos), the ***DDoS Handbook***, and the **CompTIA Security+** network domains. This is the **infrastructure** counterpart to [[secure-coding]] (application/code security) and uses the primitives from [[cryptography]].

> **Defensive only.** This skill is about *detecting, mitigating, and preventing* attacks — understanding how attacks work so you can defend, not perform them. (Consistent with the toolkit's stance: no offensive/exploit content.)

Cross-links: [[computer-networks]], [[network-engineering]], [[tcp-ip]] (what you're securing), [[secure-coding]] (app layer), [[cryptography]] (TLS/IPsec primitives), [[site-reliability-engineering]] (detection, on-call, incident response), [[os-security]] (host hardening).

## Defense-in-depth & zero-trust

- **Defense-in-depth:** layered controls so no single failure is fatal — perimeter + segmentation + host + application + data + monitoring. Assume any one layer can be breached.
- **Zero-trust:** "never trust, always verify." No implicit trust from network location; authenticate and authorize **every** access, least-privilege, **microsegment** so a breach can't move laterally. The modern replacement for the hard-perimeter/soft-interior model.
- **Least privilege & need-to-know** applied to network reachability: a host should only reach what it must.

## Segmentation (the highest-leverage control)

Divide the network so a compromise is contained:
- **VLANs / subnets** to separate user, server, IoT, guest, and management traffic ([[network-engineering]]).
- **DMZ** — a buffer zone for internet-facing services, isolated from the internal network.
- **Microsegmentation** — fine-grained, per-workload policy (zero-trust); east-west traffic is filtered, not just north-south.
- Separate and lock down the **management plane** (out-of-band where possible); never expose device admin to the internet.

## Perimeter & traffic controls

- **Firewalls:** stateful inspection (track connection state) → **NGFW** (app-aware, user-aware, with IPS/TLS-inspection). **Host-based firewalls** on endpoints. **ACLs** on routers/switches for coarse filtering. Default-deny inbound; explicit allow-lists.
- **IDS/IPS:** detect (IDS) or detect-and-block (IPS) malicious traffic via signatures and anomaly/behavioral analysis. Tune to cut false positives; place at choke points and key segments.
- **Secure DNS & email:** DNS filtering/sinkholing, DoT/DoH, DNSSEC; email SPF/DKIM/DMARC and filtering (a top attack vector).
- **Proxies / web filtering** for egress control; **egress filtering** to stop exfiltration and C2.

## Encrypted transport & remote access

- **VPNs:** **IPsec** (site-to-site, and remote access), **TLS/SSL VPNs**, **WireGuard** (modern, simple, fast). Encrypt traffic over untrusted networks; terminate at the edge ([[network-engineering]]). Primitives from [[cryptography]].
- **TLS everywhere** for app traffic; mind certificate management and TLS-inspection trade-offs (privacy vs visibility).
- **NAC / 802.1X** — authenticate devices/users before granting network access; posture checks; dynamic VLAN assignment.
- **Secure remote access:** MFA, bastion/jump hosts, just-in-time access — never expose RDP/SSH directly.

## DDoS — understand to defend

DDoS overwhelms a target's resources. Know the categories to mitigate them:
- **Volumetric** — saturate bandwidth (UDP/ICMP floods, **amplification/reflection** via DNS/NTP/memcached). Mitigate **upstream** — you can't absorb 1 Tbps at your edge.
- **Protocol/state-exhaustion** — SYN floods, fragmented-packet attacks; exhaust connection tables/firewalls. Mitigate with SYN cookies, stateful protections, rate limits.
- **Application-layer (L7)** — low-and-slow (Slowloris), HTTP floods that look like real users; hardest to detect. Mitigate with WAF, rate limiting, behavioral analysis, CAPTCHAs.

**Mitigation toolkit:** rate limiting & traffic shaping, **anycast** to spread load, **scrubbing centers**/cloud DDoS protection (Cloudflare/AWS Shield/Akamai), upstream/ISP filtering (BGP blackhole/flowspec), overprovisioning + autoscaling, a tested **runbook**. Resilience is a [[site-reliability-engineering]] concern too (capacity, graceful degradation). See `references/controls.md`.

## Monitoring, detection & response

- **Logging & telemetry:** device/firewall/flow logs, **NetFlow/sFlow**, packet capture at choke points, endpoint telemetry — centralized in a **SIEM**.
- **Detection:** signatures + anomaly baselines; watch for the "golden signals" of attack (traffic spikes, new flows, scanning, beaconing/C2, lateral movement, auth anomalies).
- **Incident response** (NIST): Prepare → Detect & Analyze → Contain → Eradicate → Recover → Lessons learned. Have a plan *before* the incident; isolate (segmentation pays off), preserve evidence, communicate.

## Wireless & edge

WPA2/WPA3 (not WEP/WPA), strong PSK or 802.1X/EAP enterprise auth, separate **guest/IoT SSIDs → isolated VLANs**, disable WPS, manage rogue APs. The SOHO/prosumer edge (firewall/router + managed APs) applies all of the above at small scale.

## Anti-patterns

- **Flat network** with no segmentation → one compromise owns everything (the classic ransomware enabler).
- Hard-perimeter/soft-interior trust instead of **zero-trust**; implicit trust by IP/location.
- Exposing **management interfaces / RDP / SSH** to the internet; no MFA on remote access.
- **Blocking all ICMP** (breaks diagnostics/PMTUD — rate-limit instead); over-permissive any-any firewall rules.
- Trying to absorb a **volumetric DDoS at your own edge** instead of upstream/cloud scrubbing.
- IDS/IPS deployed and never tuned (alert fatigue → ignored alerts); no centralized logging/SIEM.
- WEP/WPA or a shared flat Wi-Fi for guests, IoT, and trusted devices together.
- Treating network security as a substitute for [[secure-coding]] (or vice-versa) — you need both.

## Always-apply

1. **Defense-in-depth + zero-trust + least privilege**; assume breach.
2. **Segment aggressively** (VLANs/DMZ/microsegmentation); isolate management, guest, and IoT.
3. **Default-deny firewalls**, tuned **IDS/IPS**, **encrypted transport** (IPsec/TLS/WireGuard), **NAC/MFA** for access.
4. **DDoS:** mitigate volumetric **upstream/cloud**, protocol with rate-limits/SYN cookies, L7 with WAF/behavioral — and have a runbook.
5. **Log centrally (SIEM), detect on anomalies, and rehearse incident response.** Pair with [[secure-coding]] + [[cryptography]].

## How to use the reference

- **`references/controls.md`** — firewall/IDS-IPS/VPN/NAC specifics, the DDoS attack taxonomy + mitigation playbook, segmentation patterns, and the detection/IR checklist.

## Related

- [[secure-coding]] — application/code security (the other half of "secure"); [[cryptography]] — the TLS/IPsec/WPA primitives.
- [[computer-networks]] / [[tcp-ip]] / [[network-engineering]] — what's being defended, and the protocol/diagnostic detail.
- [[site-reliability-engineering]] — detection, capacity, graceful degradation, incident response.
- [[os-security]] — host hardening behind the network controls.
- Sources: *End-to-End Network Security: Defense-in-Depth* (Omar Santos); the *DDoS Handbook*; CompTIA **Security+** network/security domains.
