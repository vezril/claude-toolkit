# Subnetting, switching & routing — detail

Working reference for the practitioner skill (Network Warrior / CCNA / Network+).

## Subnetting & VLSM

**The mask.** `/n` = n network bits. Block size in the "interesting octet" = 256 − mask value. Usable hosts = 2^(32−n) − 2.

Common masks:
| CIDR | Mask | Hosts | Use |
|------|------|-------|-----|
| /24 | 255.255.255.0 | 254 | user LAN |
| /25 | 255.255.255.128 | 126 | split a /24 |
| /26 | 255.255.255.192 | 62 | small LAN |
| /27 | 255.255.255.224 | 30 | small segment |
| /30 | 255.255.255.252 | 2 | point-to-point link |
| /31 | 255.255.255.254 | 2* | P2P (RFC 3021) |

**Find the subnet of an IP:** block size = 256 − mask octet; the address falls in the multiple-of-block-size range. e.g. `192.168.1.100/26`: block 64 → subnets .0/.64/.128/.192 → 100 is in **.64** (network .64, broadcast .127, hosts .65–.126).

**VLSM example** — give `192.168.10.0/24` to: LAN-A 100 hosts, LAN-B 50, LAN-C 25, and two P2P links.
- LAN-A needs ≥100 → `/25` (126): `192.168.10.0/25` (.1–.126)
- LAN-B needs ≥50 → `/26` (62): `192.168.10.128/26` (.129–.190)
- LAN-C needs ≥25 → `/27` (30): `192.168.10.192/27` (.193–.222)
- P2P links → `/30` each: `192.168.10.224/30`, `192.168.10.228/30`
Allocate largest-first to avoid fragmentation; summarize upstream as `192.168.10.0/24`.

**Local vs remote decision:** host ANDs the destination with its own mask; equal to its own network ⇒ ARP and send directly; else send to the **default gateway's** MAC (gateway must be in the host's subnet).

## Switching detail

- **CAM/MAC table:** switch learns source MAC→ingress port; forwards to the known port, floods if unknown/broadcast/multicast; entries age out.
- **VLANs:** logical broadcast domains. **Access port** = one untagged VLAN (to a host). **Trunk port** = many VLANs, tagged with **802.1Q** (4-byte tag, 12-bit VLAN ID = 4094 usable). **Native VLAN** = untagged traffic on a trunk (match both ends; a security note — don't use VLAN 1).
- **Inter-VLAN routing:** router-on-a-stick (subinterfaces per VLAN on one trunk) or **SVIs** on a Layer-3 switch.
- **STP/RSTP:** elect a **root bridge** (lowest priority+MAC); each non-root picks a **root port**; per-segment **designated port**; others **blocked** → loop-free tree. RSTP converges in seconds. **PortFast** (edge ports skip listening/learning) + **BPDU Guard** (shut a port that unexpectedly sees BPDUs). Disabling STP on redundant links = broadcast-storm meltdown.
- **EtherChannel/LACP:** bundle 2–8 links as one logical link (bandwidth + redundancy); must match config both ends.

## Routing detail

**Routing table & forwarding:**
- **Longest-prefix match:** most specific route wins (a `/32` beats a `/24` beats `/0`).
- **Administrative distance (AD)** picks between *sources* of the same prefix: Connected 0, Static 1, eBGP 20, EIGRP 90, OSPF 110, RIP 120, iBGP 200. Lower wins.
- **Metric** picks within a protocol: OSPF cost (bandwidth-based), EIGRP composite (bw+delay), RIP hop count.
- **Default route** `0.0.0.0/0` → the gateway of last resort.

**Routing-protocol comparison:**
| Protocol | Type | Algorithm | Scope | Notes |
|----------|------|-----------|-------|-------|
| Static | — | manual | any | simple, no overhead, no adapt |
| RIP | distance-vector | Bellman-Ford, hop count | small IGP | ≤15 hops; legacy |
| OSPF | link-state | Dijkstra/SPF | IGP, large | areas; fast convergence; open standard |
| EIGRP | adv. distance-vector | DUAL | IGP | Cisco; fast, easy |
| BGP | path-vector | policy | EGP (internet) | between ASes; multi-homing; not shortest-path |

**Convergence** = time for all routers to agree after a change; link-state (OSPF) and DUAL (EIGRP) converge fast, RIP slowly. **First-hop redundancy** (HSRP/VRRP/GLBP) gives hosts a virtual gateway IP that fails over.

## Quick troubleshooting map
- No link → physical (cable/SFP/port, duplex).
- Link but no L2 → VLAN/trunk/native mismatch, STP blocking, MAC issues.
- L2 ok, no L3 → IP/mask/gateway wrong, missing route, ARP failing, wrong subnet.
- L3 ok, app fails → firewall/ACL, NAT, DNS, MTU/MSS.
- Slow/intermittent → duplex mismatch, congestion/QoS, STP flaps, loss (check interface counters, `mtr`).
