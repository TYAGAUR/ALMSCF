"""Part 2 – Backend & architecture; Part 3 – APIs, database, UI mapping."""
from base import *
from svg import *
import charts as C

F = C.F


# ============================================================ PART 2 diagrams
def d_stack():
    d = S(900, 440)
    layers = [("CLIENT", "Browser · React 19 UI · cookies only, no tokens in JavaScript", "ui", 20),
              ("WEB TIER", "Next.js 16 (Node) · server-rendered shell · rewrites /api/* → FastAPI · security headers", "ui", 100),
              ("API TIER", "FastAPI · Pydantic 2 validation · middleware · RBAC dependencies · services per module", "api", 180),
              ("DATA ACCESS", "SQLAlchemy 2 async ORM · asyncpg driver · pool 10 (+10 overflow) · Alembic migrations", "api", 260),
              ("STORAGE", "PostgreSQL 16 (JSONB · CITEXT · INET · advisory locks)   ·   Local disk / S3 for media", "db", 340)]
    for t, s, k, y in layers:
        f, st, tx = KIND[k]
        d.rect(20, y, 860, 66, f, st, 12)
        d.pill(34, y + 10, 118, 22, t, st, WHITE, 10)
        d.text(460, y + 46, s, 12.5, INK, 500)
    d.arrow([(450, 86), (450, 100)], MUTED); d.arrow([(450, 166), (450, 180)], MUTED); d.arrow([(450, 246), (450, 260)], MUTED); d.arrow([(450, 326), (450, 340)], MUTED)
    d.rect(20, 416, 860, 20, "#F4F5F9", LINE, 6)
    d.text(450, 427, "Cross-cutting: argon2-cffi · PyJWT · pyotp · httpx (gateway, events) · pydantic-settings · uvicorn", 10.5, MUTED)
    return d.svg()


def d_modules():
    d = S(900, 470)
    d.rect(10, 10, 880, 90, "#F4F5F9", LINE, 12)
    d.text(24, 26, "PLATFORM CORE  ·  app/core", 11, MUTED, 800, anchor="start")
    core = ["config", "db · uow", "deps · rbac", "security", "errors", "events · outbox", "middleware", "storage", "notify"]
    for i, c in enumerate(core): d.box(22 + i * 96, 42, 88, 44, c, "grey", 10.5)
    doms = [("Identity", 14, 120, "ui", ["auth", "users"]), ("Learning", 232, 120, "api", ["catalog", "content", "media", "learning", "progress"]),
            ("Assessment", 450, 120, "warn", ["qbank", "flashcards"]), ("Commerce", 668, 120, "ok", ["commerce", "payments", "enrolment"])]
    for t, x, y, k, mods in doms:
        f, st, tx = KIND[k]
        d.rect(x, y, 208, 230, "#FAFBFF", st, 12)
        d.pill(x + 14, y + 10, 180, 22, t.upper(), st, WHITE, 10.5)
        for i, m in enumerate(mods): d.box(x + 14, y + 44 + i * 36, 180, 30, m, k, 12)
    d.rect(14, 366, 874, 92, "#FAFBFF", ROSE, 12)
    d.pill(28, 376, 220, 22, "GOVERNANCE & OPERATIONS", ROSE, WHITE, 10.5)
    for i, (m, s) in enumerate([("privacy", "consent · requests"), ("audit", "hash-chained log"), ("admin/users", "users · batches"), ("admin/catalog", "content CRUD"),
                                ("admin/commerce", "courses · orders"), ("admin/ops", "reports · audit")]):
        d.box(28 + i * 143, 408, 134, 40, m, "bad", 11, sub=s)
    return d.svg()


def d_request():
    d = Flow(900, 330)
    steps = [("Browser", "fetch /api/v1/…\ncookie + X-CSRF-Token", "ui"), ("Next.js", "rewrite to\n127.0.0.1:8000", "ui"), ("Middleware", "request-id · client IP\nCSRF double-submit", "api"),
             ("Route + Pydantic", "path, query, body\nvalidation → 422", "api"), ("Dependencies", "JWT → session row\n→ user → permissions", "warn"),
             ("Service", "business rules\nentitlement checks", "api"), ("Unit of work", "one transaction\ncommit / rollback", "db")]
    x = 8
    for i, (t, s, k) in enumerate(steps):
        d.node(f"n{i}", x, 40 + (i % 2) * 120, 118, 80, t, k, sub=s, size=11.5)
        x += 126
    for i in range(6): d.link(f"n{i}", f"n{i+1}", color=INDIGO, mode="h")
    d.node("aud", 560, 250, 160, 56, "Audit + outbox\n(same transaction)", "bad", size=11.5)
    d.node("resp", 740, 250, 150, 56, "Response headers\nx-request-id · nosniff", "ok", size=11)
    d.link("n5", "aud", None, ROSE, mode="v"); d.link("aud", "resp", None, GREEN, mode="h")
    d.text(30, 280, "Any exception → rollback → RFC 7807 problem+json\n{type,title,status,code,detail,request_id,errors[]}", 11, MUTED, anchor="start", italic=True)
    return d.svg()


def d_events():
    d = Flow(900, 250)
    d.node("a", 10, 90, 150, 70, "Service calls\npublish(topic, payload)", "api", size=12)
    d.node("b", 230, 30, 190, 64, "In-process subscribers", "ok", sub="same transaction")
    d.node("c", 230, 150, 190, 64, "outbox row", "db", sub="same transaction")
    d.node("d", 490, 150, 170, 64, "Dispatcher loop", "warn", sub="every 2 s · SKIP LOCKED")
    d.node("e", 730, 150, 150, 64, "Event sink (HTTP)", "ext", sub="HMAC-SHA256 header")
    d.node("f", 490, 30, 390, 64, "order_paid → activate registration → grant entitlements\norder_refunded (full) → cancel registration, revoke access", "ok", size=11.5)
    d.link("a", "b", color=GREEN); d.link("a", "c", color=AMBER); d.link("b", "f", color=GREEN, mode="h"); d.link("c", "d", color=AMBER); d.link("d", "e", "retry on failure", VIOLET)
    return d.svg()


def d_deploy_now():
    d = Flow(900, 440)
    d.node("br", 10, 160, 120, 70, "Browser", "ui", size=14)
    d.rect(180, 20, 500, 400, "#FAFBFF", INDIGO, 14, dash="6,4")
    d.pill(196, 32, 320, 22, "RENDER WEB SERVICE · DOCKER · SINGAPORE", INDIGO, WHITE, 10)
    d.node("sh", 200, 70, 460, 56, "deploy/start.sh  (PID 1, restarts container if either process dies)", "grey", size=12)
    d.node("m", 200, 150, 220, 56, "1 · alembic upgrade head", "db", size=12)
    d.node("sd", 440, 150, 220, 56, "2 · seed.py (SEED_ON_START)", "db", size=12)
    d.node("nx", 200, 240, 220, 70, "Next.js standalone", "ui", sub="public $PORT 10000", size=13)
    d.node("fa", 440, 240, 220, 70, "uvicorn FastAPI", "api", sub="127.0.0.1:8000 · proxy headers", size=13)
    d.node("vol", 440, 340, 220, 56, "backend/var/storage\n(ephemeral on free plan)", "warn", size=11)
    d.node("pg", 740, 240, 140, 90, "Render Postgres 16\ncfa-lms-db", "db", "db", size=12)
    d.node("rz", 740, 100, 140, 60, "Razorpay /\nmock gateway", "ext", size=12)
    d.link("br", "nx", "HTTPS", INDIGO, mode="h", lpos=(155, 160)); d.link("nx", "fa", "/api/*", INDIGO, mode="h")
    d.link("fa", "pg", "asyncpg", TEAL, mode="h"); d.link("fa", "vol", None, AMBER, mode="v"); d.link("fa", "rz", None, VIOLET, mode="h")
    d.text(300, 405, "Health check: GET /api/v1/healthz · readiness: /api/v1/readyz (SELECT 1)", 11, MUTED, italic=True)
    return d.svg()


def d_build():
    d = Flow(900, 170)
    d.node("a", 10, 40, 200, 80, "Stage 1 · web", "ui", sub="node:24-slim · npm ci\nnext build (standalone)", size=13)
    d.node("b", 250, 40, 200, 80, "Stage 2 · api deps", "api", sub="python:3.12-slim + uv\nuv sync --frozen --no-dev", size=13)
    d.node("c", 490, 40, 400, 80, "Stage 3 · runtime image", "ok", sub="python:3.12-slim + node binary · user 'app' (non-root)\nCOPY .venv · backend · seed · .next/standalone", size=13)
    d.link("a", "c", "static + server", INDIGO, mode="h", lpos=(350, 30)); d.link("b", "c", None, TEAL, mode="h", off=20)
    return d.svg()


def d_aws():
    d = Flow(900, 520)
    d.node("u", 10, 220, 90, 60, "Users", "ui", "pill")
    d.node("r53", 120, 220, 90, 60, "Route 53", "ext", size=12)
    d.node("cf", 230, 220, 100, 60, "CloudFront", "ext", sub="TLS · HTTP/3", size=12)
    d.node("waf", 350, 220, 90, 60, "AWS WAF", "ext", sub="rate rules", size=12)
    d.node("alb", 460, 220, 90, 60, "ALB", "ext", size=13)
    d.rect(570, 20, 320, 480, "#FAFBFF", INDIGO, 14, dash="6,4")
    d.pill(584, 30, 230, 22, "VPC · PRIVATE SUBNETS · 2 AZ", INDIGO, WHITE, 10)
    d.node("web", 590, 70, 130, 70, "ECS web", "ui", sub="Next.js ×2–6", size=12)
    d.node("api", 740, 70, 130, 70, "ECS api", "api", sub="FastAPI ×2–8", size=12)
    d.node("wk", 590, 170, 130, 70, "ECS worker", "warn", sub="Celery ×1–4", size=12)
    d.node("av", 740, 170, 130, 70, "ClamAV", "bad", sub="upload scan", size=12)
    d.node("rds", 590, 290, 130, 80, "RDS PG 16\nMulti-AZ", "db", "db", size=11.5)
    d.node("rc", 740, 290, 130, 80, "ElastiCache\nRedis 7", "db", "db", size=11.5)
    d.node("s3", 590, 410, 280, 60, "S3 · media · exports · backups · logs (KMS, VPC endpoint)", "ok", size=11.5)
    for a, b in (("u", "r53"), ("r53", "cf"), ("cf", "waf"), ("waf", "alb")): d.link(a, b, color=INDIGO, mode="h")
    d.link("alb", "web", None, INDIGO, mode="h"); d.link("alb", "api", "/api/*", INDIGO, mode="h", off=14)
    d.link("api", "rds", None, TEAL, mode="v", off=-30); d.link("api", "rc", None, TEAL, mode="v"); d.link("wk", "rds", None, AMBER, mode="v", off=-20)
    d.link("api", "s3", None, OK if False else GREEN, mode="v", off=40)
    d.text(110, 330, "DR: encrypted backup copy in ap-south-2 (Hyderabad)\nRPO ≤ 15 min · RTO ≤ 5 min (AZ) / 4 h (region)", 11, MUTED, anchor="start", italic=True)
    d.text(110, 395, "Primary region ap-south-1 (Mumbai): data at rest stays in India", 11, MUTED, anchor="start", italic=True)
    return d.svg()


# ============================================================ PART 3 diagrams
def d_erd_a():
    d = S(900, 640)
    def tb(x, y, w, name, cols, kind):
        f, st, tx = KIND[kind]
        h = 30 + len(cols) * 17 + 6
        d.rect(x, y, w, h, WHITE, st, 6, 1.4)
        d.p.append(f'<path d="M{x},{y+6} a6,6 0 0 1 6,-6 h{w-12} a6,6 0 0 1 6,6 v18 h{-w} z" fill="{st}"/>')
        d.text(x + w / 2, y + 12, name, 12, WHITE, 700)
        for i, c in enumerate(cols):
            pk = c.startswith("*")
            d.text(x + 8, y + 40 + i * 17, ("🔑 " if False else "") + c.lstrip("*"), 10, INK if not pk else NAVY, 700 if pk else 400, anchor="start")
        return (x, y, w, h)
    T = {}
    T["users"] = tb(20, 20, 190, "users", ["*id  uuid7", "mobile_e164 · email (unique)", "student_code (unique)", "dob · is_minor · status", "password_hash (staff)", "totp_secret · mfa_enrolled_at", "failed_login_count · locked_until"], "ui" if False else "dark")
    T["roles"] = tb(20, 200, 190, "user_roles", ["*user_id → users", "*role  student|author|…", "granted_by → users"], "ui" if False else "dark")
    T["guard"] = tb(20, 285, 190, "guardians", ["*id", "student_user_id → users (1:1)", "mobile · relationship", "verified_at"], "dark")
    T["sess"] = tb(250, 20, 200, "sessions", ["*id  · family_id", "user_id → users", "refresh_token_hash (unique)", "prev_refresh_token_hash", "expires_at · revoked_at", "revoke_reason"], "ui" if False else "dark")
    T["otp"] = tb(250, 150, 200, "otp_challenges", ["*id", "destination_hash (HMAC)", "code_hash · attempts", "expires_at · consumed_at"], "dark")
    T["cons"] = tb(250, 245, 200, "consents", ["*id", "user_id → users", "purpose · granted", "notice_version · actor", "guardian_id → guardians"], "dark")
    T["dr"] = tb(250, 355, 200, "data_requests", ["*id", "user_id → users", "type · status · due_at", "handled_by → users"], "dark")
    T["course"] = tb(500, 20, 180, "courses", ["*id · code (unique)", "fee_paise · currency", "validity_days · access_ends_on", "seat_limit · status", "batch_id → batches"], "warn" if False else "db")
    T["cs"] = tb(500, 150, 180, "course_subjects", ["*course_id → courses", "*subject_id → subjects"], "db")
    T["reg"] = tb(500, 215, 180, "registrations", ["*id", "user_id → users", "course_id → courses", "status · form (JSONB)", "current_order_id", "uq: one open per user+course"], "db")
    T["ord"] = tb(710, 20, 170, "orders", ["*id · number (KSC-…)", "user_id → users", "purpose · reference_id", "amount_paise · status", "provider_order_id (uq)", "refunded_paise · notes"], "db")
    T["pay"] = tb(710, 165, 170, "payments", ["*id", "order_id → orders", "provider_payment_id (uq)", "status · method"], "db")
    T["pev"] = tb(710, 250, 170, "payment_events", ["*id", "uq(provider, event_id)", "payload · signature_valid"], "db")
    T["ref"] = tb(710, 335, 170, "refunds", ["*id", "order_id → orders", "payment_id → payments", "amount_paise · status"], "db")
    T["bat"] = tb(500, 360, 180, "batches", ["*id · code (unique)", "starts_on · ends_on", "status"], "db")
    T["enr"] = tb(500, 450, 180, "enrolments", ["*id", "uq(user_id, batch_id)", "user_id · batch_id"], "db")
    T["ent"] = tb(710, 450, 170, "entitlements", ["*id", "user_id → users", "subject_id → subjects", "source: registration|batch|grant", "starts_at · ends_at · revoked_at"], "db")
    T["sub"] = tb(250, 480, 200, "subjects", ["*id · code (unique)", "name · sort_order · status"], "ui" if False else "api")
    def ln(a, b, col=MUTED):
        ax, ay, aw, ah = T[a]; bx, by, bw, bh = T[b]
        p1 = (ax + aw, ay + ah / 2) if bx > ax else (ax, ay + ah / 2)
        p2 = (bx, by + bh / 2) if bx > ax else (bx + bw, by + bh / 2)
        d.arrow([p1, p2], col, sw=1.2)
    for a, b in [("roles", "users"), ("guard", "users"), ("sess", "users"), ("cons", "users"), ("dr", "users"), ("cons", "guard"), ("reg", "users"), ("reg", "course"), ("cs", "course"),
                 ("pay", "ord"), ("ref", "ord"), ("ord", "users"), ("ent", "users"), ("cs", "sub"), ("ent", "sub")]:
        ln(a, b, "#B0B7D6")
    d.text(20, 620, "Colour: navy = identity & privacy · amber = commerce & enrolment · teal = catalogue. Arrows point from the referencing table to the referenced table.", 10.5, MUTED, anchor="start", italic=True)
    return d.svg()


def d_erd_b():
    d = S(900, 620)
    def tb(x, y, w, name, cols, st):
        h = 30 + len(cols) * 17 + 6
        d.rect(x, y, w, h, WHITE, st, 6, 1.4)
        d.p.append(f'<path d="M{x},{y+6} a6,6 0 0 1 6,-6 h{w-12} a6,6 0 0 1 6,6 v18 h{-w} z" fill="{st}"/>')
        d.text(x + w / 2, y + 12, name, 12, WHITE, 700)
        for i, c in enumerate(cols):
            pk = c.startswith("*")
            d.text(x + 8, y + 40 + i * 17, c.lstrip("*"), 10, NAVY if pk else INK, 700 if pk else 400, anchor="start")
        return (x, y, w, h)
    T = {}
    T["sub"] = tb(20, 20, 170, "subjects", ["*id · code", "name · exam_weight"], TEAL)
    T["lm"] = tb(20, 110, 170, "learning_modules", ["*id", "subject_id → subjects", "lm_no · title · summary", "source_ref (internal)", "status · published_at"], TEAL)
    T["top"] = tb(20, 245, 170, "topics", ["*id", "lm_id → learning_modules", "title · sort_order", "los_ids (JSONB)"], TEAL)
    T["los"] = tb(20, 345, 170, "los", ["*id", "lm_id · code (uq)", "statement · command_word"], TEAL)
    T["ci"] = tb(235, 20, 190, "content_items", ["*id", "lm_id · topic_id", "kind · title", "current_published_version_id"], INDIGO)
    T["cv"] = tb(235, 120, 190, "content_versions", ["*id", "item_id → content_items", "uq(item_id, version_no)", "body (JSONB) · plain_text", "status · provenance", "author_id · reviewer_id"], INDIGO)
    T["res"] = tb(235, 255, 190, "resources", ["*id", "lm_id → learning_modules", "kind video|pdf|class_note|link", "storage_key · mime · size", "chapters (JSONB)", "status · downloadable"], INDIGO)
    T["fc"] = tb(235, 395, 190, "flashcards", ["*id", "subject_id · lm_id", "front · back · status"], VIOLET)
    T["cr"] = tb(235, 470, 190, "card_reviews", ["*user_id · *card_id", "ease · interval_days · due_on", "reps · lapses · last_rating"], VIOLET)
    T["q"] = tb(470, 20, 200, "questions", ["*id", "subject_id · lm_id · los_id", "stem · options[3] · correct_index", "explanation · difficulty E/M/H", "qtype · status · version", "author_id · reviewer_id"], VIOLET)
    T["ta"] = tb(470, 165, 200, "test_attempts", ["*id", "user_id · kind chapter|master|custom", "mode · timed · deadline_at", "status · submit_reason", "total · correct · score_pct"], VIOLET)
    T["ai"] = tb(470, 290, 200, "attempt_items", ["*attempt_id · *position", "question_id → questions", "snapshot (JSONB)", "answer_index · is_correct", "time_spent_s · flagged"], VIOLET)
    T["lp"] = tb(715, 20, 165, "lm_progress", ["*user_id · *lm_id", "learned_at", "learned_undo_until", "last_opened_at"], GREEN)
    T["rp"] = tb(715, 115, 165, "resource_progress", ["*user_id · *resource_id", "watched (JSONB intervals)", "last_position_s", "completed_at"], GREEN)
    T["rl"] = tb(715, 225, 165, "revision_logs", ["*id", "user_id · lm_id", "revised_on · counted", "uq per user, LM, day"], GREEN)
    T["eoc"] = tb(715, 325, 165, "eoc_entries", ["*user_id · *lm_id", "q_attempted · q_correct", "weak_topics"], GREEN)
    T["bm"] = tb(715, 415, 165, "bookmarks", ["*id · user_id", "target_type · target_id", "position_s · note"], GREEN)
    def ln(a, b):
        ax, ay, aw, ah = T[a]; bx, by, bw, bh = T[b]
        if abs(ax - bx) < 5: p1, p2 = (ax + aw / 2, ay if by < ay else ay + ah), (bx + bw / 2, by + bh if by < ay else by)
        else:
            p1 = (ax + aw, ay + ah / 2) if bx > ax else (ax, ay + ah / 2); p2 = (bx, by + bh / 2) if bx > ax else (bx + bw, by + bh / 2)
        d.arrow([p1, p2], "#B0B7D6", sw=1.2)
    for a, b in [("lm", "sub"), ("top", "lm"), ("los", "lm"), ("ci", "lm"), ("cv", "ci"), ("res", "lm"), ("q", "lm"), ("fc", "sub"), ("cr", "fc"), ("ai", "ta"), ("ai", "q"), ("rp", "res"), ("lp", "lm")]:
        ln(a, b)
    d.text(20, 600, "All user-owned rows reference users(id) with ON DELETE CASCADE; only orders and courses are RESTRICT so financial history survives. Colours: teal = catalogue · indigo = content · violet = assessment · green = progress.", 10, MUTED, anchor="start", italic=True)
    return d.svg()


def d_seq_test():
    return seq([("ui", "Candidate UI", "ui"), ("api", "FastAPI", "api"), ("en", "Entitlement", "warn"), ("db", "PostgreSQL", "db")], [
        ("ui", "api", "POST /lms/{id}/quiz"), ("api", "en", "assert_entitled(subject)"), ("api", "db", "SELECT published questions (unseen first)"),
        ("api", "db", "INSERT test_attempts + attempt_items (snapshot)"), ("api", "ui", "attempt without answer keys", "dash"),
        ("ui", "api", "PUT /attempts/{id}/items/{n}  (autosave)"), ("api", "db", "UPDATE answer · time_spent (≤ 600 s)"),
        ("ui", "api", "POST /attempts/{id}/submit"), ("api", "db", "grade from snapshot · score_pct · audit"), ("api", "ui", "result + explanations", "dash")], 900, step=38)


# ============================================================ endpoint descriptions
DESC = {
    "POST /auth/otp/request": "Send a 6-digit code to a mobile or email", "POST /auth/otp/verify": "Check the code; sign in or return a signup token",
    "POST /auth/signup": "Create the student account and start a session", "POST /auth/staff/login": "Staff email + password; returns MFA step",
    "POST /auth/staff/mfa/setup": "First-time TOTP secret and otpauth URI", "POST /auth/staff/mfa": "Verify TOTP and start a staff session",
    "POST /auth/refresh": "Rotate refresh token, issue new access token", "POST /auth/logout": "End the current session",
    "GET /me": "Current user with permission list", "PATCH /me": "Update own profile", "GET /me/sessions": "List signed-in devices", "DELETE /me/sessions/{session_id}": "End one of my sessions",
    "GET /privacy/notice/current": "Current privacy notice text and version", "GET /me/consents": "My consent history", "POST /me/consents": "Grant or withdraw an optional consent",
    "GET /me/guardian": "Guardian status for a minor", "POST /me/guardian": "Send consent link to a guardian", "GET /guardian-consent/{token}": "Guardian views the notice",
    "POST /guardian-consent/{token}/otp": "Send OTP to the guardian's mobile", "POST /guardian-consent/{token}": "Guardian accepts with OTP; activates account",
    "GET /me/data-requests": "My data-rights requests", "POST /me/data-requests": "File access / correction / erasure / grievance / nomination", "GET /me/data-export": "Download my data as JSON",
    "GET /courses": "Public course catalogue", "GET /courses/{code}": "Course detail; shows registration state if signed in", "POST /courses/{code}/register": "Create registration and order, return checkout",
    "GET /me/registrations": "My registrations",
    "GET /me/orders": "My orders and receipts", "GET /payments/orders/{order_id}": "One order (owner only)", "POST /payments/orders/{order_id}/confirm": "Verify checkout signature, fetch payment, apply",
    "POST /payments/webhooks/{provider}": "Signed gateway webhook (idempotent)", "GET /payments/mock/orders/{provider_order_id}": "Demo gateway: order info", "POST /payments/mock/complete": "Demo gateway: simulate pay / fail",
    "GET /subjects": "Subjects with progress and an entitled flag", "GET /subjects/{code}": "Subject with LMs", "GET /lms/{lm_id}": "LM detail: topics, items, resources, stats",
    "GET /content/{item_id}": "Published note body", "GET /resources/{rid}/playback": "Signed URL + watermark + resume position", "GET /media/stream/{token}": "Stream file by signed token (Range)",
    "POST /resources/{rid}/progress": "Heartbeat: watched interval / position / complete", "POST /lms/{lm_id}/learned": "Mark LM learned (24 h undo)", "DELETE /lms/{lm_id}/learned": "Undo learned",
    "POST /lms/{lm_id}/revisions": "Log a revision session", "PUT /lms/{lm_id}/eoc": "Record end-of-chapter questions result", "GET /me/dashboard": "Home dashboard data",
    "GET /search": "Search LMs and notes", "GET /me/bookmarks": "List bookmarks", "POST /me/bookmarks": "Add bookmark", "DELETE /me/bookmarks/{bid}": "Remove bookmark",
    "GET /practice/options": "Subjects, chapters and counts for the quiz builder", "POST /tests/preview": "Pool size for chosen filters", "POST /tests": "Create custom test",
    "POST /lms/{lm_id}/quiz": "Start chapter quiz", "POST /subjects/{code}/test": "Start 50-question subject test", "GET /attempts/{attempt_id}": "Load attempt (auto-submits if past deadline)",
    "PUT /attempts/{attempt_id}/items/{position}": "Save answer / flag / time", "POST /attempts/{attempt_id}/submit": "Submit and grade", "GET /me/attempts": "Attempt history",
    "GET /me/test-stats": "Accuracy by subject and difficulty",
    "GET /flashcards/decks": "Decks with due counts", "GET /flashcards/session": "Cards due now", "POST /flashcards/{card_id}/review": "Rate card, schedule next review",
    "GET /admin/flashcards": "List flashcards", "POST /admin/flashcards": "Create flashcard", "PATCH /admin/flashcards/{cid}": "Edit / publish flashcard",
    "GET /admin/questions": "Filter question bank", "POST /admin/questions": "Create question", "PATCH /admin/questions/{qid}": "Edit question", "POST /admin/questions/{qid}/{action}": "publish | retire | draft",
    "GET /admin/questions/validate": "Release checks for an LM's question set",
    "GET /admin/catalog": "Full catalogue incl. drafts", "POST /admin/subjects": "Create subject", "PATCH /admin/subjects/{sid}": "Edit subject", "POST /admin/lms": "Create LM", "GET /admin/lms/{lm_id}": "LM with items, resources, LOS",
    "PATCH /admin/lms/{lm_id}": "Edit LM", "POST /admin/topics": "Add topic", "DELETE /admin/topics/{tid}": "Remove topic", "POST /admin/los": "Add learning outcome", "DELETE /admin/los/{lid}": "Remove learning outcome",
    "POST /admin/content-items": "Create note item", "GET /admin/content-items/{iid}/versions/{vid}": "Read a version", "POST /admin/content-items/{iid}/versions": "Save new draft version",
    "POST /admin/content-items/{iid}/versions/{vid}/publish": "Publish a version", "POST /admin/resources": "Upload video / PDF / link (multipart)", "PATCH /admin/resources/{rid}": "Edit resource metadata",
    "POST /admin/resources/{rid}/{action}": "publish | unpublish",
    "GET /admin/courses": "List courses", "POST /admin/courses": "Create course", "PATCH /admin/courses/{cid}": "Edit course, fee, status", "GET /admin/registrations": "Filter registrations",
    "POST /admin/registrations/offline": "Enter an offline payment", "POST /admin/registrations/{rid}/cancel": "Cancel and revoke access", "GET /admin/orders": "Filter orders", "GET /admin/orders/{oid}": "Order with payments and refunds",
    "POST /admin/orders/{oid}/refund": "Full or partial refund", "GET /admin/revenue": "Revenue summary",
    "GET /admin/overview": "KPI tiles", "GET /admin/reports/progress": "Per-student progress for a course", "GET /admin/audit": "Search the audit log", "GET /admin/audit/verify": "Recompute the hash chain",
    "GET /admin/data-requests": "Privacy request queue", "POST /admin/data-requests/{did}": "Update status / resolution", "POST /admin/data-requests/{did}/erase": "Execute erasure",
    "GET /admin/users": "Search users", "GET /admin/users/{uid}": "User with roles, entitlements, sessions", "POST /admin/users": "Create staff user", "PUT /admin/users/{uid}/roles": "Set roles",
    "POST /admin/users/{uid}/deactivate": "Deactivate and end sessions", "POST /admin/users/{uid}/reactivate": "Reactivate", "DELETE /admin/users/{uid}/sessions": "Force sign-out everywhere",
    "GET /admin/batches": "List batches", "POST /admin/batches": "Create batch", "PATCH /admin/batches/{bid}": "Edit batch", "POST /admin/entitlements": "Grant subject access manually",
    "POST /admin/entitlements/{eid}/revoke": "Revoke an entitlement", "GET /healthz": "Liveness", "GET /readyz": "Readiness (database ping)",
}
CHIP = {"public": ("pub", "public"), "session": ("ses", "signed in"), "pending": ("pend", "signed in*"), "optional": ("opt", "optional"), "perm": ("perm", "")}
MODNAME = [("auth", "Auth & profile"), ("privacy", "Privacy & consent"), ("commerce", "Courses & registration"), ("payments", "Payments"), ("learning", "Learning & progress"),
           ("qbank", "Tests & question bank"), ("flashcards", "Flashcards"), ("admin/catalog", "Admin · catalogue & content"), ("admin/commerce", "Admin · commerce"),
           ("admin/users", "Admin · users, batches, entitlements"), ("admin/ops", "Admin · reports, audit, data requests"), ("system", "System")]


def endpoint_table(mod):
    rows = []
    for r in F["routes"]:
        if r["mod"] != mod: continue
        short = r["path"].replace("/api/v1", "")
        c, lab = CHIP[r["auth"]]
        acc = f'<span class="chip {c}">{r["perm"] or lab}</span>'
        rows.append([f'<span class="m {r["m"]}">{r["m"]}</span> <code>{short}</code>', acc, DESC.get(f'{r["m"]} {short}', "")])
    return table(["Endpoint", "Access", "What it does"], rows, "tight", ["46%", "22%", "32%"])


# ============================================================ UI → API → DB map
UIMAP = [
    ("/login", "otp/request · otp/verify · signup · privacy/notice", "otp_challenges, users, user_roles, sessions, consents, audit_log"),
    ("/pending-consent", "me/guardian", "guardians, consents"),
    ("/guardian-consent/[token]", "guardian-consent/{t} · …/otp", "guardians, otp_challenges, consents, users"),
    ("/courses · /courses/[code]", "courses · courses/{code}", "courses, course_subjects, registrations"),
    ("/register/[code]", "courses/{code}/register · payments/orders/{id}/confirm", "registrations, orders, payments, users"),
    ("/mock-gateway (demo)", "payments/mock/* · payments/orders/{id}/confirm", "orders, payments, payment_events"),
    ("/checkout/[orderId] · /orders", "payments/orders/{id} · me/orders", "orders, payments, refunds"),
    ("/dashboard", "me/dashboard · subjects", "lm_progress, resource_progress, entitlements, test_attempts"),
    ("/learn · /learn/[subject]", "subjects · subjects/{code} · lms/{id} · content/{id} · resources/{id}/playback · progress · learned · revisions · eoc", "subjects, learning_modules, topics, los, content_items/versions, resources, lm_progress, resource_progress, revision_logs, eoc_entries"),
    ("/practice", "practice/options · tests/preview · tests · subjects/{code}/test", "questions, test_attempts, attempt_items, entitlements"),
    ("/test/[id]", "attempts/{id} · items/{n} · submit · lms/{id}/quiz", "test_attempts, attempt_items, questions, audit_log"),
    ("/flashcards", "flashcards/decks · session · {id}/review", "flashcards, card_reviews"),
    ("/bookmarks · /search", "me/bookmarks · search", "bookmarks, content_items/versions, learning_modules"),
    ("/profile", "me · me/sessions · me/consents · me/data-requests · me/data-export", "users, sessions, consents, data_requests"),
    ("/staff/login", "auth/staff/login · mfa/setup · mfa", "users, sessions, audit_log"),
    ("/admin (overview)", "admin/overview", "users, registrations, orders, data_requests"),
    ("/admin/catalog · /admin/lms/[id]", "admin/catalog · lms · topics · los · content-items · resources", "subjects, learning_modules, topics, los, content_*, resources"),
    ("/admin/questions", "admin/questions · …/{id}/{action} · validate", "questions"),
    ("/admin/flashcards", "admin/flashcards", "flashcards"),
    ("/admin/courses", "admin/courses", "courses, course_subjects, batches"),
    ("/admin/registrations", "admin/registrations · offline · cancel", "registrations, orders, entitlements"),
    ("/admin/orders · /admin/orders/[id]", "admin/orders · refund · revenue", "orders, payments, refunds"),
    ("/admin/users · /admin/users/[id]", "admin/users · roles · deactivate · sessions · entitlements", "users, user_roles, sessions, entitlements"),
    ("/admin/batches", "admin/batches", "batches, enrolments"),
    ("/admin/reports", "admin/reports/progress", "lm_progress, test_attempts, registrations"),
    ("/admin/data-requests", "admin/data-requests · erase", "data_requests, users and all user-owned rows"),
    ("/admin/audit", "admin/audit · verify", "audit_log"),
]

TABLE_DOC = {
    "Identity & access": [
        ("users", "Every person: candidate or staff", "mobile_e164 / email unique · status · is_minor · password_hash · totp_secret", "CITEXT email; soft delete via deleted_at"),
        ("user_roles", "Role grants (composite PK)", "user_id + role", "CASCADE with user"),
        ("guardians", "Parent / guardian of a minor", "student_user_id unique · verified_at", "1 per student"),
        ("sessions", "One row per signed-in device", "refresh_token_hash · family_id · revoked_at", "hash only, never the token"),
        ("otp_challenges", "One-time codes", "destination_hash · code_hash · attempts", "hashes only"),
    ],
    "Catalogue & content": [
        ("subjects", "10 CFA subjects", "code unique · exam_weight", ""),
        ("learning_modules", "56 LMs", "unique(subject_id, lm_no) · source_ref (internal)", "source_ref never exposed to candidates"),
        ("topics", "Sections inside an LM", "los_ids JSONB", ""), ("los", "Learning outcome statements", "unique(lm_id, code) · command_word", ""),
        ("content_items", "A note slot in an LM", "current_published_version_id", ""),
        ("content_versions", "Immutable versions of a note", "unique(item_id, version_no) · body JSONB · plain_text (search)", "provenance + licence_ref"),
        ("resources", "Video, PDF, class note, link", "storage_key · chapters JSONB · downloadable", "status draft→published"),
    ],
    "Commerce & enrolment": [
        ("courses", "Sellable course", "fee_paise (GST-inclusive) · validity_days or access_ends_on · seat_limit", "status draft|open|closed"),
        ("course_subjects", "Which subjects a course includes", "composite PK", ""),
        ("registrations", "A candidate's seat in a course", "partial unique index: one open registration per user+course", "RESTRICT on course"),
        ("orders", "Money request", "number KSC-year-seq · provider_order_id unique · refunded_paise", "RESTRICT on user"),
        ("payments", "Gateway payment attempts", "provider_payment_id unique", ""), ("payment_events", "Raw webhooks for replay & idempotency", "unique(provider, event_id)", "signature_valid recorded"),
        ("refunds", "Refund records", "amount_paise · status", ""), ("batches", "Cohorts", "code unique · starts_on / ends_on", ""),
        ("enrolments", "User ↔ batch", "unique(user_id, batch_id)", ""), ("entitlements", "The access ledger: who may open which subject, until when", "index(user, subject, ends_at) · source registration|batch|grant", "single source of truth for access"),
    ],
    "Learning activity": [
        ("lm_progress", "Learned flag and last opened", "learned_undo_until", ""), ("resource_progress", "Watched intervals per resource", "watched JSONB merged intervals", ""),
        ("revision_logs", "Revision sessions", "unique per user+LM+day when counted", ""), ("eoc_entries", "End-of-chapter results", "q_attempted · q_correct", ""),
        ("bookmarks", "Saved places", "target_type · target_id", ""), ("flashcards", "Front/back cards", "source_ref unique", ""), ("card_reviews", "Per-user SRS state", "ease · interval · due_on (indexed)", ""),
    ],
    "Assessment": [
        ("questions", "3-option MCQs", "options JSONB · correct_index · difficulty · status draft|published|retired", "version, provenance"),
        ("test_attempts", "A quiz or test run", "kind chapter|master|custom · mode · deadline_at · score_pct", ""),
        ("attempt_items", "Questions in an attempt", "snapshot JSONB · answer_index · is_correct", "snapshot freezes content"),
    ],
    "Privacy & governance": [
        ("consents", "Append-only consent ledger", "purpose · granted · notice_version · actor self|guardian", "never updated in place"),
        ("data_requests", "DPDP rights requests", "type · due_at · status", ""), ("audit_log", "Tamper-evident audit trail", "prev_hash · hash (SHA-256 chain) · changes/metadata JSONB", "INET ip"),
        ("outbox", "Domain events awaiting dispatch", "dispatched_at · attempts", ""), ("settings", "Key/value config", "JSONB value", ""),
    ],
}


def build():
    o = []
    # ======================================================== PART 2
    o.append(h1("2", "Backend mapping", "Tech stack, technical architecture, deployment and the shape of the code."))
    o.append(h2("2.1", "Technology stack"))
    o.append(fig(d_stack(), "Five-layer stack from browser to storage."))
    o.append(table(["Area", "Library / service", "Version constraint", "Used for"], [
        ["Web framework", "Next.js · React · TypeScript", "^16.4 · ^19.3 · ~5.9", "35 pages, same-origin proxy, security headers"],
        ["API framework", "FastAPI · Pydantic · Uvicorn", "≥0.115 · ≥2.9 · ≥0.54", "Routing, validation, ASGI server"],
        ["ORM / DB", "SQLAlchemy (async) · asyncpg · Alembic", "≥2.0.36 · ≥0.32 · ≥1.20", "Models, queries, migrations (2 revisions so far)"],
        ["Database", "PostgreSQL 16", "extensions: citext, pg_trgm", "37 tables, JSONB, INET, advisory locks"],
        ["Security", "argon2-cffi · PyJWT · pyotp", "≥25.1 · ≥2.9 · ≥2.10", "Password hashing, tokens, TOTP"],
        ["HTTP client", "httpx", "≥0.28", "Gateway and event-sink calls"],
        ["Config", "pydantic-settings", "≥2.16", "12-factor settings with start-up guard rails"],
        ["Quality", "pytest · pytest-asyncio · ruff · tsc", "≥9.1 · ≥1.4 · ≥0.17", "32 tests, lint (E,F,I,B,UP), type-check"]], widths=["16%", "30%", "22%", "32%"]))
    o.append(h2("2.2", "Technical architecture: a modular monolith"))
    o.append(p("The API is one deployable service organised into modules. Each module owns its models, service functions and router. Modules talk through service calls and domain events, never by reaching into each other's tables, which keeps a later split into separate services possible without a rewrite (the payments module is already written to be replaceable by an external service)."))
    o.append(fig(d_modules(), "Module map. Every box is a Python package under <code>app/modules</code> (or <code>app/core</code>).", wide=True))
    o.append(table(["Module", "Owns tables", "Responsibility"], [
        ["auth", "otp_challenges, sessions", "OTP, staff login, TOTP, session rotation"], ["users", "users, user_roles, guardians", "Identity records"],
        ["catalog · content · media", "subjects, learning_modules, topics, los · content_* · resources", "What there is to learn, versioned, with files"],
        ["learning · progress", "lm_progress, resource_progress, revision_logs, eoc_entries, bookmarks", "Reading content, tracking progress, search"],
        ["qbank", "questions, test_attempts, attempt_items", "Question bank, tests, grading"], ["flashcards", "flashcards, card_reviews", "Cards and spaced repetition"],
        ["commerce · enrolment", "courses, registrations, batches, enrolments, entitlements", "Selling a course and granting access"],
        ["payments", "orders, payments, payment_events, refunds", "Gateway adapters (Razorpay, mock), webhooks, refunds"],
        ["privacy · audit", "consents, data_requests, audit_log, outbox, settings", "DPDP compliance, tamper-evident log, events"]], widths=["22%", "42%", "36%"]))
    o.append(h2("2.3", "Request lifecycle"))
    o.append(fig(d_request(), "What happens on every API call. The unit of work commits once at the end, so a failed audit write rolls back the business change too.", wide=True))
    o.append(table(["Concern", "How it is done", "Code"], [
        ["Identifiers", "UUIDv7: time-ordered (good for index locality), random part makes them unguessable", "<code>core/ids.py</code>"],
        ["Time", "Timestamps are stored timezone-aware in UTC; business dates use IST", "<code>core/timeutil.py</code>"],
        ["Errors", "RFC 7807 <code>application/problem+json</code> with a stable <code>code</code> field the UI switches on", "<code>core/errors.py</code>"],
        ["Validation", "Pydantic models reject unknown fields and return per-field messages (HTTP 422)", "<code>core/schemas.py</code>"],
        ["Naming", "Deterministic constraint and index names so migrations are reviewable", "<code>core/db.py</code> NAMING"],
        ["Settings", "Environment variables; start-up asserts forbid unsafe combos outside dev", "<code>core/config.py</code>"],
        ["Notifications", "SMS and email behind provider interfaces; console provider in dev, MSG91 / SES adapters planned", "<code>core/notify.py</code>"],
        ["Files", "Storage interface with path-traversal protection and size cap; local disk now, S3 planned", "<code>core/storage.py</code>"]], widths=["16%", "62%", "22%"]))
    o.append(h2("2.4", "Domain events and the outbox"))
    o.append(p("Payments finishing must open access, and a full refund must close it. These cross-module reactions use a small event bus. <code>publish()</code> writes the event to an <code>outbox</code> table <i>and</i> calls in-process subscribers inside the caller's transaction, so local consistency is immediate and atomic. A background loop then forwards pending events to an optional HTTP sink, signed with HMAC, so another team's service (CRM, analytics) can listen without touching this code."))
    o.append(fig(d_events(), "Transactional outbox. The dispatcher uses <code>FOR UPDATE SKIP LOCKED</code>, so several API replicas can run the loop safely."))
    o.append(h2("2.5", "Deployment today: one container on Render"))
    o.append(fig(d_deploy_now(), "Current staging deployment from <code>render.yaml</code> and <code>Dockerfile</code>.", wide=True))
    o.append(fig(d_build(), "Three-stage image keeps build tools out of the runtime image; the process runs as a non-root user."))
    o.append(table(["Variable", "Staging value", "Purpose"], [
        ["APP_ENV", "staging", "Activates production-style guard rails"], ["DEMO_MODE", "true (staging only)", "On-screen OTP and mock gateway until SMS and Razorpay are connected; production refuses to start with it"],
        ["COOKIE_SECURE · STAFF_MFA_REQUIRED", "true · true", "Mandatory outside local/test; server asserts at start-up"], ["PAYMENT_PROVIDER", "mock → razorpay", "Selects gateway adapter"],
        ["SECRET_KEY", "generated by Render", "Signs every JWT and keyed hash (min 32 chars)"], ["DATABASE_URL", "from Render Postgres", "Auto-rewritten to the asyncpg driver"],
        ["SEED_ON_START · SEED_STAFF_PASSWORD", "true · prompted", "Idempotent demo catalogue and four staff accounts"]], widths=["32%", "22%", "46%"]))
    o.append(callout("warn", "Free-plan limits to know", "Render's free web service sleeps after 15 minutes idle (first request takes about a minute), has no persistent disk (uploaded PDFs vanish on redeploy) and its free Postgres expires after 30 days. Move to a paid plan, or to S3 for uploads, before real students sign up."))
    o.append(h2("2.6", "Target architecture: AWS Mumbai"))
    o.append(p("The infrastructure document (A-05) defines where the platform is heading once traffic and compliance needs outgrow a single container. The application code is already stateless apart from the media directory, so the move is mostly infrastructure."))
    o.append(fig(d_aws(), "Target architecture from A-05 (design, not yet built). Elements not yet present in code: Redis, Celery worker, S3 adapter, ClamAV scan.", wide=True))
    o.append(h2("2.7", "Quality and delivery"))
    o.append('<div class="grid2"><div>' + C.tests_chart() + "</div><div>" + ul([
        "Backend tests run against a separate <code>cfa_lms_test</code> database with real PostgreSQL features (advisory locks, JSONB).",
        "Covered: OTP and session rules, staff login and MFA, privacy and consent, payments, webhooks and refunds, learning progress, tests and flashcards.",
        "Frontend: <code>tsc --noEmit</code> and <code>next build</code> must pass.",
        "CI/CD design (D-02) and branching (D-03) are documented; pipeline files are not yet in the repo."]) + "</div></div>")

    # ======================================================== PART 3
    o.append(h1("3", "APIs, database & UI mapping", "Every endpoint, every table, and how each screen connects to them."))
    o.append(h2("3.1", "API conventions"))
    o.append(table(["Topic", "Convention"], [
        ["Base path", "<code>/api/v1</code>. Interactive docs at <code>/api/v1/docs</code> exist only in local/test."],
        ["Format", "JSON in and out; file upload uses multipart (<code>POST /admin/resources</code>)."],
        ["Authentication", "HttpOnly <code>access_token</code> cookie (or <code>Authorization: Bearer</code>). See Part 5."],
        ["CSRF", "Unsafe methods carrying the cookie must send <code>X-CSRF-Token</code> equal to the <code>csrf_token</code> cookie. Exempt: sign-in endpoints, refresh, webhooks, guardian links."],
        ["Idempotency", "Payment application and webhooks are idempotent by provider ids; unpaid order reuse for 30 min."],
        ["Pagination", "<code>limit</code> query parameter with a hard cap (500 admin lists, 200 attempts)."],
        ["Tracing", "Every response carries <code>x-request-id</code>; the same id is in logs and audit rows."],
        ["Caching", "<code>Cache-Control: no-store</code> on all API responses except signed media (private, 1 h)."]], widths=["18%", "82%"]))
    o.append(table(["HTTP", "code", "Meaning for the UI"], [
        ["401", "unauthenticated · token_expired", "Client refreshes once, then asks to sign in"], ["403", "forbidden · not_entitled · guardian_consent_required · csrf_failed", "Missing permission, subject not bought, minor awaiting consent, bad CSRF"],
        ["404", "not_found", "Also used to hide resources that belong to someone else"], ["409", "conflict · already_registered · course_full · course_closed", "State conflict"],
        ["422", "validation_failed · otp_invalid · otp_expired …", "Field-level messages in <code>errors[]</code>"], ["423", "account_locked", "Staff lock after 5 bad passwords"],
        ["429", "rate_limited", "OTP request limit"], ["502", "gateway_unavailable", "Payment gateway unreachable"]], "tight", ["8%", "42%", "50%"]))
    o.append(h2("3.2", "Endpoint inventory"))
    o.append(fig(C.api_by_module(), "Endpoints per module, split by HTTP method."))
    o.append('<div class="grid2"><div>' + C.api_by_auth() + "</div><div>" + C.perm_counts() + "</div></div>")
    o.append(callout("info", "Reading the access column", "<span class='chip pub'>public</span> no sign-in (some use a token in the URL or a signature). <span class='chip ses'>signed in</span> any active user. <span class='chip pend'>signed in*</span> also allowed while a minor awaits guardian consent. <span class='chip opt'>optional</span> works signed out, richer when signed in. Permission names (e.g. <span class='chip perm'>order:refund</span>) are checked against the caller's roles."))
    o.append(h2("3.3", "Endpoint catalogue"))
    for mod, name in MODNAME:
        n = sum(1 for r in F["routes"] if r["mod"] == mod)
        o.append(h3(f"{name} · {n} endpoints"))
        o.append(endpoint_table(mod))
    o.append(h2("3.4", "Database design"))
    o.append(fig(C.domain_donut(), "37 tables grouped into six domains."))
    o.append(fig(d_erd_a(), "Entity relationships · identity, privacy, commerce and enrolment (key columns only).", wide=True))
    o.append(fig(d_erd_b(), "Entity relationships · catalogue, content, assessment and learning progress.", wide=True))
    o.append(fig(C.tables_chart(), "Width of each table (columns), coloured by domain.", wide=True))
    o.append(h3("Design rules"))
    o.append(ul(["<b>UUIDv7 primary keys</b> everywhere except two append-only logs (audit_log, outbox) which use identity integers to give a total order.",
                 "<b>JSONB</b> only for genuinely flexible payloads: note bodies, question options, attempt snapshots, watched intervals, audit changes.",
                 "<b>Referential actions</b>: user-owned rows CASCADE on delete (erasure is simple); orders and courses are RESTRICT so financial history cannot be orphaned.",
                 "<b>Money</b> is stored as integer paise, never floats. GST-inclusive fee on the course.",
                 "<b>Secrets</b> are stored only as hashes (OTP, refresh token, password) or, for TOTP, as base32 bytes awaiting KMS envelope encryption.",
                 "<b>Constraints do the policing</b>: partial unique index for one open registration per user and course; unique (provider, event_id) for webhook replay; unique per-day revision count."]))
    o.append(h3("Data dictionary"))
    for dom, rows in TABLE_DOC.items():
        o.append(f'<h4 style="color:{C.DCOL[dom]}">{dom} · {len(rows)} tables</h4>')
        o.append(table(["Table", "Purpose", "Key columns & constraints", "Notes"], [[f"<code>{a}</code>", b, c, d_] for a, b, c, d_ in rows], "tight", ["17%", "27%", "38%", "18%"]))
    o.append(h2("3.5", "UI → API → database mapping"))
    o.append(p("Read each row left to right: a screen calls the listed endpoints, which read or write the listed tables. Use it to estimate the blast radius of a change in either direction."))
    o.append(table(["Screen (route)", "API calls (under /api/v1)", "Tables touched"], [[f"<code>{a}</code>", b, c] for a, b, c in UIMAP], "tight", ["22%", "40%", "38%"]))
    o.append(h3("Flow: taking a quiz, from click to stored result"))
    o.append(fig(d_seq_test(), "Quiz data flow. The answer key never leaves the server before submission; the result is graded from the stored snapshot.", wide=True))
    return "".join(o)
