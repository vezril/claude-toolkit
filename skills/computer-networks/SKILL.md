---
name: computer-networks
description: Computer networking fundamentals — the layered model and how the internet actually works, distilled from Tanenbaum's *Computer Networks*. The meta/overview skill for the networking cluster. Covers the OSI 7-layer and TCP/IP 5-layer reference models and what each layer does (physical, data link, network, transport, application); core design principles (layering, encapsulation, protocols & services, connection-oriented vs connectionless, packet vs circuit switching, the end-to-end principle, statistical multiplexing); key concepts per layer (framing/MAC/error & flow control; addressing, routing, and the internetwork; reliable transport, congestion control; the application protocols); performance fundamentals (bandwidth, latency, throughput, the bandwidth-delay product); and how LANs, WANs, and the internet are structured. Use to get oriented in networking, understand where a protocol or problem sits in the stack, learn the layered model, or decide which deeper networking skill to reach for. Routes to tcp-ip (the protocol suite in depth), network-engineering (practical routing/switching/admin), and network-security; pairs with os-io-and-devices and information-theory.
---

# Computer Networks

The **meta/overview** of the networking cluster: a correct mental model of how networks are layered and how the internet works, from **Tanenbaum's *Computer Networks***. Get the layered model right and every protocol, tool, and failure has an obvious home. This skill is the map; the deeper skills are the territory.

Routes to: [[tcp-ip]] (the TCP/IP protocol suite at the wire), [[network-engineering]] (practical routing/switching/subnetting/troubleshooting), [[network-security]] (defending networks). Cross-links [[os-io-and-devices]] (NICs, drivers, the host's network stack), [[information-theory]] (channel capacity, coding — the physical-layer limits), [[docker]] (container networking), [[site-reliability-engineering]] (operating networked systems).

## The layered model

Networks are built as a **stack of layers**, each providing services to the layer above and using the layer below, talking to its peer via a **protocol**. This is the single most important idea in networking.

**OSI (7-layer, the reference)** vs **TCP/IP (5-layer, what we actually use)**:

| TCP/IP layer | OSI | Job | Examples |
|---|---|---|---|
| Application | 5–7 | app-level protocols | HTTP, DNS, SMTP, SSH, TLS |
| Transport | 4 | process-to-process delivery | TCP, UDP, QUIC |
| Network (Internet) | 3 | host-to-host across networks; routing & addressing | IP, ICMP, routing protocols |
| Data link | 2 | frame delivery on one link; MAC | Ethernet, Wi-Fi, ARP, switches |
| Physical | 1 | bits on the medium | copper, fiber, radio |

Two foundational mechanisms:
- **Encapsulation** — each layer wraps the layer above in its own header (and the link layer adds a trailer): application data → TCP segment → IP packet → Ethernet frame → bits. Each layer reads only its own header. (The PDU names: segment/datagram → packet → frame.)
- **Services vs protocols** — a *service* is what a layer offers; a *protocol* is the rules peers use to implement it. Keep them distinct.

## Design principles (the durable ideas)

- **The end-to-end principle** — put function in the endpoints, not the network, unless the network can do it strictly better. Why IP is a dumb, best-effort core and TCP adds reliability at the edges.
- **Connection-oriented vs connectionless** — a reliable virtual circuit (TCP) vs fire-and-forget datagrams (UDP/IP); the trade of reliability/ordering vs latency/simplicity.
- **Packet switching vs circuit switching** — statistical multiplexing of bursty traffic (the internet) vs dedicated channels (old telephony). Packet switching wins on efficiency, at the cost of variable delay/loss.
- **Layering & modularity** — independent evolution (swap Ethernet for Wi-Fi without touching TCP), at a small efficiency cost. The "hourglass": everything over **IP**, IP over everything.
- **Best-effort + retransmission** — the network may drop/reorder/duplicate; reliability is rebuilt above it.

## What each layer does (orientation)

- **Physical** — encode bits onto a medium; bandwidth limited by Shannon/Nyquist ([[information-theory]]); modulation, cabling, signaling.
- **Data link** — group bits into **frames**, deliver across one hop, **MAC addressing**, error detection (CRC), and on shared media **medium access** (CSMA/CD historically, switching today). Ethernet, Wi-Fi (802.11), switches, VLANs, ARP (link↔network glue). → [[network-engineering]]
- **Network** — move packets **host-to-host across many links**: the **IP address**, the **internetwork** of routers, **routing** (shortest-path, distance-vector vs link-state), forwarding, fragmentation, ICMP. → [[tcp-ip]], [[network-engineering]]
- **Transport** — **process-to-process** (ports): **TCP** (reliable, ordered, flow + congestion control, the 3-way handshake) and **UDP** (unreliable, low-overhead). → [[tcp-ip]]
- **Application** — what users/programs actually speak: DNS (names→addresses), HTTP, SMTP, SSH, TLS (security as an app/transport-adjacent layer — [[cryptography]]). → [[tcp-ip]]

## Performance fundamentals

- **Bandwidth** (capacity, bits/s) ≠ **throughput** (achieved) ≠ **latency** (delay). Total latency = propagation + transmission + queuing + processing.
- **Bandwidth-delay product** (bandwidth × RTT) = bits "in flight"; sets the window size needed to keep a pipe full (why high-BDP "long fat networks" need large TCP windows).
- **Jitter** (delay variation) and **loss** matter as much as raw bandwidth for real-time traffic.
- Bottleneck thinking: the path is only as fast as its slowest link / most congested queue.

## How the internet is structured

End hosts → **LAN** (switched Ethernet/Wi-Fi, often one IP subnet) → **gateway/router** → **ISP** → a mesh of **autonomous systems (AS)** peering via **BGP** → the global internet. **DNS** resolves names to addresses; **NAT** lets many private hosts share public IPs ([[tcp-ip]]). LAN vs WAN is about scope and who owns the links.

## Anti-patterns / misconceptions

- Reasoning about a problem without placing it in a **layer** (is it physical, link, IP, transport, or app? — the first troubleshooting question).
- Conflating **MAC address** (link-local, one hop) with **IP address** (end-to-end, routed).
- Assuming the network is reliable/ordered/secure — it is **best-effort**; reliability and security are added above ([[network-security]]).
- Treating bandwidth as the only performance metric (latency, jitter, loss, BDP often dominate).
- Confusing a **switch** (layer 2, MAC) with a **router** (layer 3, IP).

## Always-apply

1. **Locate everything in the stack first** (physical → link → network → transport → application).
2. Think in **encapsulation**: data gains/sheds a header per layer; each layer reads only its own.
3. Respect the **end-to-end principle** and **best-effort** core — reliability/security live at the edges.
4. Separate **bandwidth / throughput / latency**; use the **bandwidth-delay product** to reason about pipes.
5. Reach for the right depth: **[[tcp-ip]]** for protocol detail, **[[network-engineering]]** for build/operate, **[[network-security]]** for defense.

## Related

- [[tcp-ip]] — the TCP/IP protocol suite (IP/ARP/ICMP/UDP/TCP/DNS/DHCP/NAT) at the packet level.
- [[network-engineering]] — practical routing, switching, subnetting, VLANs, and troubleshooting.
- [[network-security]] — firewalls, VPNs, segmentation, IDS/IPS, DDoS defense.
- [[os-io-and-devices]] — the host network stack, NICs, drivers, interrupts/DMA.
- [[information-theory]] — channel capacity, coding, the physical-layer limits.
- [[cryptography]] — TLS/IPsec primitives that secure the layers above.
- [[docker]] — container networking (bridges, NAT, overlay) builds on these basics.
- Source: *Computer Networks* (Andrew S. Tanenbaum & David J. Wetherall, 5th ed.).
