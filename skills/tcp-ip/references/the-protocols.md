# TCP/IP — protocol detail

Header fields, the TCP state machine, and key behaviors (Stevens, *TCP/IP Illustrated Vol 1*).

## IPv4 header (20 bytes, no options)
Version · IHL · DSCP/ECN · Total Length · Identification · Flags (DF/MF) · Fragment Offset · **TTL** · **Protocol** (1 ICMP, 6 TCP, 17 UDP) · Header Checksum · **Source IP** · **Dest IP** · [Options]. IPv6: fixed 40-byte header, 128-bit addresses, no header checksum, no router fragmentation (hosts do PMTUD), extension headers for options, flow label.

## Addressing & subnetting (recap; math in network-engineering)
CIDR `a.b.c.d/n`: first `n` bits = network, rest = host. Mask = `n` ones. Network address (hosts all-0), broadcast (hosts all-1), usable hosts = 2^(32−n) − 2. Private: 10/8, 172.16/12, 192.168/16. Off-subnet → default gateway.

## ARP
Local IPv4→MAC resolution: broadcast "who has 10.0.0.5?" → target unicasts its MAC; cached (timeout). Gratuitous ARP announces/updates. IPv6 → NDP (ICMPv6 neighbor solicitation/advertisement). Only valid within one broadcast domain.

## ICMP (diagnostics)
- **Echo request/reply** → `ping` (reachability + RTT).
- **Time exceeded** (TTL hit 0) → `traceroute`/`tracert` (send packets with TTL 1,2,3… and read who replies).
- **Destination unreachable** (net/host/port; and **fragmentation needed + DF** → PMTUD).
- **Redirect** (better gateway). Rate-limit ICMP rather than blocking it (blocking breaks PMTUD/diagnostics).

## UDP
8-byte header: source port, dest port, length, checksum. No state, no reliability/ordering. DNS, DHCP, NTP, VoIP, QUIC substrate.

## TCP header & key fields
Source/Dest port · **Sequence number** · **Acknowledgment number** · Data offset · **Flags** (SYN, ACK, FIN, RST, PSH, URG) · **Window** · Checksum · Urgent pointer · Options (**MSS**, **window scale**, **SACK**, timestamps).

### Connection lifecycle
- **Open (3-way handshake):** `SYN(seq=x)` → `SYN(seq=y),ACK(x+1)` → `ACK(y+1)`. Options (MSS, wscale, SACK) negotiated here.
- **Data:** byte-stream; each byte numbered; cumulative **ACK**s; **PSH** to deliver promptly.
- **Close (4-way):** `FIN`/`ACK` each direction. The active closer enters **TIME_WAIT** (~2×MSL) to absorb delayed segments and ensure the final ACK arrived — too many simultaneous closers → port exhaustion. `RST` is an abrupt abort.

### Reliability & timers
- **RTO** from smoothed RTT + variance (Jacobson/Karn); exponential backoff on repeated loss.
- **Fast retransmit/recovery:** 3 duplicate ACKs ⇒ retransmit without waiting for RTO.
- **Persist timer** (probe a zero window), **keepalive timer** (detect dead peers).

### Flow vs congestion control
- **Flow control** = receiver-driven: the advertised **window** caps in-flight data so the receiver isn't overrun. **Window scaling** for high bandwidth-delay-product links.
- **Congestion control** = network-driven: **cwnd** with **slow start** (exponential until ssthresh) → **congestion avoidance** (AIMD: +1 MSS/RTT, halve on loss). Variants: Reno, **CUBIC** (Linux default), **BBR** (model-based). Loss/ECN are the congestion signals.
- **MSS** = link MTU − IP − TCP headers (≈1460 on Ethernet). MSS/PMTUD mismatch over tunnels/VPNs → stalls; "MSS clamping" is the common fix.

## DNS
Hierarchy: root (`.`) → TLD (`.com`) → authoritative. **Recursive resolver** does the legwork and caches by **TTL**. Records: A/AAAA, CNAME, MX, NS, TXT, PTR (reverse), SOA. UDP/53 (TCP/53 for large responses & zone transfers). DoT/DoH encrypt it. Tools: `dig`, `nslookup`, `host`.

## DHCP (DORA)
**Discover** (client broadcast) → **Offer** (server) → **Request** (client) → **Ack** (server) — leases IP, mask, gateway, DNS, lease time. UDP/67-68, broadcast; a **DHCP relay** forwards across subnets. Conflicts/expiry → renewal at T1/T2.

## NAT / PAT
Rewrites source (and tracks) addresses/ports so private hosts share a public IP. **PAT** ("overload") multiplexes by port — the home-router default. Breaks inbound-initiated connections → **port forwarding**, **UPnP**, or NAT traversal (STUN/TURN/ICE). Hairpinning = a host reaching another via the public IP from inside. CGNAT adds a second NAT layer at the ISP.

## Diagnostic toolbox (maps to the network-troubleshooter agent)
`ping` (ICMP reachability/RTT) · `traceroute`/`mtr` (path + per-hop loss) · `dig`/`nslookup` (DNS) · `arp` (link cache) · `ip`/`ifconfig` (interfaces/routes) · `ss`/`netstat` (sockets/states) · `tcpdump`/`tshark`/Wireshark (capture & decode) · `nmap` (port/host discovery on your own networks) · `curl -v` (app + TLS). Work bottom-up: link/ARP → IP/route → MTU → DNS → TCP handshake → app.
