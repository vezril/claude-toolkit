---
name: os-security
description: "Operating-system protection and security — how an OS isolates principals and enforces access, and the threats it must withstand. Covers the distinction between protection (mechanism) and security (policy/threats), the principle of least privilege, protection domains and the access matrix and its implementations (access control lists vs capabilities), users/groups/rings and the kernel-user privilege boundary, authentication, the OS attack surface (the syscall boundary, drivers, setuid, confused-deputy problems), isolation and sandboxing (namespaces, seccomp, MAC: SELinux/AppArmor, virtualization), and trusted computing basics. Use when reasoning about OS-level protection/isolation, designing access control or sandboxing, hardening a kernel's user/kernel boundary, or understanding capabilities vs ACLs. Defensive/architecture-focused; part of the operating-systems skill set, pairs with secure-coding and cryptography."
---

# OS Protection & Security

How an OS keeps principals (users, processes) from harming each other, the kernel, and the data they shouldn't touch. **Defensive and architectural** — about isolation mechanisms and sound design, not attacks. Part of the [[operating-systems]] set; pairs with [[secure-coding]] (application-level hardening) and [[cryptography]]. *(This skill does not cover exploit development — that boundary holds; the value here is building isolation that resists attack.)*

## Protection vs security

- **Protection** = the *mechanism* that controls access of processes/users to resources (the access matrix, page protection, privilege levels). Internal, policy-neutral.
- **Security** = defending against *threats* given a threat model (malicious users, untrusted code, network attackers) — the policy and the broader posture. Protection is a tool security uses.

The bedrock mechanism is the **dual-mode (kernel/user) privilege boundary** ([[operating-systems]]): user code can't execute privileged instructions or touch kernel/other-process memory (enforced by the CPU + MMU). Everything else builds on it.

## Principle of least privilege

Give each principal (process, user, module, token) the **minimum** rights needed, for the **minimum** time. It bounds the damage of any compromise or bug and is the single most important design rule — it underlies capabilities, dropping privileges, sandboxing, microkernels (drivers in user space), and the [[secure-coding]] posture.

## The access matrix and its implementations

Model access as a matrix: **rows = domains/principals**, **columns = objects**, **cells = allowed operations** (read/write/execute/own). Two practical ways to store it (it's sparse):
- **Access Control Lists (ACLs)** — store per **object** the list of (principal → rights). Easy to see "who can access X" and to revoke per object; this is the Unix `rwx` owner/group/other model, POSIX ACLs, Windows ACLs. Most file systems use ACLs.
- **Capabilities** — store per **subject** an unforgeable token (handle) that *is* the right to an object; possession = permission. Composable, least-privilege-friendly, avoids "ambient authority" and the **confused-deputy** problem; harder to audit/revoke globally. Seen in capability OSes (seL4, KeyKOS), and in Linux **file descriptors** and POSIX **capabilities** (splitting root into fine-grained bits). 
A **protection domain** is the set of rights a process runs with; **switching domains** (setuid, syscalls into the kernel, sandboxes) changes the active rights — a sensitive operation.

## Authentication & principals

The OS maps logins to principals (users/groups) via **authentication**: passwords (stored as **salted slow-hash** digests — see [[cryptography]]/[[secure-coding]], never plaintext), multi-factor, tokens, biometrics. Once authenticated, **authorization** uses the access-matrix mechanisms above. Sessions, credentials, and uid/gid carry identity through the system.

## The OS attack surface (defensive view)

Where protection must be airtight:
- **The system-call boundary** — every syscall is an entry from untrusted user space into the privileged kernel; arguments (pointers, lengths, fds) must be **validated and copied carefully** (never trust a user pointer; guard against TOCTOU). The bulk of kernel vulnerabilities live here and in drivers.
- **Device drivers** — large, privileged, often third-party; the riskiest kernel code. Microkernels mitigate by running them in user space.
- **setuid / privilege escalation paths** — programs that gain privilege must be minimal and careful; the classic source of escalation.
- **Confused deputy** — a privileged component tricked into misusing its authority on behalf of a caller (capabilities help avoid this).
- **Side channels** — timing/cache/speculative-execution leaks (Spectre/Meltdown class) cross isolation boundaries without violating the access matrix; mitigations are architectural (KPTI, microcode, constant-time code — [[secure-coding]]).

## Isolation & sandboxing (defense in depth)

- **Memory isolation** via the MMU/page protection (per-process address spaces, NX, supervisor bits — [[os-memory-and-virtual-memory]]).
- **Mandatory Access Control (MAC)** — SELinux/AppArmor: a system-wide policy the *kernel* enforces regardless of user discretion (vs the discretionary owner-controlled ACLs).
- **Sandboxing** — seccomp(-bpf) to restrict the syscalls a process may make, namespaces+cgroups (containers — [[os-virtualization]]), `chroot`/jails, and **VMs** for the strongest isolation. Layer them.
- **Trusted computing** — secure boot, a TPM, measured boot, and a minimized **Trusted Computing Base (TCB)** (keep the security-critical code small — the seL4 argument; a smaller TCB is easier to get right and verify).

## Always-apply notes (for implementation/hardening)

- Treat the **kernel/user boundary as a trust boundary**: validate and copy all syscall arguments; never dereference user pointers directly; check bounds and permissions on every path ([[secure-coding]] input-handling).
- Apply **least privilege** everywhere: drop privileges after setup, run drivers/services with the minimum rights, prefer capabilities/fds over ambient authority.
- Keep the **TCB small**; isolate risky components (drivers, parsers) — a microkernel or user-space-driver design limits blast radius.
- Set page protections correctly (NX, no W^X violations, supervisor-only kernel pages) — hardware-enforced isolation is your strongest control.
- Defense in depth: combine MMU isolation + MAC + sandboxing + minimal privilege; assume any one layer can fail.

## Related

- [[operating-systems]] (map; dual-mode/syscalls) · [[os-memory-and-virtual-memory]] (MMU isolation) · [[os-virtualization]] (containers/VMs as isolation) · [[osdev-kernel]] (the user/kernel boundary in practice).
- [[secure-coding]] — application-level hardening and the syscall-argument/input-validation discipline; [[cryptography]] — password hashing, secure boot, auth.
- Sources: Silberschatz Ch. 16–17 (Protection, Security); Tanenbaum Ch. 9 (Security); OSTEP (mechanisms via the user/kernel boundary).
