---
name: nginx
description: Nginx — the high-performance web server, reverse proxy, and load balancer — distilled from *Nginx HTTP Server* and *Nginx Module Extension*. Covers the architecture (event-driven, asynchronous, master/worker processes — why it scales to many connections), the configuration model (the config tree, contexts: main/events/http/server/location; directives; server blocks/virtual hosts; location matching & precedence), serving static files, as a reverse proxy (proxy_pass, upstreams, headers, buffering), load balancing (round-robin/least_conn/ip_hash, health/failover), TLS/HTTPS termination (certs, Let's Encrypt, HTTP→HTTPS redirect, modern TLS config), caching & compression (gzip/brotli, proxy_cache), rate limiting & access control, the module system (http modules, FastCGI/uWSGI for PHP/Python, stream module for TCP/UDP), and logging. Use when configuring or reviewing Nginx — reverse-proxying an app (Node/Next.js/Home Assistant), TLS termination, load balancing, location/server blocks, caching, rate limiting, or hardening. Pairs with nodejs/nextjs (apps it fronts), home-assistant (reverse proxy), docker, devops, and network-security.
---

# Nginx

The high-performance **web server, reverse proxy, and load balancer** — from ***Nginx HTTP Server*** and ***Nginx Module Extension***. Nginx is the standard front door for web apps: it serves static files, terminates TLS, and proxies/loads-balances to backends (Node, Next.js, Python, PHP) — and it's the natural reverse proxy for your home-lab services.

Cross-links: [[nodejs]] / [[nextjs]] (apps Nginx fronts), [[home-assistant]] (reverse-proxy HA with TLS), [[docker]] (Nginx in containers), [[devops]] / [[site-reliability-engineering]] (ops, load balancing), [[network-security]] (TLS, rate limiting, exposure), [[secure-coding]] (headers, hardening).

## Why Nginx scales (the architecture)

Nginx is **event-driven and asynchronous**: a small number of **worker processes** (typically one per CPU core) each handle **thousands of connections** in a non-blocking event loop — versus the old thread/process-per-connection model (Apache prefork) that exhausts memory under load. A **master process** reads config and manages workers (graceful reloads with no dropped connections). This is why Nginx excels at high concurrency, static files, and proxying. (Same non-blocking philosophy as [[nodejs]].)

## The configuration model

Config is a tree of **directives** grouped into **contexts** (blocks):
```nginx
# main context (worker_processes, user, ...)
events { worker_connections 1024; }
http {
  include mime.types;
  gzip on;
  server {                       # a virtual host
    listen 443 ssl;
    server_name example.com;
    root /var/www/example;
    location / { try_files $uri $uri/ =404; }      # static
    location /api/ { proxy_pass http://backend; }  # proxy
  }
}
```
- **Contexts:** `main` → `events` (connection processing) and `http` → `server` (virtual hosts) → `location` (per-path rules); plus `stream` (TCP/UDP), `mail`. Directives inherit downward and can be overridden.
- **`server` blocks** = virtual hosts, selected by `listen` + `server_name` (host-based routing; a `default_server`).
- **`location` matching & precedence** (the most error-prone part): exact `=` > prefix `^~` > regex `~`/`~*` (first match, in file order) > plain prefix (longest wins). Get this wrong and the wrong block handles the request.
- Test before reload: **`nginx -t`** then `nginx -s reload` (graceful). Keep config modular with `include sites-enabled/*`.

## Serving static files

`root`/`alias`, `index`, **`try_files $uri $uri/ =404`** (the canonical static/SPA fallback — for an SPA: `try_files $uri /index.html`), `expires`/`Cache-Control` for caching assets, `sendfile on`, `gzip`/brotli compression. Nginx is extremely fast at static content.

## Reverse proxy (the most common use)

Put Nginx in front of an app server ([[nodejs]]/[[nextjs]]/uWSGI):
```nginx
location / {
  proxy_pass http://127.0.0.1:3000;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```
- Always forward **`Host`** and **`X-Forwarded-*`** headers (apps need the real client IP/proto). For **WebSockets** (Home Assistant, Socket.IO): set `proxy_http_version 1.1` + `Upgrade`/`Connection` headers.
- `proxy_buffering`, timeouts (`proxy_read_timeout`), and `proxy_cache` for performance.

## Load balancing

```nginx
upstream backend {
  least_conn;                 # or default round-robin, or ip_hash (sticky)
  server 10.0.0.1:3000;
  server 10.0.0.2:3000;
  server 10.0.0.3:3000 backup;
}
```
Methods: **round-robin** (default), **least_conn**, **ip_hash** (session stickiness), weighted; passive **health checks**/failover (`max_fails`/`fail_timeout`), `backup` servers. Scale [[nodejs]] cluster instances or multiple containers behind it. ([[site-reliability-engineering]].)

## TLS / HTTPS

```nginx
server {
  listen 443 ssl http2;
  ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers ...;  # modern suite
}
server { listen 80; server_name example.com; return 301 https://$host$request_uri; }  # redirect
```
Terminate TLS at Nginx (one place to manage certs); **Let's Encrypt** (certbot) for free auto-renewing certs; **HTTP→HTTPS redirect**; enable **HTTP/2** (HTTP/3 in recent builds); HSTS and security headers ([[secure-coding]]). This is exactly how to securely expose [[home-assistant]] or a self-hosted app.

## Caching, compression, rate limiting & access control

- **Compression:** `gzip on` (+ types), brotli (module) — big bandwidth win.
- **Caching:** `proxy_cache` (cache backend responses), `expires`/`Cache-Control` for static; cache zones.
- **Rate limiting:** `limit_req_zone`/`limit_req` (requests/sec), `limit_conn` (connections) — basic DDoS/abuse defense ([[network-security]]).
- **Access control:** `allow`/`deny` (IP), `auth_basic` (basic auth), header filtering; restrict admin paths to LAN/VPN.

## Modules & the stream module

Nginx is modular (compiled-in or dynamic modules — *Nginx Module Extension*):
- **HTTP modules:** proxy, fastcgi (**PHP** via php-fpm), uwsgi/scgi (**Python**), gzip, ssl, headers, rewrite, geoip, rate-limit, etc.
- **`stream` module:** proxy/load-balance **raw TCP/UDP** (databases, MQTT, game servers) — not just HTTP.
- Dynamic modules (`load_module`); third-party modules; or use **OpenResty** (Nginx + Lua) for scripting. Most setups need only the bundled modules.

## Logging

`access_log` (configurable `log_format` — add `$request_time`, upstream timings), `error_log` (levels). Ship to a log stack ([[site-reliability-engineering]]); watch 4xx/5xx and upstream latency.

## Anti-patterns

- **`location` precedence mistakes** (regex vs prefix vs exact) → wrong block serves the request; reloading without **`nginx -t`** first.
- Reverse-proxying **without `Host`/`X-Forwarded-*`** headers (apps see wrong IP/host/proto); missing WebSocket upgrade headers (HA/sockets break).
- Exposing apps over **plain HTTP**; weak/old TLS (`ssl_protocols` including TLSv1.0/1.1); no HTTP→HTTPS redirect.
- Exposing **admin/management paths** to the internet without `allow`/`deny`/auth/VPN ([[network-security]]); no rate limiting on login/API.
- Serving an SPA without the `try_files … /index.html` fallback; no gzip/caching (wasted bandwidth).
- Running everything in one monolithic config (use `include`); over-reaching for OpenResty/Lua when stock directives suffice.

## Always-apply

1. Understand the **context tree** and **location precedence**; always `nginx -t` before a graceful reload.
2. As a reverse proxy: forward **Host + X-Forwarded-*** (and WebSocket upgrade headers); tune buffering/timeouts.
3. **Terminate TLS** (Let's Encrypt, TLS 1.2/1.3, HTTP/2, HTTP→HTTPS redirect, HSTS); never expose apps over plain HTTP.
4. **Load-balance** backends (least_conn/ip_hash + health checks); **gzip + caching** for performance.
5. **Rate-limit and restrict** sensitive paths; keep config modular; log and watch 4xx/5xx + upstream latency.

## Related

- [[nodejs]] / [[nextjs]] — app servers Nginx fronts (TLS, static, load balancing, WebSockets).
- [[home-assistant]] — reverse-proxy HA with TLS + WebSocket upgrade (secure remote access).
- [[docker]] — Nginx as a container / sidecar; [[devops]] / [[site-reliability-engineering]] — deployment, scaling, logs.
- [[network-security]] — TLS, rate limiting, access control, exposure; [[secure-coding]] — security headers, hardening.
- Sources: *Nginx HTTP Server, 2nd ed.* (Clément Nedelcu); *Nginx Module Extension* (Usama Dar).
