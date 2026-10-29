"""Part 4 – Scaling & performance; Part 5 – Authentication & security; closing appendix."""
from base import *
from svg import *
import charts as C


def d_scale_stages():
    d = S(900, 380)
    st = [("0 · Demo / staging", "Render free\n1 container, 1 DB", "Today", GREEN, 70),
          ("1 · Pilot", "Render paid\n+ disk or S3\npaid Postgres", "next", INDIGO, 130),
          ("2 · Launch", "AWS Mumbai\n2 web + 2 api tasks\nMulti-AZ RDS · Redis · S3", "plan (A-05)", VIOLET, 195),
          ("3 · Growth", "Autoscale web ≤ 6\napi ≤ 8 · worker ≤ 4\nread replica for reports", "plan (N-03)", AMBER, 260),
          ("4 · Headroom", "10,000 registered\nbigger RDS · CDN for\nvideo · job queue", "design headroom", ROSE, 325)]
    for i, (t, s, tag, col, h) in enumerate(st):
        x = 20 + i * 175
        d.rect(x, 340 - h, 160, h, col, col, 8, op=.92)
        d.text(x + 80, 340 - h + 20, t, 12.5, WHITE, 700)
        d.text(x + 80, 340 - h + 20 + 34, s, 10.2, WHITE, 500)
        d.pill(x + 30, 346, 100, 20, tag, "#F4F5F9", col, 9.5)
    d.arrow([(24, 30), (860, 30)], MUTED, sw=2); d.text(440, 14, "Capacity and resilience grow with each stage", 11, MUTED, italic=True)
    return d.svg()


def d_stateless():
    d = Flow(900, 330)
    d.node("lb", 10, 120, 110, 70, "Load\nbalancer", "ext", size=13)
    for i in range(3):
        d.node(f"w{i}", 190, 30 + i * 100, 140, 60, f"API replica {i+1}", "api", sub="no local state", size=12)
        d.link("lb", f"w{i}", color=INDIGO, mode="h")
        d.node(f"o{i}", 360, 30 + i * 100, 140, 60, "outbox loop", "warn", sub="SKIP LOCKED", size=11)
    d.node("db", 560, 100, 150, 110, "PostgreSQL", "db", "db", size=13)
    d.node("rc", 760, 40, 120, 70, "Redis\n(planned)", "ext", sub="auth cache", size=12)
    d.node("s3", 760, 190, 120, 70, "S3 / CDN\n(planned)", "ext", sub="media", size=12)
    for i in range(3): d.link(f"o{i}", "db", color=TEAL, mode="h") if False else None
    for i in range(3): d.link(f"w{i}", "db", color=TEAL, mode="h", off=0) if i == 1 else None
    d.arrow([(330, 60), (560, 130)], TEAL); d.arrow([(330, 260), (560, 180)], TEAL)
    d.arrow([(710, 130), (760, 80)], VIOLET, "4,3"); d.arrow([(710, 180), (760, 220)], VIOLET, "4,3")
    d.text(300, 316, "Any replica can serve any request: identity lives in the database-backed session row, not in memory.", 11, MUTED, italic=True)
    return d.svg()


def d_layers():
    d = S(900, 420)
    rings = [("EDGE", "CloudFront · WAF rate rules · TLS 1.2+ · HSTS (target)", 20, "ext"),
             ("WEB", "Same-origin cookies · SameSite=Lax · security headers · no tokens in JS", 90, "ui"),
             ("API", "CSRF double-submit · request id · Pydantic validation · RFC 7807 errors", 160, "api"),
             ("IDENTITY", "OTP · password + TOTP · JWT purpose-bound · rotating refresh · session revocation", 230, "warn"),
             ("AUTHORISATION", "RBAC deny-by-default · entitlements per subject · ownership checks", 300, "ok"),
             ("DATA & AUDIT", "Argon2id · hashed secrets · hash-chained audit log · consent ledger", 370, "bad")]
    for t, s, y, k in rings:
        f, st, tx = KIND[k]
        d.rect(30 + (y - 20) * 0.12, y - 8 + 8, 840 - (y - 20) * 0.24, 56, f, st, 10)
        d.text(150 + (y - 20) * .12, y + 20, t, 12.5, tx, 800)
        d.text(560, y + 20, s, 11.8, INK, 500)
    return d.svg()


def d_otp_seq():
    return seq([("b", "Browser", "ui"), ("api", "FastAPI", "api"), ("db", "PostgreSQL", "db"), ("sms", "SMS", "ext")], [
        ("b", "api", "POST /auth/otp/request {mobile}"), ("api", "db", "count codes this hour (limit 5) · store sha256(id:code)"), ("api", "sms", "Send code (never stored in plain text)"),
        ("api", "b", "challenge_id (+ debug_code in dev only)", "dash"), ("b", "api", "POST /auth/otp/verify {challenge_id, code}"),
        ("api", "db", "attempts+1 · constant-time compare · mark consumed"), ("api", "db", "User exists? → create sessions row (family_id, refresh hash)"),
        ("api", "b", "Set-Cookie: access_token · refresh_token · csrf_token", "dash"), ("b", "api", "later: any call with cookie (+ X-CSRF-Token on writes)")], 900, step=38)


def d_refresh_seq():
    return seq([("b", "Browser", "ui"), ("api", "FastAPI", "api"), ("db", "sessions row", "db")], [
        ("b", "api", "API call → 401 token_expired (access token is 15 min)"), ("b", "api", "POST /auth/refresh  (refresh cookie, path /api/v1/auth)"),
        ("api", "db", "find row by sha256(refresh_token)"), ("api", "db", "prev ← current hash · current ← sha256(new token)"),
        ("api", "b", "new access + refresh + csrf cookies", "dash"), ("b", "b", "retry original call once"),
        ("b", "api", "attacker replays the OLD refresh token", "dash"), ("api", "db", "matches prev_refresh_token_hash → revoke session (reuse_detected)"),
        ("api", "b", "401 · both parties must sign in again", "dash")], 900, step=38)


def d_authz():
    d = Flow(900, 190)
    st = [("Cookie / Bearer\npresent?", "dia", "warn"), ("JWT signature,\nexpiry, purpose=access", "box", "api"), ("sessions row\nexists, not revoked", "box", "api"), ("user status\nactive?", "dia", "warn"),
          ("role → permission\nset has required?", "dia", "warn"), ("entitlement for\nthis subject?", "dia", "warn"), ("Handler runs", "pill", "ok")]
    x = 6
    for i, (t, sh, k) in enumerate(st):
        d.node(f"a{i}", x, 50, 120, 90, t, k, sh, size=10.8); x += 128
    for i in range(6): d.link(f"a{i}", f"a{i+1}", color=INDIGO, mode="h")
    for i, t in [(1, "401"), (3, "401 / 403 guardian"), (4, "403"), (5, "403 not_entitled")]:
        d.text(6 + 128 * i + 60, 165, t, 10.5, ROSE, 700)
    d.text(6 + 128 * 0 + 60, 165, "401", 10.5, ROSE, 700); d.text(6 + 128 * 2 + 60, 165, "401", 10.5, ROSE, 700)
    return d.svg()


def d_signed_media():
    return seq([("c", "Candidate UI", "ui"), ("api", "FastAPI", "api"), ("fs", "Storage", "db")], [
        ("c", "api", "GET /resources/{id}/playback"), ("api", "api", "session + entitlement for the LM's subject"),
        ("api", "c", "url = /media/stream/<JWT purpose=media, 2 h> + watermark text", "dash"),
        ("c", "api", "GET stream URL (video element, Range requests)"), ("api", "fs", "verify token → read file (path-traversal guarded)"),
        ("api", "c", "206/200 + Cache-Control: private", "dash")], 900, step=40)


def build():
    o = []
    # ======================================================== PART 4
    o.append(h1("4", "Scaling & performance", "Workload assumptions, objectives, how the code scales today, known limits and the roadmap."))
    o.append(callout("warn", "Targets, models and measurements", "No load test has been run against this build yet (the plan, N-04, is documented). Everything in this part is therefore one of: a <b>requirement</b> from the NFR specification (N-01), a <b>design</b> from the infrastructure document (A-05), a <b>mathematical model</b> built from those assumptions and from real settings in the code, or a <b>fact</b> read from the code. Each is labelled."))
    o.append(h2("4.1", "Workload assumptions"))
    o.append(table(["Parameter", "Value", "Kind"], [
        ["Registered students", "2,000 in year 1; design headroom to 10,000", "Requirement (N-01)"], ["Daily active students", "600", "Requirement"],
        ["Peak concurrent users", "300 (evening 20:00–23:00 IST, batch start); 500 at contest start", "Requirement"],
        ["Peak API request rate", "≈150 req/s at 300 users (≈0.5 req/s per user, heartbeats dominate)", "Requirement"],
        ["Content", "56 LMs, ≈200 h video, ≈1,000 PDFs/notes, 5,000 questions by end of phase 2", "Requirement"],
        ["Data growth", "≈5 GB / year relational", "Requirement"], ["Required headroom", "3× peak = 900 users ≈ 450 req/s for 30 minutes with latency SLO met", "Requirement (N-01 §4)"]], widths=["26%", "54%", "20%"]))
    o.append(fig(C.capacity_curve(), "Workload model derived from the N-01 assumption. The three marked points are the planning milestones."))
    o.append(h2("4.2", "Service-level objectives"))
    o.append(fig(C.slo_chart(), "Latency objectives (requirements)."))
    o.append('<div class="grid2"><div>' + table(["SLO", "Target"], [
        ["SLO-1 Availability", "99.5% monthly (≈3 h 39 min budget)"], ["SLO-2 API read latency", "p95 ≤ 400 ms · p99 ≤ 1 s"], ["SLO-3 Writes", "progress p95 ≤ 300 ms · submit ≤ 1 s"],
        ["SLO-4 Page experience", "LCP p75 ≤ 2.5 s · INP ≤ 200 ms · CLS ≤ 0.1"], ["SLO-5 End-to-end action", "p95 ≤ 2 s"], ["SLO-6 Video start", "p90 ≤ 3 s"],
        ["SLO-7 Durability", "no acknowledged write lost"], ["SLO-8 OTP delivery", "≥ 97% within 30 s"]], "tight") + "</div><div>" + C.availability_chart() + "</div></div>")
    o.append(table(["Reliability item", "Target"], [["RPO / RTO (AZ failure)", "≈ 0 / ≤ 5 min (Multi-AZ, automatic)"], ["RPO / RTO (region)", "≤ 15 min / ≤ 4 h (runbook)"],
                                                    ["Backups", "PITR 14 days; daily snapshots 35 days; cross-region copy; quarterly restore test"], ["Deploys", "Zero-downtime rolling; expand/contract migrations"]], "tight", ["30%", "70%"]))
    o.append(h2("4.3", "How the code is built to scale"))
    o.append(fig(d_stateless(), "Stateless API tier. Replicas share nothing in memory, so adding capacity is a configuration change.", wide=True))
    o.append(table(["Technique", "Fact in the code", "Effect"], [
        ["Stateless requests", "Sessions are rows in PostgreSQL; the JWT carries only ids", "Any replica serves any request; no sticky sessions"],
        ["Async I/O", "FastAPI + asyncpg + async SQLAlchemy", "One worker holds many in-flight requests while waiting on the database"],
        ["Connection pooling", "<code>pool_size=10</code> (+10 default overflow), <code>pool_pre_ping</code>", "Bounded DB concurrency per process; stale connections are replaced"],
        ["One transaction per request", "<code>get_session()</code> commits once or rolls back", "Short, predictable lock windows"],
        ["Cheap list endpoints", "Hard <code>limit</code> caps; LM topics and course subjects use <code>selectin</code> eager loading", "Avoids N+1 queries (budget ≤ 10 queries per request)"],
        ["Indexes on hot paths", "user_id on every user-owned table; due_on on card_reviews; status on questions and attempts; (user, subject, ends_at) on entitlements", "Dashboard, quiz draw and access checks stay index-driven"],
        ["Idempotent writes", "Webhook unique key; payment applied once; revision once per day", "Retries and duplicate clicks are harmless"],
        ["Multi-replica background work", "Outbox dispatch uses <code>SKIP LOCKED</code>", "No leader election needed"],
        ["Range-capable media", "<code>FileResponse</code> with browser Range seeking and 1-hour private cache", "Seeking in video without re-download; moves behind a CDN later"]], widths=["22%", "44%", "34%"]))
    o.append(fig(C.littles_law(), "Model: with a pool of 10 connections and ~40 ms of connection time per request, one API process tops out near 250 req/s, comfortably above the 150 req/s planning peak but below the 450 req/s headroom goal, which is why two or more replicas are planned.", wide=True))
    o.append('<div class="grid2"><div>' + C.scaling_ranges() + "</div><div>" + table(["Tier", "Today", "Target scaling rule"], [
        ["Web", "1 process", "2–6 tasks · CPU 60%"], ["API", "1 process", "2–8 tasks · CPU 60% + requests per target"], ["Worker", "in-process loop", "1–4 · queue depth"],
        ["Database", "Render PG", "t4g.medium Multi-AZ → xlarge → read replica at CPU > 60%"], ["Cache", "none", "Redis primary + replica"]], "tight") + "</div></div>")
    o.append(h2("4.4", "Known limits and bottlenecks"))
    o.append(p("Honest list of what would limit growth, ordered by when it would bite."))
    o.append(table(["#", "Area", "Today", "Risk", "Planned remedy"], [
        ["1", "Media on local disk", "Files stored under <code>backend/var/storage</code>", "Ties the API to one machine; lost on redeploy on Render free; heavy video traffic competes with API CPU", "S3 + CloudFront signed URLs (A-05); storage interface already abstracts this"],
        ["2", "Auth lookups", "Each request loads the session row and the user row", "2 extra queries per call at 150–450 req/s", "Short-TTL Redis cache keyed by session id; revocation clears the key"],
        ["3", "Global audit lock", "<code>pg_advisory_xact_lock</code> serialises every audit write to keep the hash chain linear", "Throughput ceiling for audited actions (logins, orders, publishing); not hit by reads or autosave", "Acceptable at launch volumes; shard the chain per day or per actor if audited writes exceed hundreds/s"],
        ["4", "Progress heartbeats", "Watched intervals merged in JSONB on each ping", "Write amplification at 300 concurrent viewers", "Client-side batching (send every 15–30 s); already within the 20 req/s heartbeat budget"],
        ["5", "Search", "ILIKE on titles plus <code>to_tsvector</code> computed at query time; pg_trgm installed, no GIN index yet", "Sequential scans as notes grow into the thousands", "Add GIN index on a stored tsvector column and trigram index on titles"],
        ["6", "Reports", "Progress report computed synchronously", "Slow query at 10,000 students", "Run as job or on read replica (N-03)"],
        ["7", "Rate limiting", "Per-destination OTP limit only", "No generic per-IP or per-user throttle inside the app", "WAF rate rules on <code>/api/v1/auth/*</code>; add middleware limiter backed by Redis"],
        ["8", "Question draw", "Eligible pool loaded in Python then sampled", "O(pool) per quiz start; fine for 5,000 questions", "Push sampling into SQL if the bank grows 10×"],
        ["9", "Single instance", "One container on Render", "No redundancy; cold start on free plan", "Stage 1–2 of the roadmap"]], "tight", ["4%", "14%", "26%", "28%", "28%"]))
    o.append(h2("4.5", "Scaling roadmap"))
    o.append(fig(d_scale_stages(), "Staged path from demo to headroom for 10,000 registered students. Stages 2–4 are planned designs.", wide=True))
    o.append(h2("4.6", "Performance budgets and verification"))
    o.append(table(["Budget (N-01 §3)", "Limit", "How it is checked"], [
        ["JS shipped on student routes (gzip, first load)", "≤ 180 KB", "Lighthouse CI on pull requests (planned)"], ["Fonts", "Figtree subset WOFF2 ≤ 120 KB", "Build check"],
        ["DB queries per API request", "≤ 10", "N+1 detector in tests with SQLAlchemy event counters (planned)"], ["DB statement timeout (API role)", "5 s", "Role setting; long reports run as jobs"],
        ["API payload", "≤ 200 KB typical; lists ≤ 200 items", "Schema review"], ["Load test", "3× peak for 30 min with SLO-2 met", "N-04 plan, not yet executed"]], "tight", ["36%", "26%", "38%"]))

    # ======================================================== PART 5
    o.append(h1("5", "Authentication & security", "Every credential, token and control that protects candidates, staff and money."))
    o.append(h2("5.1", "Defence in depth"))
    o.append(fig(d_layers(), "Six layers. A request must pass each one; a failure at any layer stops it.", wide=True))
    o.append(h2("5.2", "Catalogue of authentication mechanisms"))
    o.append(table(["#", "Mechanism", "Used by", "How it works", "Key parameters"], [
        ["1", "Mobile OTP", "Candidates", "6-digit random code; stored as sha256(challenge_id:code); destination stored only as a keyed HMAC", "5 min TTL · 5 requests/h · 5 guesses · single use"],
        ["2", "Email OTP", "Candidates (API-ready)", "Same engine, channel = email", "same"],
        ["3", "Password + TOTP", "Staff", "Argon2id password, then RFC 6238 authenticator code (±1 step window)", "5 fails → 15 min lock · TOTP mandatory outside dev"],
        ["4", "Signup token", "New candidates", "JWT <code>purpose=signup</code> proves the verified mobile until the form is submitted", "20 min"],
        ["5", "MFA step-up token", "Staff", "JWT <code>purpose=mfa</code> carries the user between password and TOTP", "5 min"],
        ["6", "Access token", "Everyone signed in", "HS256 JWT in HttpOnly cookie <code>access_token</code>; carries sub, session id, roles; session row re-checked on every call", "15 min"],
        ["7", "Refresh token", "Everyone signed in", "Opaque random token, only its sha256 stored; rotated on every use; reuse of an old one revokes the session", "Student 30 d · staff 12 h"],
        ["8", "CSRF token", "Browser writes", "Double-submit: cookie <code>csrf_token</code> must equal header <code>X-CSRF-Token</code>", "per session"],
        ["9", "Guardian consent", "Parents of minors", "JWT link (<code>purpose=guardian</code>) plus the guardian's own OTP", "link 7 d · OTP 5 min"],
        ["10", "Signed media URL", "Video / PDF viewers", "JWT <code>purpose=media</code> bound to resource and user", "2 h"],
        ["11", "Checkout signature", "Payments", "Gateway signature verified server-side, then the payment is fetched from the gateway", "per payment"],
        ["12", "Webhook HMAC", "Gateway → API", "Razorpay signature on raw body; event id deduplicated", "per event"],
        ["13", "Event-sink HMAC", "API → partner service", "<code>x-event-signature</code> = HMAC-SHA256 of body with the secret key", "per event"]], "tight", ["4%", "15%", "14%", "43%", "24%"]))
    o.append(fig(C.lifetimes(), "Lifetimes of every token and credential, from the code's configuration.", wide=True))
    o.append(callout("key", "Purpose-bound tokens", "All JWTs share one signing key but carry a <code>pur</code> claim (access, signup, mfa, guardian, media). <code>decode_token(token, purpose)</code> rejects a token whose purpose differs, so a media link can never be used as an access token and vice versa."))
    o.append(h2("5.3", "Candidate sign-in sequence"))
    o.append(fig(d_otp_seq(), "OTP sign-in from request to cookies.", wide=True))
    o.append(h2("5.4", "Sessions, cookies and refresh rotation"))
    o.append(table(["Cookie", "HttpOnly", "Path", "SameSite", "Secure", "Purpose"], [
        ["<code>access_token</code>", "yes", "/", "Lax", "required outside dev", "Authenticates API calls"], ["<code>refresh_token</code>", "yes", "/api/v1/auth", "Lax", "required outside dev", "Only sent to the auth endpoints, so it is rarely exposed"],
        ["<code>csrf_token</code>", "no (read by JS)", "/", "Lax", "required outside dev", "Echoed in the X-CSRF-Token header"]], "tight", ["16%", "12%", "14%", "10%", "18%", "30%"]))
    o.append(fig(d_refresh_seq(), "Rotating refresh tokens with reuse detection. The previous token's hash is kept so a replay is recognised and the whole session is killed.", wide=True))
    o.append('<div class="grid2"><div>' + ul(["<b>Immediate revocation.</b> Because every request checks the <code>sessions</code> row, ending a session (logout, admin force sign-out, deactivation, erasure) takes effect on the very next call, not 15 minutes later.",
                                               "<b>Device limit.</b> Students may hold 2 live sessions; signing in on a third ends the oldest (BR-ACC-05). Staff are not limited but expire in 12 h.",
                                               "<b>Visible to the user.</b> Profile → Signed-in devices lists each session with device label and last seen."]) + "</div><div>" + C.lockouts() + "</div></div>")
    o.append(h2("5.5", "Authorisation"))
    o.append(fig(d_authz(), "The order of checks for a protected API call. Red text is the response when that step fails.", wide=True))
    o.append(ul(["<b>RBAC, deny by default.</b> Roles map to permissions in one file; endpoints declare <code>require('perm')</code>. A role not listed grants nothing.",
                 "<b>Entitlements</b> are the second gate for content: an LM, note, video, quiz or flashcard in a subject opens only when an active entitlement exists (granted by registration, batch or manual grant). Staff preview everything.",
                 "<b>Ownership checks.</b> Attempts, orders, bookmarks, sessions and data exports are always filtered by the caller's user id; a wrong id returns 404, not 403, so ids cannot be probed.",
                 "<b>Separation of duties.</b> Authors cannot publish; reviewers cannot edit commerce; only super admins assign admin roles."]))
    o.append(fig(d_signed_media(), "Protecting paid content: a short-lived signed URL, a visible watermark and no download unless allowed."))
    o.append(h2("5.6", "How credentials are stored"))
    o.append(table(["Secret", "Stored as", "Notes"], [
        ["Staff password", "Argon2id · time 3 · memory 64 MiB · parallelism 2", "argon2-cffi; verify is constant-time; generic error for unknown user and wrong password"],
        ["OTP code", "sha256(challenge_id : code)", "Plain code exists only in the SMS"], ["OTP destination", "HMAC-SHA256 keyed with SECRET_KEY", "Rate-limit counts without storing the number"],
        ["Refresh token", "sha256 of 256-bit random value", "Database leak cannot be replayed"], ["TOTP secret", "base32 bytes in <code>users.totp_secret</code>", "Never returned by the API; KMS envelope encryption is a TODO for the cloud move"],
        ["JWT signing key", "<code>SECRET_KEY</code> environment variable, ≥ 32 chars", "Start-up refuses the default key outside dev"], ["Gateway secrets", "Environment variables (Secrets Manager in target)", "Never logged or stored in the database"]], "tight", ["22%", "40%", "38%"]))
    o.append(h2("5.7", "Integrity, audit and privacy controls"))
    o.append(ul(["<b>Hash-chained audit log.</b> Each row stores <code>hash = SHA-256(previous hash + canonical row)</code>. <code>GET /admin/audit/verify</code> recomputes the chain; any edited or deleted row breaks every later hash. Writes are serialised with an advisory lock.",
                 "<b>What is audited.</b> Sign-in and failures, lockouts, MFA enrolment, session revocation, user and role changes, orders, payments, refunds, mismatches, content and question publishing, resource uploads, consents, data requests and erasure.",
                 "<b>Consent ledger.</b> Append-only rows with notice version, actor (self or guardian), method, IP and user agent.",
                 "<b>Erasure.</b> Personal fields are overwritten and progress rows deleted; orders are kept as business records with the user pseudonymised.",
                 "<b>Start-up guard rails.</b> Outside local/test the server refuses to run unless COOKIE_SECURE and STAFF_MFA_REQUIRED are on and SECRET_KEY is changed; DEMO_MODE and on-screen OTP are blocked in production."]))
    o.append(h2("5.8", "Threats and the controls that answer them"))
    o.append(table(["Threat", "Control in this build", "Status"], [
        ["Password guessing (staff)", "Argon2id, 5-fail lock for 15 min, MFA, generic errors, audit of failures", "In place"],
        ["OTP abuse / SMS bombing", "5 codes/h per destination, 5 guesses, 5-min TTL; WAF rule planned", "In place · edge rule planned"],
        ["Token theft via XSS", "HttpOnly cookies, short access token, nosniff, same-origin only", "In place · CSP header not yet set"],
        ["Cross-site request forgery", "SameSite=Lax cookies plus double-submit CSRF header on writes", "In place"],
        ["Refresh-token replay", "Rotation with previous-hash reuse detection", "In place"],
        ["Payment tampering", "Server-side signature, gateway fetch, amount match, idempotent apply, webhook dedupe", "In place"],
        ["Content piracy", "Entitlement check, 2-hour signed URLs, watermark, download off by default", "In place · DRM not in scope"],
        ["Insecure object references", "Owner-scoped queries, UUIDv7 ids, 404 for foreign objects", "In place"],
        ["SQL injection", "SQLAlchemy parameterised queries only", "In place"],
        ["Malicious upload", "MIME allow-list, PDF signature check, size cap, safe file names", "Partial · antivirus scan pending"],
        ["Insider tampering", "Hash-chained audit with verify endpoint, separation of duties", "In place"],
        ["Minor's data", "Guardian consent gate before registration and learning", "In place"]], "tight", ["24%", "52%", "24%"]))
    o.append(h2("5.9", "Gaps and hardening backlog"))
    o.append(p("These are visible in the code today and should be closed before real students and live payments."))
    o.append(table(["Priority", "Gap", "Why it matters", "Fix"], [
        ["High", "SMS and email adapters are console-only (<code>NotImplementedError</code> for MSG91 / SES)", "No real OTP can be delivered; demo mode shows codes on screen", "Implement MSG91 and SES adapters, then set OTP_DEBUG_ECHO=false and DEMO_MODE=false"],
        ["High", "Razorpay keys and webhook not yet connected", "Payments run on the mock gateway", "Set PAYMENT_PROVIDER=razorpay, three keys, register the webhook URL"],
        ["High", "TOTP secrets not envelope-encrypted", "Database leak would expose second-factor seeds", "KMS-encrypt at rest (documented TODO)"],
        ["Medium", "No Content-Security-Policy header; HSTS expected from the edge", "Lower XSS defence in depth", "Add CSP in Next.js headers and HSTS at CloudFront"],
        ["Medium", "TOTP codes can be reused inside their time window", "Replay by someone who observes the code within ~60 s", "Store last accepted time-step per user"],
        ["Medium", "Single HS256 key without rotation id", "Rotating the key logs everyone out; compromise affects all tokens", "Use key id (kid) with two active keys, or move to asymmetric signing"],
        ["Medium", "No generic API rate limit in the application", "Scraping and abuse of expensive endpoints", "WAF rate rules and Redis-backed middleware"],
        ["Medium", "Antivirus scan on uploads not implemented", "Infected PDF could reach students", "ClamAV job before publish (S-01 T-08)"],
        ["Low", "Free-plan storage is ephemeral", "Uploaded files vanish on redeploy", "Disk mount or S3"]], "tight", ["8%", "30%", "30%", "32%"]))
    o.append(h2("5.10", "Appendix · source map"))
    o.append(table(["Topic", "File"], [
        ["Token and crypto helpers", "<code>backend/app/core/security.py</code>"], ["OTP, sessions, staff login, TOTP", "<code>backend/app/modules/auth/service.py</code>"],
        ["Permission mapping", "<code>backend/app/core/rbac.py</code>"], ["Auth dependencies", "<code>backend/app/core/deps.py</code>"], ["CSRF and request context", "<code>backend/app/core/middleware.py</code>"],
        ["Settings and guard rails", "<code>backend/app/core/config.py</code>"], ["Audit chain", "<code>backend/app/modules/audit/service.py</code>"], ["Payments", "<code>backend/app/modules/payments/service.py</code>"],
        ["Access ledger", "<code>backend/app/modules/enrolment/service.py</code>"], ["Tests engine", "<code>backend/app/modules/qbank/service.py</code>"], ["Spaced repetition", "<code>backend/app/modules/flashcards/service.py</code>"],
        ["API client (CSRF + refresh)", "<code>frontend/src/lib/api.ts</code>"], ["Proxy and headers", "<code>frontend/next.config.ts</code>"], ["Deployment", "<code>render.yaml</code> · <code>Dockerfile</code> · <code>deploy/start.sh</code>"],
        ["Design documents", "<code>Documentation/</code> (A-01…A-08 architecture, S-01…S-03 security, N-01 NFRs, P-xx product)"]], "tight", ["34%", "66%"]))
    return "".join(o)
