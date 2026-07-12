# 802.11 foundations — why the features work

Source: documentation.hak5.org/wifi-pineapple/wifi-basics (fetched 2026-07). The technical substrate under PineAP, Recon, deauth, and handshake capture.

## Radios, chipsets, modes

- A **radio** is a transceiver (WNIC) on PCI/USB; an **SoC** integrates radio + CPU (MIPS/ARM). Best chipset support: **Atheros, Mediatek** (some Ralink/Realtek).
- **Mark VII chipsets:** **MT7601U** (2.4 GHz primary) + **MT7610U** (5 GHz-capable secondary); native 2.4 GHz, optional 5 GHz via USB adapter. (Enterprise = native 2.4+5.)
- **Station (STA)** is the umbrella term; infrastructure mode splits into **AP** (base station / hub) and **client stations**.
- **Modes:** **Master** (APs) · **Managed** (clients) · **Monitor / RFMON** (passively captures ALL nearby traffic regardless of association — needs driver+firmware support; this is what enables Recon + handshake capture) · secondary: ad-hoc, mesh, P2P, repeater. Not all radios support every mode or more than one at once.
- **Why monitor + injection matter:** monitor = passive omniscient capture; injection = actively transmit arbitrary frames. Together they are Recon (listen), deauth (inject), and handshake capture (deauth → forced reauth → sniff the 4-way handshake). One radio can monitor/inject while another serves an AP role.

## RF layer

- **Transmit power:** chipset baseline ~**20 dBm = 100 mW** (`txpower`); external amps may not report through the SoC (real output ≠ reported). **EIRP** = radio dBm + amp + antenna dBi (e.g. 24 dBm + 5 dBi = 29 dBm ≈ 800 mW). **FCC:** 2.4 GHz point-to-multipoint max **36 dBm EIRP (4 W)**.
- **Antennas** shape, don't create, power (gain in dBi over isotropic). **Omnidirectional** (≈spherical; ships standard; best for surrounding detection; above ~9 dBi vertical range collapses) vs **directional** (concentrated; good for targeting one device/area, poor for general survey). "More gain is not always better."
- **Channels/regions:** **2.4 GHz** — 14 channels, 22 MHz each, non-overlapping **1/6/11/14** (ch1 centered 2.412 GHz); regional: NA 1–11, most of world 1–13, Japan 1–14. **5 GHz** — U-NII 1–3, 45 channels, 20/40/80/160 MHz. **A radio occupies one channel at a time** → channel-hopping for full-spectrum recon. Regulatory domain caps channels + power.

## Protocols

- **802.11a** (5 GHz, 54 Mbps) · **b** (2.4 GHz, 11 Mbps) · **g** (2.4 GHz, faster via better encoding) · **n** (up to 1800 Mbps) · **ac** (up to 1800 Mbps). Encoding via **OFDM + QAM**. (MT7601U is a 2.4 GHz b/g/n-class part.)

## Addressing

- **MAC** = 6 octets (`00:C0:CA:8F:5E:80`); first three = **OUI** (IEEE-assigned vendor). **Universally administered** = burned in ROM; **locally administered** = software override = **MAC spoofing** (basis for the Pineapple spoofing its MAC and for client MAC randomization).
- **Broadcast MAC `FF:FF:FF:FF:FF:FF`** = all stations in vicinity (beacons use it; interfaces listen to broadcast by default). **Multicast** = a specific group (service discovery / mDNS).
- **SSID** = network name (≤32 chars). **BSSID** = derived from the AP's NIC MAC. **BSS** = one AP + clients; **ESS/ESSID** = multiple APs sharing an SSID (roaming). **Key trust:** clients treat any AP broadcasting the same SSID as the same network and will associate — the basis of the **Evil Twin** and the probe-driven SSID pool (clients reveal preferred SSIDs in probe requests; the Pineapple answers as them).

## 802.11 frames

- **Three classes:** **Management** (run the infrastructure — advertise, connect, tear down) · **Control** (spectrum access — RTS/CTS/ACK) · **Data** (payload; body ≤2312 bytes, larger packets fragment).
- **Frame structure:** MAC Header (Frame Control + address fields BSSID/source/destination) → Payload/Body → **FCS** (CRC).
- **Management subtypes:** **Beacon** (AP advertisement — SSID, rates, params; to broadcast, many/sec; drives passive Recon) · **Probe Request** (client seeks APs; directed probes reveal preferred SSIDs → Karma/SSID-pool) · **Probe Response** · **Association / Reassociation Request+Response** · **Disassociation** (graceful) · **Authentication** ("almost always open"; real security is post-association) · **Deauthentication** (an **unencrypted, spoofable** management frame → the deauth attack).
- **Frame injection:** transmit any frame regardless of association. **Deauth injection** = craft a deauth with **spoofed source+destination MACs** to force-disconnect a client → triggers a fresh handshake for capture. **Beacon injection/flooding** = inject arbitrary/fake SSIDs. Not all radios/drivers support injection. **PineAP leverages frame injection to run its attacks.**

## Association state machine (the lever behind deauth + handshakes)

1. **Unauthenticated + Unassociated** — client discovers APs (passive beacons or active probes); learns channel/protocol/rate.
2. **Authenticated + Unassociated** — client sends authentication; AP responds success (open).
3. **Authenticated + Associated** — association request/response; then security negotiation (WPA2) and network init (DHCP).

Deauth/disassociation knocks a station **back down** the ladder — forcing the reconnection whose 4-way handshake you capture. Open networks skip security straight to DHCP.

- **Logical configs:** point-to-point · **point-to-multipoint = Infrastructure mode** (AP + many clients — the common case, the Pineapple's primary target) · multipoint-to-multipoint (ad-hoc/mesh).
- **Pineapple specifics:** its client network is **open**; DHCP hands clients addresses in **172.16.42.0/24**.

> Docs gaps (absent from the .md sources, not omitted here): hidden-SSID mechanics, per-radio virtual-interface/BSSID multiplexing, and numeric frame type/subtype codes.
