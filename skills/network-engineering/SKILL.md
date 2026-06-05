---
name: network-engineering
description: Practical network engineering and administration — building and operating real LANs/WANs — distilled from *Network Warrior*, Cisco CCNA, and CompTIA Network+. Covers IP addressing & subnetting/VLSM/CIDR math, switching (Ethernet, VLANs, trunking/802.1Q, spanning tree/STP, link aggregation, the MAC table), routing (static routes, default gateways, the routing table/longest-prefix match, dynamic routing — OSPF, EIGRP, BGP, RIP — and administrative distance/metrics), NAT/PAT and DHCP/DNS in operation, WAN/edge concepts, network services and management (SNMP, NetFlow, syslog, QoS), cabling/media, and a structured troubleshooting methodology (the OSI bottom-up approach + the standard CLI tools). Use when designing or operating a network — subnetting/VLAN/addressing plans, configuring or reasoning about switches and routers, choosing/under­standing a routing protocol, planning NAT/DHCP, or troubleshooting connectivity/performance. The build-and-operate complement to computer-networks (the model) and tcp-ip (the protocols); pairs with network-security, devops/SRE, and the network-architect/troubleshooter agents.
---

# Network Engineering

The **build-and-operate** layer of networking — how to actually design, configure, and troubleshoot LANs and WANs — from ***Network Warrior*** (Donahue), **Cisco CCNA**, and **CompTIA Network+**. Where [[computer-networks]] is the model and [[tcp-ip]] is the protocols, this is the practitioner's skill: subnets, switches, routers, and a troubleshooting method.

Cross-links: [[computer-networks]] / [[tcp-ip]] (the foundations), [[network-security]] (segmentation, firewalls, secure configs), [[devops]] / [[site-reliability-engineering]] (network as operated infrastructure), the **network-architect** and **network-troubleshooter** agents.

## IP addressing & subnetting (the core skill)

You must be able to subnet fluently. **CIDR** `a.b.c.d/n`: the `/n` prefix is the network portion; the rest is host.
- **Usable hosts** = 2^(32−n) − 2 (network + broadcast reserved). `/24` = 254 hosts, `/30` = 2 (point-to-point links), `/31` = 2 usable for P2P (RFC 3021).
- **VLSM** — subnet a block into different-sized subnets to avoid waste (e.g. `/30`s for links, `/24`s for user LANs). **Summarization/supernetting** aggregates routes to shrink routing tables.
- Know the private ranges (RFC 1918), `169.254/16` APIPA (DHCP failed), and how a host decides **local vs remote** (AND the dest with your mask → same network = ARP directly, else send to the default gateway).
- IPv6: `/64` per subnet is standard; SLAAC vs DHCPv6; link-local `fe80::/10`.

Worked subnetting + a VLSM example in `references/routing-switching-subnetting.md`.

## Switching (Layer 2)

- **Ethernet & the switch**: a switch learns **MAC→port** mappings (the CAM table) and forwards frames only where needed; floods unknown/broadcast. Collision domains gone (full duplex); one **broadcast domain** per VLAN.
- **VLANs** segment one physical switch into many logical LANs (broadcast domains); inter-VLAN traffic needs a **router/L3 switch** ("router-on-a-stick" or SVIs). **802.1Q trunking** carries multiple VLANs on one link (tagged); access ports are untagged. A **native VLAN** carries untagged trunk traffic.
- **Spanning Tree (STP/RSTP/MSTP)** prevents loops in redundant L2 topologies by blocking ports to form a tree; know root-bridge election, port states, and that loops cause **broadcast storms**. PortFast/BPDU guard on edge ports.
- **Link aggregation (LACP/EtherChannel)** bonds links for bandwidth/redundancy.

## Routing (Layer 3)

- **The routing table & longest-prefix match**: the router picks the most specific matching route; `0.0.0.0/0` is the default route. **Administrative distance** breaks ties between sources (connected < static < EIGRP < OSPF < RIP); **metric** breaks ties within a protocol.
- **Static routing** — explicit, simple, no overhead; good for stubs and defaults; doesn't adapt.
- **Dynamic routing:**
  - **OSPF** — link-state IGP; builds a topology map, Dijkstra shortest-path, areas for scale; fast convergence. The workhorse interior protocol.
  - **EIGRP** — Cisco advanced distance-vector; fast (DUAL), easy.
  - **RIP** — legacy distance-vector (hop count, ≤15); know it, avoid it.
  - **BGP** — the path-vector **exterior** protocol that glues the internet (between autonomous systems); policy-driven, not shortest-path. Essential at the edge/multi-homing.
- **First-hop redundancy** (HSRP/VRRP) for gateway failover.

## Services in operation

- **DHCP** (DORA) and **DNS** deployment/relay; **NAT/PAT** at the edge (overload, port forwarding, hairpin) — mechanics in [[tcp-ip]], operations here.
- **QoS** — classify/queue/shape/police to protect latency-sensitive traffic (voice/video) under congestion (DSCP marking).
- **Management/observability**: **SNMP** (poll/traps), **NetFlow/sFlow** (traffic accounting), **syslog**, NTP. Feeds [[site-reliability-engineering]] monitoring.

## WAN & edge

Leased lines, MPLS, broadband, and increasingly **VPN/SD-WAN** over the internet ([[network-security]]). The edge router does NAT, firewalling, and BGP/multi-homing. Home/SMB edge: the all-in-one router/firewall (e.g. pfSense) + managed switches/APs.

## Troubleshooting methodology

Work the **OSI stack bottom-up** (the single most useful habit):
1. **Physical** — link light, cable, SFP, interface up/down, errors/CRCs.
2. **Data link** — VLAN/trunk config, STP state, MAC table, duplex mismatch.
3. **Network** — IP/mask/gateway correct? routing table? `ping` gateway, then beyond; `traceroute` the path.
4. **Transport** — port reachable? firewall/ACL? `ss`/`telnet host port`.
5. **Application/DNS** — `dig` the name; `curl -v`.
Isolate: works locally but not remotely → routing/NAT/firewall; intermittent → STP/duplex/congestion; "slow" → MTU/QoS/loss. Change one thing at a time; read the actual tables/counters. (Tools in [[tcp-ip]]; automated by the **network-troubleshooter** agent.)

## Anti-patterns

- Subnetting by guesswork; flat `/24`-everything with no VLAN segmentation; overlapping subnets (breaks routing/VPN).
- One giant **broadcast domain** (broadcast storms, no isolation) — segment with VLANs.
- Redundant L2 links with **STP disabled** → loop meltdown; no BPDU guard on edge ports.
- Default-route-only where dynamic routing is needed (or full dynamic routing where a static route would do).
- Duplex/speed **mismatch** (one side auto, one fixed) → silent performance collapse.
- No monitoring (SNMP/NetFlow/syslog) → flying blind; no documentation/diagram of the topology.
- Treating a **switch** as a **router** (or vice-versa); forgetting inter-VLAN routing needs L3.

## Always-apply

1. **Subnet deliberately** (VLSM, room to grow, summarizable); document the addressing plan.
2. **Segment with VLANs**; one broadcast domain per VLAN; route between them at L3.
3. **STP on** for redundant L2; **right routing tool** (static for stubs, OSPF interior, BGP exterior); mind **admin distance**.
4. **Troubleshoot bottom-up** the OSI stack, reading real tables/counters, changing one thing at a time.
5. **Instrument** the network (SNMP/NetFlow/syslog/NTP) and **document** the topology.

## How to use the reference

- **`references/routing-switching-subnetting.md`** — worked subnetting/VLSM, the VLAN/trunk/STP detail, the routing-table/longest-prefix/admin-distance mechanics, and a routing-protocol comparison.

## Related

- [[computer-networks]] — the layered model; [[tcp-ip]] — the protocols and diagnostic tools.
- [[network-security]] — segmentation, firewalls, ACLs, secure device config.
- [[site-reliability-engineering]] / [[devops]] — operating, monitoring, and automating network infrastructure.
- [[docker]] — container/overlay networking reuses VLAN/bridge/NAT/routing ideas.
- Sources: *Network Warrior, 2nd ed.* (Gary A. Donahue); Cisco **CCNA**; CompTIA **Network+ (N10-007)**.
