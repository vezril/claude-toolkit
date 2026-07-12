# Setup, internet, recovery, adapters

Source: documentation.hak5.org/wifi-pineapple/setup + /faq (fetched 2026-07). Mark VII 2.x-era; version-pinned facts flagged.

## First boot & connection

- **Connect the antennas before powering on** (the docs stress this).
- Powered + driven over **USB-C** (power and data; USB-C→USB-A adapter works). Needs plain **5V, ≥2A** (not all USB-C PD adapters supply 5V; a 2A+ battery bank works). Enumerates on the host as a **USB Ethernet adapter** — the recommended setup path is wired USB, not WiFi.
- **Web UI: `http://172.16.42.1:1471`** — port **1471** is non-standard and required. Device management IP **172.16.42.1**.

**Stager (initial setup):** ships running "the stager," a minimal firmware that downloads + flashes the full firmware. Flow: (1) press the reset button when prompted (physical-presence proof — stops a stranger in RF range from configuring it); (2) join a known upstream WiFi network (stager supports **WPA2/WPA only**); (3) auto-download + install full firmware; (4) wait **10–15 min** for flash + boot; (5) reach `http://172.16.42.1:1471`. Fallback: manual firmware upload via the Network page.

## Per-OS connection (host static IP)

- **Linux** (`eth0`): IP `172.16.42.42`, mask `255.255.255.0` (**/24**), gateway unset.
  ```
  sudo ip link set eth0 down
  sudo ip addr add 172.16.42.42/255.255.255.0 dev eth0
  sudo ip link set eth0 up
  ```
- **Windows** (Win 11; similar 7–10): static IPv4 on the Pineapple adapter — IP `172.16.42.42`, mask **`255.255.0.0`** (**/16**, wider than Linux), gateway blank, DNS `8.8.8.8` / `8.8.4.4`. Path: Network & Internet → More network adapter options → adapter Properties → IPv4.
- **macOS: not supported on macOS 11 (Big Sur)+** — the driver-model change broke the ASIX AX88772 USB-Ethernet driver (native driver only for 10.9–10.15). Use Linux/Windows over USB-C, or a VM with USB pass-through (VMware Fusion + Kali reported working; M1: Parallels/Fusion Preview) — pass the USB device into the VM, don't install macOS native drivers. Wireless-LAN operation is unaffected.
- **Over WiFi (setup only):** open AP `Pineapple_XXXX` (last 4 of MAC), host gets DHCP; press the button when prompted. After setup those open networks are removed; reconnect via your management network at `172.16.42.1:1471`.

## Internet: Client Mode / ICS / USB Ethernet

- **Client Mode** (Pineapple as a station on an upstream AP): uses **`wlan2`** ("greatly recommended… dedicated for Client Mode"). **Settings > Networking → Wireless Client Mode → Scan → pick SSID + PSK → Connect**; shows associated SSID + DHCP IP; auto-reconnects on boot. Static IP needs the Web Terminal. **Auditing implication:** wlan2 is consumed, so it's unavailable for attack/recon while client mode is up.
- **ICS over USB-C:** Windows — internet-facing adapter → Properties → **Sharing** → allow + select the Pineapple adapter; then set the Pineapple adapter IPv4 (IP `172.16.42.42`, mask `255.255.0.0`, DNS `8.8.8.8`/`8.8.4.4`). Linux — the doc only says ICS = **masquerading/NAT**, exact steps **distribution-dependent** (no canonical commands given — roll your own NAT).
- **USB Ethernet adapter** (wired uplink): supported out-of-box — **ASIX AX88179** (USB2 10/100), **Realtek RTL8152** (USB2 10/100), **Realtek RTL8153** (USB3 gigabit). Other chipsets: **Modules > Packages**, search the chipset for a kernel module.

## Recovery & maintenance (watch the LED)

- **Password reset** (firmware **1.1.0+**): fully boot, then **hold Reset ≥10 s**. Success = LED **rainbow** then reboot; if no rainbow, press harder/longer. Log in with default `hak5pineapple`. Works over USB-C or open WiFi.
- **Factory reset / recovery + re-flash:** **hold Reset while applying power** → LED flashes **RED ×3** → release → rapid red → **SOLID RED** = recovery mode (if it turns **BLUE**, power-cycle and retry). Set host to `172.16.42.42`, browse to **`http://172.16.42.1`** (recovery UI — **no port**), upload the `.bin` **recovery** image, **Update firmware**, don't unplug. Then normal setup at `:1471`.
- **Updates:** Settings > General → check/auto-install, or upload a local `.bin`. **Updating factory-resets the device** (redo setup; recon data lost). LED **alternating red/blue** during update; **5–10 min**; don't unplug. SSH host key regenerates on first boot after a flash.
- **Setup by USB disk** (offline): single-partition USB (ext4 / exFAT-FAT / NTFS), inserted in the **USB-A port before power**. Firmware `.bin` on root (keep name `upgrade-x.x.x.bin`). `config.txt` (ASCII, root) keys: `ROOT_PASSWORD`, `HOSTNAME`, `TIMEZONE`, `MANAGEMENT_SSID`, `MANAGEMENT_PSK`, `ACCEPT_LICENSE=TRUE`. Optional `device.config` for Cloud C² enrollment.

## Hardware / adapters

- **Chipsets out-of-box:** Mediatek **MT7601U** (2.4 GHz primary) + **MT7610U** (5 GHz-capable). Mark VII is natively 2.4 GHz; add 5 GHz/802.11ac via a supported USB adapter. (Docs name only **`wlan2`** by role — dedicated Client Mode — so don't assert wlan0/wlan1 assignments beyond that.)
- **Compatible 802.11ac USB adapters** (all **MT7612U**): **Hak5 MK7AC**, **Alfa AWUS036ACM**, **EP-AC1605 V1** (V2 **not** compatible). "Only MT7612U are confirmed to work correctly in all circumstances." Other chipsets: drivers via **Modules > Packages**.
- Contrast: the **WiFi Pineapple Enterprise** ships three MT7612U radios (native 2.4+5 GHz); the Mark VII adds 5 GHz via one USB adapter.
