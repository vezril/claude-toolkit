---
name: tcp-ip
description: The TCP/IP protocol suite at the wire level, distilled from Stevens' *TCP/IP Illustrated, Vol 1*. Covers the internet layer (IPv4/IPv6 addressing & headers, subnetting/CIDR, fragmentation, TTL; ICMP; ARP/NDP), the transport layer (UDP; TCP's three-way handshake, sequence/ACK, sliding-window flow control, retransmission & timers, congestion control — slow start/AIMD, connection teardown/TIME_WAIT), and the core application protocols (DNS resolution, DHCP/BOOTP, NAT/PAT, and where TLS sits). Use when reasoning about packets and protocol behavior — reading a packet capture, debugging a handshake/retransmission/MTU/MSS issue, understanding ports/sockets, ARP/DNS/DHCP/NAT behavior, congestion or window problems, or how a protocol field works. The protocol-depth complement to computer-networks (the model) and network-engineering (build/operate); pairs with network-security and the network-troubleshooter agent.
---

# TCP/IP

How the **TCP/IP protocol suite actually works on the wire**, from **W. Richard Stevens' *TCP/IP Illustrated, Volume 1: The Protocols*** — the definitive packet-level account. Where [[computer-networks]] gives the layered model, this skill is the protocol detail you need to read a capture or debug a real connection.

Cross-links: [[computer-networks]] (the model this sits in), [[network-engineering]] (configuring routing/subnets/NAT), [[network-security]] (securing/inspecting these protocols), [[cryptography]] (TLS/IPsec over them), the **network-troubleshooter** agent (which exercises these with `ping`/`traceroute`/`dig`/`tcpdump`).

## Internet layer

**IP (the host-to-host datagram).**
- **Addressing:** IPv4 (32-bit, dotted quad) and IPv6 (128-bit, hex). **CIDR** notation (`/24`) = prefix length; the mask splits network vs host bits. Private ranges (RFC 1918: `10/8`, `172.16/12`, `192.168/16`), loopback `127/8`, link-local `169.254/16` / `fe80::/10`. → subnetting math in [[network-engineering]].
- **The IP header:** version, IHL, TTL (hop limit — decremented per router, ICMP "time exceeded" at 0, the basis of `traceroute`), protocol (TCP=6/UDP=17/ICMP=1), source/dest, fragmentation fields. IPv6 simplifies the header and drops in-network fragmentation.
- **Fragmentation & MTU:** links have an **MTU** (Ethernet 1500); oversized datagrams fragment (IPv4) — but **Path MTU Discovery** (DF bit + ICMP) is preferred; black-holed PMTUD is a classic real-world bug. Relates to TCP **MSS**.
- **Best-effort:** IP may drop/reorder/duplicate; no delivery guarantee (that's TCP's job).

**ICMP** — IP's control/error companion: echo request/reply (**ping**), destination unreachable, **time exceeded** (traceroute), redirect, fragmentation-needed (PMTUD). Diagnosing with ICMP is half of network troubleshooting.

**ARP / NDP** — the link↔network glue: **ARP** maps an IPv4 address to a MAC on the local segment (broadcast "who has X?" → unicast reply, cached); IPv6 uses **NDP** (Neighbor Discovery over ICMPv6). ARP only works within one subnet — off-subnet traffic goes to the default gateway's MAC.

## Transport layer

**UDP** — thin wrapper over IP: ports + length + checksum, **no** connection, ordering, or reliability. Low overhead; used by DNS, DHCP, VoIP, QUIC's substrate, games. The app handles loss if it cares.

**TCP** — reliable, ordered, byte-stream, connection-oriented:
- **Three-way handshake:** SYN → SYN/ACK → ACK establishes the connection and exchanges initial sequence numbers and options (MSS, window scaling, SACK).
- **Reliability:** every byte has a **sequence number**; the receiver **ACKs**; unacked data is **retransmitted** after the **RTO** (adaptive, from RTT estimation) or via **fast retransmit** (3 duplicate ACKs).
- **Flow control:** the **sliding window** (receiver's advertised window) stops a fast sender overrunning a slow receiver; **window scaling** for high-BDP links.
- **Congestion control:** **slow start** (exponential cwnd growth) → **congestion avoidance** (AIMD — additive increase, multiplicative decrease on loss); variants (Reno/CUBIC/BBR). This is what shares the internet fairly.
- **Teardown:** FIN/ACK each direction; **TIME_WAIT** holds the closer ~2×MSL to absorb stray segments (a common source of "address already in use" / port-exhaustion at scale).
- **MSS** = MTU − IP − TCP headers; mismatches with PMTUD cause stalls.

See `references/the-protocols.md` for headers, state machine, and worked behaviors.

## Application-layer essentials

- **DNS** — names → addresses. Recursive vs authoritative resolution, the root → TLD → authoritative hierarchy, record types (A/AAAA, CNAME, MX, TXT, NS, PTR), TTL/caching, mostly **UDP/53** (TCP for large/zone transfers), and DoT/DoH for privacy. `dig`/`nslookup` are your tools.
- **DHCP** (and its BOOTP ancestor) — automatic host config: the **DORA** exchange (Discover, Offer, Request, Ack) leases IP + mask + gateway + DNS. Broadcast-based; relayed across subnets by a DHCP relay.
- **NAT / PAT** — rewrites addresses/ports so many private hosts share a public IP (PAT = "NAT overload" by port). Enables IPv4 conservation; complicates inbound connections (port forwarding, hairpinning, NAT traversal/STUN). → [[network-engineering]], [[network-security]].
- **Where TLS sits** — between TCP and the app; it secures the byte stream but the TCP/IP behaviors below are unchanged ([[cryptography]]).

## Reading the wire (the practical payoff)

The whole point: given a `tcpdump`/Wireshark capture you can tell a SYN storm from a retransmission storm, a DNS failure from a routing failure, an MTU black hole from congestion. The **network-troubleshooter** agent operationalizes this.

## Anti-patterns / gotchas

- Confusing **MAC** (ARP, one segment) with **IP** (routed); expecting ARP to cross subnets.
- Ignoring **MTU/MSS / PMTUD** — silent stalls on tunnels/VPNs when ICMP is filtered.
- Treating **UDP** as reliable; or assuming **TCP** preserves message boundaries (it's a byte stream — framing is the app's job).
- Forgetting **TIME_WAIT** / ephemeral-port exhaustion under high connection churn.
- Blocking **all ICMP** at the firewall (breaks PMTUD and diagnostics — rate-limit, don't kill).
- Hard-coding IPs instead of names; ignoring DNS **TTL/caching** when debugging "it still resolves to the old IP."

## Always-apply

1. Identify the **protocol and layer** of the symptom (IP? ICMP? ARP? TCP? DNS?) before guessing.
2. Reason in **headers and state**: TTL, flags, seq/ack, window, MSS/MTU.
3. Remember **best-effort IP + reliable TCP**; UDP is on its own.
4. Check the usual suspects in order: link/ARP → IP/routing → MTU → DNS → TCP handshake → app.
5. Don't filter all ICMP; mind **TIME_WAIT**, **PMTUD**, and DNS **TTL**.

## How to use the reference

- **`references/the-protocols.md`** — IPv4/IPv6 and TCP header fields, the TCP state machine, the handshake/teardown and retransmission/congestion behaviors, and ARP/ICMP/DNS/DHCP/NAT specifics with the diagnostic tools for each.

## Related

- [[computer-networks]] — the layered model these protocols implement.
- [[network-engineering]] — subnetting/CIDR math, routing, NAT, and VLANs in practice.
- [[network-security]] — firewalling, inspecting, and securing these protocols; DDoS at the TCP/IP layer.
- [[cryptography]] — TLS/IPsec that protect the data over TCP/IP.
- [[docker]] — container networking (veth/bridge/NAT) is these mechanisms in miniature.
- Source: *TCP/IP Illustrated, Volume 1: The Protocols* (W. Richard Stevens).
