"""Cover, executive summary and Part 1 – UI workflows."""
from base import *
from svg import *
import charts as C


def cover():
    art = S(794, 1123)
    import random
    random.seed(7)
    pts = [(random.randint(380, 780), random.randint(40, 520)) for _ in range(34)]
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 125 ** 2:
                art.line(a[0], a[1], b[0], b[1], "#7EE7DF", 1, None); art.p[-1] = art.p[-1].replace('stroke-width="1"', 'stroke-width="1" opacity=".22"')
    for x, y in pts:
        art.p.append(f'<circle cx="{x}" cy="{y}" r="{random.choice([3,4,6])}" fill="#7EE7DF" opacity=".55"/>')
    for x, y in pts[:6]:
        art.p.append(f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="#9FB0FF" stroke-width="1.2" opacity=".5"/>')
    return f"""<section class="cover"><div class="art">{art.svg()}</div>
<div class="txt"><div class="tag">KARAN SIR CLASSES · CFA LEARNING HUB</div>
<h1>Platform<br><b>Technical Guide</b></h1>
<div class="sub">User workflows for candidates, staff and admins · backend and architecture mapping · APIs, database and UI mapping · scaling, performance and authentication.</div></div>
<div class="parts"><div><b>1</b>UI workflows</div><div><b>2</b>Backend &amp; architecture</div><div><b>3</b>APIs · DB · UI map</div><div><b>4–5</b>Scaling &amp; authentication</div></div>
<div class="meta"><div><b>Version 1.0</b>29 October 2026</div><div><b>Source of truth</b>Repository code (master @ 8b76491)</div><div><b>Audience</b>Product, engineering, operations, security</div></div></section>"""


def toc(pages=None):
    pages = pages or {}
    rows = []
    for lvl, num, title, hid in HEADINGS:
        pg = pages.get(hid, "")
        cls = "r1" if lvl == 1 else "r2"
        label = f"Part {num} · {title}" if lvl == 1 else f"{num}&nbsp;&nbsp;{title}"
        rows.append(f'<div class="{cls}"><span>{label}</span><span class="dots"></span><span class="pg">{pg}</span></div>')
    return '<section class="toc"><h2 style="margin-top:0">Contents</h2>' + "".join(rows) + "</section>"


# ============================================================ diagrams
def d_system_context():
    d = Flow(900, 420)
    d.node("cand", 20, 40, 150, 70, "Candidate", "ui", sub="student · mobile / laptop", size=14)
    d.node("staff", 20, 160, 150, 70, "Staff", "ui", sub="author · reviewer", size=14)
    d.node("adm", 20, 280, 150, 70, "Admin", "ui", sub="admin · super admin", size=14)
    d.rect(240, 20, 420, 380, PALE, LINE, 14, dash="6,4")
    d.text(450, 40, "KARAN SIR CLASSES · CFA LEARNING HUB", 11, MUTED, 700)
    d.node("web", 270, 70, 360, 80, "Next.js 16 web app", "ui", sub="React 19 · 35 pages · same-origin /api proxy", size=14)
    d.node("api", 270, 190, 360, 80, "FastAPI service", "api", sub="12 modules · 118 endpoints · async SQLAlchemy", size=14)
    d.node("db", 290, 305, 140, 75, "PostgreSQL 16", "db", shape="db", size=13)
    d.node("fs", 470, 315, 140, 55, "File storage", "db", sub="PDF · video", size=13)
    d.node("rz", 730, 40, 150, 70, "Razorpay", "ext", sub="payments · webhooks", size=14)
    d.node("sms", 730, 140, 150, 70, "SMS · email", "ext", sub="MSG91 · SES (planned)", size=14)
    d.node("evt", 730, 240, 150, 70, "Event sink", "ext", sub="optional HTTP + HMAC", size=14)
    d.node("cfa", 730, 340, 150, 55, "Authenticator app", "ext", sub="TOTP · staff MFA", size=13)
    for a in ("cand", "staff", "adm"): d.link(a, "web", color=INDIGO, mode="h")
    d.link("web", "api", "/api/* proxy", INDIGO, mode="v")
    d.link("api", "db", None, TEAL, mode="v", off=-50)
    d.link("api", "fs", None, TEAL, mode="v", off=50)
    d.link("api", "rz", "orders · webhooks", VIOLET, mode="h", lpos=(690, 140))
    d.link("api", "sms", "OTP · consent links", VIOLET, mode="h")
    d.link("api", "evt", "outbox events", VIOLET, mode="h", lpos=(695, 262))
    d.link("cfa", "api", None, VIOLET, dash="4,3", mode="h", lpos=(690, 350))
    return d.svg()


def d_roles():
    d = Flow(900, 330)
    d.node("c", 20, 30, 250, 150, "", "ui")
    d.text(145, 52, "CANDIDATE", 12, INDIGO, 800); d.text(145, 74, "role: student", 11, MUTED)
    d.text(145, 130, "Learns, practises, pays,\nmanages own privacy.\n9 permissions", 12, INK)
    d.node("a", 330, 20, 250, 80, "", "warn"); d.text(455, 38, "STAFF · AUTHOR", 11.5, "#9A6410", 800)
    d.text(455, 72, "Writes content, questions,\nflashcards · 12 permissions", 11.5, INK)
    d.node("r", 330, 110, 250, 80, "", "warn"); d.text(455, 128, "STAFF · REVIEWER", 11.5, "#9A6410", 800)
    d.text(455, 162, "Publishes, reads reports\n11 permissions", 11.5, INK)
    d.node("ad", 640, 40, 240, 150, "", "api")
    d.text(760, 62, "ADMIN", 12, "#0B5F5D", 800); d.text(760, 84, "role: admin", 11, MUTED)
    d.text(760, 138, "Everything staff can do plus\nusers · batches · fees · orders\nrefunds · audit · data requests\n29 permissions", 11.5, INK)
    d.node("sa", 640, 230, 240, 80, "", "dark"); d.text(760, 250, "SUPER ADMIN", 12, "#7EE7DF", 800)
    d.text(760, 286, "Admin + assign admins,\nglobal settings · 32 permissions", 11.5, WHITE)
    d.arrow([(580, 60), (640, 100)], MUTED, label="union"); d.arrow([(580, 150), (640, 130)], MUTED)
    d.arrow([(760, 190), (760, 230)], MUTED, label="inherits")
    d.text(300, 250, "Roles are additive: a user's permissions are the union of every role held.\nDeny by default: an endpoint with no matching permission returns 403.", 12, MUTED, anchor="middle", italic=True)
    d.p.append("")
    return d.svg()


def d_sitemap_candidate():
    d = S(900, 470)
    cols = [("PUBLIC", 20, ["/\nHome", "/courses\nCourse catalogue", "/courses/[code]\nCourse detail & fee", "/login\nOTP sign-in · sign-up"], "std"),
            ("ACCOUNT & PAYMENT", 245, ["/register/[code]\nRegistration form", "/checkout/[orderId]\nReceipt & status", "/mock-gateway\nTest gateway (demo)", "/pending-consent\n/guardian-consent/[token]\nUnder-18 flow"], "warn"),
            ("LEARN & PRACTISE", 470, ["/dashboard\nProgress by subject", "/learn · /learn/[subject]\nLM view: videos · notes · quiz", "/practice → /test/[id]\nCustom quiz & attempt", "/flashcards\nSpaced repetition"], "ui"),
            ("MY SPACE", 695, ["/search  ·  /bookmarks", "/orders\nReceipts", "/profile\nDetails · devices · privacy", "Sign out"], "ok")]
    for title, x, items, kind in cols:
        f, st, tx = KIND[kind]
        d.rect(x, 14, 190, 440, "#FAFBFF", LINE, 12)
        d.pill(x + 20, 26, 150, 24, title, st, WHITE, 10.5)
        for i, it in enumerate(items):
            d.box(x + 12, 66 + i * 98, 166, 82, it, kind, 11.5, weight=600)
    for x in (210, 435, 660):
        d.arrow([(x - 8, 232), (x + 36, 232)], INDIGO, sw=2.2)
    return d.svg()


def d_sitemap_staff():
    d = S(900, 430)
    groups = [("CONTENT", 20, [("Catalogue & content", "/admin/catalog → /admin/lms/[id]"), ("Question bank", "/admin/questions"), ("Flashcards", "/admin/flashcards")], "warn", "catalog:*, content:*, qbank:*"),
              ("COMMERCE", 245, [("Courses & fees", "/admin/courses"), ("Registrations", "/admin/registrations"), ("Payments & refunds", "/admin/orders → /[id]")], "api", "course:manage, order:*"),
              ("PEOPLE", 470, [("Users & staff", "/admin/users → /[id]"), ("Batches", "/admin/batches"), ("Entitlements · sessions", "inside user detail")], "ui", "user:*, batch:manage"),
              ("INSIGHT & COMPLIANCE", 695, [("Overview", "/admin"), ("Progress report", "/admin/reports"), ("Data requests · Audit log", "/admin/data-requests · /admin/audit")], "bad", "report:read, audit:read")]
    for title, x, items, kind, perm in groups:
        f, st, tx = KIND[kind]
        d.rect(x, 14, 190, 400, "#FAFBFF", LINE, 12)
        d.pill(x + 14, 26, 162, 24, title, st, WHITE, 10)
        for i, (a, b) in enumerate(items):
            d.box(x + 12, 66 + i * 90, 166, 76, a, kind, 12.5, sub=b)
        d.text(x + 95, 372, perm, 10.5, MUTED, 500, italic=True)
        d.text(x + 95, 392, "menu item shown only if held", 9.5, MUTED)
    return d.svg()


def d_journey():
    d = S(900, 240)
    stages = [("Discover", "Home · Courses", INDIGO), ("Sign in", "Mobile OTP", TEAL), ("Register", "Profile form", VIOLET),
              ("Pay", "Razorpay / test", AMBER), ("Learn", "Videos · notes", GREEN), ("Practise", "Quizzes · tests", "#E07B39"),
              ("Revise", "Flashcards · log", ROSE), ("Track", "Dashboard", NAVY)]
    w = 106
    for i, (t, sub, c) in enumerate(stages):
        x = 14 + i * 110
        d.p.append(f'<polygon points="{x},30 {x+w-14},30 {x+w},70 {x+w-14},110 {x},110 {x+14},70" fill="{c}"/>')
        d.text(x + w / 2 - 2, 62, t, 13, WHITE, 700); d.text(x + w / 2 - 2, 84, sub, 9.6, "#ffffffdd")
    detail = ["No account\nneeded to browse", "Code via SMS\n5 min validity", "Course, fee, seats\nchecked server-side", "Order → webhook →\naccess opens",
              "Every LM open\nno chapter locks", "10-q chapter quiz\n50-q subject test", "Spaced repetition\nrevision log", "Subject rings,\naccuracy, streak"]
    for i, t in enumerate(detail):
        x = 14 + i * 110
        d.rect(x + 4, 128, w - 8, 56, "#F7F8FD", LINE, 8); d.text(x + w / 2, 156, t, 10.2, INK)
    d.arrow([(14, 214), (886, 214)], LINE, sw=2.4)
    d.text(450, 228, "Self-service end to end: no staff intervention is needed between sign-up and first lesson", 10.5, MUTED, italic=True)
    return d.svg()


def d_login():
    d = Flow(900, 650)
    d.node("a", 330, 10, 240, 44, "Enter mobile number (+91)", "ui", "pill")
    d.node("b", 330, 84, 240, 44, "POST /auth/otp/request", "api")
    d.node("c", 640, 84, 230, 54, "Over 5 codes in the last hour?", "warn", "dia", size=11.5)
    d.node("c2", 660, 18, 190, 44, "429 · try again later", "bad")
    d.node("e", 330, 160, 240, 44, "Enter 6-digit code (5-min TTL)", "ui", "pill")
    d.node("f", 330, 234, 240, 44, "POST /auth/otp/verify", "api")
    d.node("g", 640, 224, 230, 64, "Wrong code?\nattempts left ≤ 0?", "warn", "dia", size=11)
    d.node("g2", 660, 318, 190, 44, "Request a new code", "bad")
    d.node("h", 330, 310, 240, 64, "Account for this mobile?", "warn", "dia", size=12.5)
    d.node("s1", 10, 322, 250, 60, "Sign-up form: name, DOB, city,\nprivacy notice + terms", "ui")
    d.node("s2", 10, 420, 250, 46, "POST /auth/signup (signup token)", "api")
    d.node("age", 10, 490, 250, 64, "Age under 18?", "warn", "dia", size=12.5)
    d.node("st", 330, 420, 240, 56, "Active/staff-only check\nstart session (cookies)", "api")
    d.node("ok", 330, 500, 240, 44, "Dashboard", "ok", "pill")
    d.node("pend", 10, 590, 250, 52, "Pending guardian consent\n/pending-consent", "bad")
    d.link("a", "b", color=INDIGO); d.link("b", "c", "check", MUTED, mode="h")
    d.link("c", "c2", "yes", ROSE, mode="v"); d.link("c", "e", "no", GREEN, mode="h", lpos=(600, 175))
    d.link("e", "f", color=INDIGO); d.link("f", "g", None, MUTED, mode="h")
    d.link("g", "g2", "yes", ROSE, mode="v"); d.link("g", "h", "no", GREEN, mode="h", lpos=(600, 330))
    d.link("h", "s1", "no", AMBER, mode="h"); d.link("h", "st", "yes", GREEN, mode="v")
    d.link("s1", "s2", color=INDIGO); d.link("s2", "age", color=INDIGO)
    d.link("age", "st", "no · adult", GREEN, mode="h"); d.link("age", "pend", "yes", ROSE, mode="v")
    d.link("st", "ok", color=GREEN)
    return d.svg()


def d_guardian():
    return seq([("s", "Student (under 18)", "ui"), ("w", "Web app", "ui"), ("api", "FastAPI", "api"), ("sms", "SMS", "ext"), ("g", "Parent / guardian", "ui")], [
        ("s", "w", "Signs up with DOB < 18"), ("w", "api", "POST /auth/signup → status = pending_guardian"),
        ("api", "api", "Account created, service consent withheld"),
        ("s", "w", "Enters guardian name · mobile · relation"), ("w", "api", "POST /me/guardian"),
        ("api", "sms", "Consent link (JWT 7 days) → guardian mobile"), ("sms", "g", "SMS with /guardian-consent/[token]", "dash"),
        ("g", "api", "GET notice · POST …/otp (guardian OTP)"), ("g", "api", "POST …/[token]  accept + OTP code"),
        ("api", "api", "Verify OTP · record consent (actor = guardian)"), ("api", "s", "Status → active · course registration unlocked", "dash")], 900, step=42)


def d_payment():
    return seq([("c", "Candidate", "ui"), ("w", "Next.js", "ui"), ("api", "FastAPI", "api"), ("db", "PostgreSQL", "db"), ("gw", "Gateway", "ext")], [
        ("c", "w", "Submits registration form"), ("w", "api", "POST /courses/{code}/register"),
        ("api", "db", "Registration (pending) + Order KSC-yyyy-nnnnnn"), ("api", "gw", "Create gateway order (amount in paise)"),
        ("api", "w", "Checkout payload", "dash"), ("c", "gw", "Pays by UPI / card on gateway"),
        ("gw", "api", "Webhook payment.captured (HMAC signed)"), ("api", "db", "Idempotent insert payment_events · order = PAID"),
        ("api", "db", "Event order_paid → registration active → entitlements"), ("gw", "w", "Browser success callback", "dash"),
        ("w", "api", "POST /payments/orders/{id}/confirm"), ("api", "gw", "Fetch payment (never trust the browser)"),
        ("api", "w", "Paid receipt → Start studying", "dash")], 900, step=40)


def d_learn_loop():
    d = Flow(900, 360)
    cx, cy = 450, 180
    d.circle(cx, cy, 70, "", NAVY)
    d.text(cx, cy - 6, "Nothing is\nlocked", 14, WHITE, 700); d.text(cx, cy + 34, "advisory pass marks", 9.5, "#C9D3FF")
    nodes = [("n1", 380, 14, "1  Open an LM", "Subject → LM view", "ui"), ("n2", 640, 80, "2  Watch · read", "Resource ≥ 90% = done", "api"),
             ("n3", 640, 220, "3  Chapter quiz", "10 q · 90 s each", "warn"), ("n4", 380, 300, "4  Log revision", "counted once / day", "ok"),
             ("n5", 120, 220, "5  Mark learned", "undo within 24 h", "ok"), ("n6", 120, 80, "6  Next LM", "or flashcards", "ui")]
    for i, x, y, t, s, k in nodes: d.node(i, x, y, 180, 56, t, k, sub=s, size=13)
    seqn = ["n1", "n2", "n3", "n4", "n5", "n6"]
    for a, b in zip(seqn, seqn[1:] + ["n1"]): d.link(a, b, color=INDIGO, mode="auto")
    return d.svg()


def d_attempt():
    d = Flow(900, 300)
    d.node("a", 20, 100, 150, 70, "in_progress", "ui", "pill", sub="items drawn, key hidden")
    d.node("b", 250, 30, 190, 60, "Answer / flag", "api", sub="PUT /attempts/{id}/items/{n}")
    d.node("c", 250, 190, 190, 60, "Save & exit", "std", sub="resume ≤ 7 days if untimed")
    d.node("d", 520, 100, 170, 70, "Submit", "api", sub="POST /attempts/{id}/submit")
    d.node("e", 520, 220, 170, 56, "Deadline passes", "bad", sub="90 s × questions")
    d.node("f", 760, 100, 120, 70, "submitted", "ok", "pill", sub="graded on server")
    d.link("a", "b", color=INDIGO); d.link("b", "a", "autosave", MUTED, mode="v", off=0, lpos=(210, 62))
    d.link("a", "c", color=MUTED); d.link("b", "d", color=INDIGO); d.link("d", "f", "score_pct, pass mark", GREEN)
    d.link("e", "f", "auto-submit (timeout)", ROSE, mode="h", lpos=(780, 235)); d.link("c", "a", "resume", MUTED, mode="auto")
    return d.svg()


def d_staff_login():
    d = Flow(900, 330)
    d.node("a", 10, 125, 150, 60, "Email +\npassword", "ui", "pill")
    d.node("b", 200, 120, 160, 70, "POST /auth/staff/login", "api", size=12)
    d.node("x", 200, 235, 160, 60, "5 wrong = 15 min lock\n(generic error)", "bad", size=11)
    d.node("c", 400, 115, 140, 80, "MFA\nenrolled?", "warn", "dia")
    d.node("e", 590, 30, 150, 70, "Show secret + QR\n/auth/staff/mfa/setup", "api", size=11)
    d.node("f", 590, 210, 150, 70, "6-digit TOTP\nPOST /auth/staff/mfa", "api", size=11)
    d.node("g", 780, 115, 110, 80, "Session\n12 h · /admin", "ok")
    d.link("a", "b", color=INDIGO); d.link("b", "x", "fail", ROSE, mode="v"); d.link("b", "c", "ok", GREEN, mode="h")
    d.link("c", "e", "no · first login", AMBER, mode="h", lpos=(525, 70)); d.link("c", "f", "yes", GREEN, mode="h", lpos=(525, 240))
    d.link("e", "f", "scan & enter code", MUTED, mode="v"); d.link("f", "g", color=GREEN, mode="h")
    return d.svg()


def d_content_flow():
    d = Flow(900, 330)
    d.text(14, 18, "Notes, videos & PDFs", 12.5, NAVY, 700, anchor="start")
    d.node("a", 14, 36, 170, 64, "Author drafts\nnew version", "warn", sub="content:write")
    d.node("b", 250, 36, 170, 64, "Draft saved", "std", "pill")
    d.node("c", 490, 36, 190, 64, "Reviewer / admin\npublishes", "api", sub="content:publish")
    d.node("d", 740, 36, 146, 64, "Live to students", "ok", "pill")
    d.link("a", "b", color=INDIGO); d.link("b", "c", color=INDIGO); d.link("c", "d", color=GREEN)
    d.link("d", "a", "edit → new version (old stays visible)", MUTED, mode="auto", dash="4,3", lpos=(450, 118))
    d.text(14, 168, "Questions", 12.5, NAVY, 700, anchor="start")
    d.node("q1", 14, 186, 170, 64, "Author writes\n3 options, key, rationale", "warn", sub="qbank:write")
    d.node("q2", 250, 186, 150, 64, "draft", "std", "pill")
    d.node("q3", 460, 170, 200, 96, "Release check\nanswer split 25–42%\nno run > 3 · no duplicates", "warn", size=11)
    d.node("q4", 730, 186, 156, 64, "published", "ok", "pill", sub="qbank:publish")
    d.link("q1", "q2", color=INDIGO); d.link("q2", "q3", color=INDIGO); d.link("q3", "q4", "ok", GREEN)
    d.arrow([(808, 250), (808, 300), (330, 300), (330, 252)], ROSE, "4,3", "retire / back to draft")
    return d.svg()


def d_ops_flow():
    d = Flow(900, 330)
    d.text(14, 16, "Online registration (candidate)", 12, NAVY, 700, anchor="start")
    d.node("a", 14, 30, 150, 52, "Order paid", "ok", "pill"); d.node("b", 220, 30, 190, 52, "registration.activated", "api")
    d.node("c", 470, 30, 190, 52, "Entitlements per\nsubject granted", "api"); d.node("d", 720, 30, 166, 52, "All LMs open", "ok", "pill")
    d.link("a", "b", color=GREEN); d.link("b", "c", color=GREEN); d.link("c", "d", color=GREEN)
    d.text(14, 118, "Offline registration (staff · order:offline)", 12, NAVY, 700, anchor="start")
    d.node("e", 14, 132, 170, 60, "Pick student, course,\nenter receipt reference", "warn"); d.node("f", 240, 132, 190, 60, "Order (provider=offline)\nmarked paid", "api")
    d.node("g", 490, 132, 190, 60, "Audit event +\nregistration active", "api"); d.node("h", 740, 132, 146, 60, "Candidate gets\naccess", "ok")
    d.link("e", "f", color=INDIGO); d.link("f", "g", color=INDIGO); d.link("g", "h", color=GREEN)
    d.text(14, 230, "Refund / cancel (staff · order:refund)", 12, NAVY, 700, anchor="start")
    d.node("i", 14, 244, 170, 60, "Order detail →\nfull or partial amount", "warn"); d.node("j", 240, 244, 190, 60, "Gateway refund\n+ Refund row", "api")
    d.node("k", 490, 244, 190, 60, "Full refund?", "warn", "dia"); d.node("l", 740, 236, 146, 36, "Access revoked", "bad"); d.node("m", 740, 280, 146, 36, "Partial: access kept", "ok")
    d.link("i", "j", color=INDIGO); d.link("j", "k", color=INDIGO); d.link("k", "l", "yes", ROSE, mode="h"); d.link("k", "m", "no", GREEN, mode="h")
    return d.svg()


def d_privacy():
    d = Flow(900, 250)
    d.node("a", 10, 90, 160, 70, "Candidate files request", "ui", sub="Profile → Your data rights")
    d.node("b", 220, 90, 170, 70, "DataRequest row", "api", sub="due date by type")
    d.node("c", 440, 90, 170, 70, "Staff queue", "warn", sub="/admin/data-requests")
    d.node("d", 670, 20, 210, 60, "Access: JSON export", "ok", sub="/me/data-export")
    d.node("e", 670, 100, 210, 60, "Erasure: pseudonymise", "bad", sub="orders kept for accounts")
    d.node("f", 670, 180, 210, 60, "Correction · grievance\nnomination", "std", size=12)
    d.link("a", "b", color=INDIGO); d.link("b", "c", color=INDIGO); d.link("c", "d", color=GREEN); d.link("c", "e", color=ROSE); d.link("c", "f", color=MUTED)
    d.text(220, 200, "Service levels: access 15 d · correction 7 d · erasure 30 d · grievance 15 d · nomination 7 d", 11, MUTED, anchor="start", italic=True)
    return d.svg()


# ============================================================ content
def build():
    o = []
    o.append(h1("0", "Overview", "What the platform is, how it is built, and how to read this guide."))
    o.append(h2("0.1", "The platform at a glance"))
    o.append(p("<b>CFA Learning Hub</b> by Karan Sir Classes is a learning-management system for the CFA Level I exam. Candidates register and pay for a course, then study 56 learning modules (LMs) across 10 subjects with class videos, notes and PDFs. They test themselves with chapter quizzes, subject tests and custom quizzes, revise with spaced-repetition flashcards, and track progress. Staff author and publish content; admins run registrations, payments, people and compliance.", "lead"))
    f = C.F
    o.append(kpi([("118", "API endpoints", INDIGO), ("37", "database tables", AMBER), ("35", "web pages (routes)", TEAL), ("5", "roles · 32 permissions", VIOLET),
                  ("12", "backend modules", NAVY), ("56", "learning modules", GREEN), ("32", "automated tests", ROSE), ("15 min", "access-token life", INDIGO)]))
    o.append(fig(d_system_context(), "System context: three kinds of user, one web app, one API service, one database. Purple boxes are external services."))
    o.append(h3("Technology in one table"))
    o.append(table(["Layer", "Choice", "Why it matters"], [
        ["Web", "Next.js 16 · React 19 · TypeScript 5.9", "Single origin. The browser only talks to the web host, which proxies <code>/api/*</code> to FastAPI. No CORS, simple cookies."],
        ["API", "FastAPI · Pydantic 2 · Python 3.12", "Typed request/response contracts, async I/O, one process per container worker."],
        ["Data", "PostgreSQL 16 · SQLAlchemy 2 (async) · Alembic", "Relational integrity (58 foreign keys), JSONB for flexible content, versioned migrations."],
        ["Auth", "OTP · password + TOTP · JWT cookies · Argon2id", "Mobile-first sign-in for candidates; MFA-enforced staff login."],
        ["Payments", "Razorpay (live) · built-in mock gateway (demo)", "Webhook-driven, idempotent, amount-verified."],
        ["Hosting", "Docker image on Render (current) · AWS ap-south-1 (target)", "One container runs both processes today; stateless tiers scale out later."]],
        widths=["14%", "34%", "52%"]))
    o.append(callout("info", "How this guide was produced", "Every number here is read from the repository: endpoints from the router source, tables from the SQLAlchemy models, permissions from <code>rbac.py</code>, token lifetimes from <code>config.py</code>. Screenshots are real captures of the running application. Where a figure is a <i>target</i> or <i>model</i> (for example capacity), it is labelled as such."))
    o.append(h2("0.2", "How to read this guide"))
    o.append(table(["You are…", "Start with", "Then"], [
        ["Product owner / trainer", "Part 1 · UI workflows", "Part 5 for what protects candidate data"],
        ["Backend / frontend engineer", "Part 2 · Backend mapping", "Part 3 · API, database and UI tables"],
        ["DevOps / SRE", "Part 2 §2.5–2.6 (deployment)", "Part 4 · Scaling and performance"],
        ["Security / compliance reviewer", "Part 5 · Authentication", "Part 1 §1.11 (privacy flows)"]], widths=["28%", "36%", "36%"]))

    # ============================================================ PART 1
    o.append(h1("1", "UI workflows", "How candidates, staff and admins move through the product, screen by screen."))
    o.append(h2("1.1", "Who uses the platform"))
    o.append(p("Three audiences share one application. The menu a person sees is built from the permissions their roles carry, so a candidate never sees the staff console and an author never sees refunds."))
    o.append(fig(d_roles(), "Roles and how they combine. Permission counts are taken from <code>core/rbac.py</code>."))
    o.append(table(["Audience", "Roles", "Primary goals", "Home screen"], [
        ["Candidate", "student", "Pass CFA Level I: learn, practise, revise, track progress. Pay and get receipts. Control personal data.", "<code>/dashboard</code>"],
        ["Staff", "author, reviewer", "Author: write notes, upload videos/PDFs, write questions and flashcards. Reviewer: publish content and read progress reports.", "<code>/admin</code>"],
        ["Admin", "admin, super_admin", "Run the business: courses and fees, registrations, orders and refunds, users and batches, privacy requests, audit trail. Super admin also assigns admins.", "<code>/admin</code>"]],
        widths=["13%", "17%", "52%", "18%"]))
    o.append(h2("1.2", "Navigation maps"))
    o.append(h3("Candidate application"))
    o.append(fig(d_sitemap_candidate(), "Candidate site map: 4 zones, 20 pages. Public pages need no account; everything in the right two zones needs sign-in."))
    o.append(h3("Staff console"))
    o.append(fig(d_sitemap_staff(), "Staff console: 12 menu items grouped by job. Each menu item appears only when the user holds the permission shown beneath its group."))
    o.append(h2("1.3", "The candidate journey"))
    o.append(fig(d_journey(), "End-to-end candidate journey from discovery to progress tracking."))
    o.append(shots2([("home", "/"), ("courses", "/courses")], "Public entry: the home page and the course catalogue (live capture)."))

    o.append(h2("1.4", "Workflow C1 · Sign-in and sign-up"))
    o.append(p("Candidates never create a password. A one-time code sent to their mobile proves ownership, and the same screen handles both existing and new accounts. Email OTP exists in the API for later use."))
    o.append(fig(d_login(), "Sign-in decision flow. Diamonds are server decisions; red boxes are error states the UI explains in plain language.", wide=True))
    o.append(shots2([("login_mobile", "/login"), ("login_otp", "/login  (code step)")], "Step 1: mobile number. Step 2: six-digit code. Local and demo environments echo the code on screen; production never does."))
    o.append(shot("signup_form", "/login  (new account)", "First-time candidates complete a short form. Date of birth is used only to decide whether guardian consent is needed."))
    o.append(table(["Rule", "Value", "Source"], [
        ["Code validity", "5 minutes, single use", "<code>otp_ttl_seconds=300</code>"],
        ["Code requests", "5 per hour per mobile or email", "<code>otp_max_requests_per_hour</code>"],
        ["Wrong guesses", "5 per code, then a new code is required", "<code>otp_max_attempts</code>"],
        ["Devices", "2 active sessions; the oldest ends when a third signs in", "<code>student_max_sessions</code> (BR-ACC-05)"],
        ["Mobile format", "Indian numbers only: +91 followed by 10 digits starting 6–9", "<code>MOBILE_RE</code>"]], widths=["22%", "46%", "32%"]))

    o.append(h2("1.5", "Workflow C2 · Under-18 candidates and guardian consent"))
    o.append(p("Under India's DPDP rules, a child's data needs a parent's verifiable consent. A candidate whose date of birth gives an age below 18 gets status <code>pending_guardian</code>. They can sign in and see <code>/pending-consent</code> but cannot register, pay or study until the guardian approves."))
    o.append(fig(d_guardian(), "Guardian consent: the guardian proves identity with their own OTP; consent is stored with actor = guardian.", wide=True))

    o.append(h2("1.6", "Workflow C3 · Choosing, registering and paying"))
    o.append(shots2([("course_detail", "/courses/CFA-L1-MAY27"), ("register_form", "/register/CFA-L1-MAY27")], "Course detail with fee and inclusions, then the registration form (name, email, city, qualification, target exam)."))
    o.append(fig(d_payment(), "Registration and payment. Access opens when the signed gateway webhook arrives; the browser callback is only a convenience and is re-verified with the gateway.", wide=True))
    o.append(shots2([("mock_gateway", "/mock-gateway  (demo only)"), ("checkout_receipt", "/checkout/[orderId]")], "Demo gateway and the receipt page. In production the candidate pays on Razorpay's hosted checkout; the receipt page and numbering (KSC-year-number) are identical."))
    o.append(callout("key", "Why this is safe", "Orders are idempotent (the same payment applied twice changes nothing), amounts are compared to the order (mismatch is flagged, never granted), and an unpaid order is reused for 30 minutes so a refresh cannot create duplicate charges."))

    o.append(h2("1.7", "Workflow C4 · Learning"))
    o.append(shot("s_dashboard", "/dashboard", "Dashboard: continue where you left off, plus a progress ring for each of the 10 subjects."))
    o.append(shot("s_lm", "/learn/qm", "LM view: lessons on the left, tabs for resources, flashcards, notes, chapter quiz, revision sheet and LOS; action bar for bookmark, revision log, mark as learned."))
    o.append(fig(d_learn_loop(), "The learning loop. No step blocks another: pass marks are advice, not gates."))
    o.append(table(["Behaviour", "Rule", "Where enforced"], [
        ["Resource completion", "A video or PDF counts as done at ≥ 90% watched (merged watched intervals, so skipping back does not double count)", "<code>progress/service.py</code> COMPLETION_THRESHOLD"],
        ["Mark as learned", "Allowed any time; can be undone for 24 hours", "<code>lm_progress.learned_undo_until</code>"],
        ["Revision log", "Counted once per LM per day, so spamming the button does not inflate numbers", "unique index <code>uq_revision_counted_per_day</code>"],
        ["Access to content", "An LM opens only if the candidate holds an active entitlement for its subject", "<code>enrolment.assert_entitled</code>"],
        ["Video / PDF delivery", "Signed link that expires in 2 hours; a watermark with student code and last 4 digits of mobile is shown", "<code>/resources/{id}/playback</code>"]],
        widths=["20%", "52%", "28%"]))
    o.append(C.content_chart())

    o.append(h2("1.8", "Workflow C5 · Tests and quizzes"))
    o.append(table(["Test", "Questions", "Timing", "Advisory pass mark", "Started from"], [
        ["Chapter quiz", "10 (min 3 available)", "90 s per question", "80%", "LM view → Chapter quiz"],
        ["Subject (master) test", "50", "90 s per question", "75%", "Custom Quiz → Subject tests"],
        ["Custom quiz", "Your choice", "Optional timer", "none", "Custom Quiz: subjects, chapters, difficulty (E/M/H), conceptual / numerical, practice or assessment"]],
        widths=["20%", "16%", "18%", "16%", "30%"]))
    o.append(shots2([("s_practice", "/practice"), ("s_test_answered", "/test/[attemptId]")], "Custom quiz builder with live pool counts, and the attempt screen: timer, question palette, flag for review, autosave."))
    o.append(fig(d_attempt(), "Attempt life cycle. Answers autosave; the server grades; a missed deadline auto-submits."))
    o.append(callout("key", "Answer keys stay on the server", "In assessment mode the correct answer and explanation are not sent to the browser until that question is submitted. The attempt stores a snapshot of each question, so later edits by staff never change a past result."))
    o.append(shot("s_test_result", "/test/[attemptId]  (after submit)", "Result screen: score, pass-mark guidance, review of each question with explanation, and a retake that draws unseen questions first."))

    o.append(h2("1.9", "Workflow C6 · Flashcards and spaced repetition"))
    o.append(p("Cards are grouped into decks by subject. After flipping a card the candidate rates it <b>Known</b>, <b>Needs revision</b> or <b>Difficult</b>. A modified SM-2 scheduler sets the next due date."))
    o.append('<div class="grid2">' + fig(C.srs_chart(), "Interval grows after every <i>Known</i>: 1, 3, then roughly × ease (2.5).") + table(["Rating", "Effect"], [
        ["Known", "Interval 1 d → 3 d → previous × ease"], ["Needs revision", "Interval × 1.2, ease − 0.15"],
        ["Difficult", "Back to 1 day, ease − 0.2, counts a lapse"], ["Floor", "Ease never below 1.3"]], "tight") + "</div>")
    o.append(shots2([("s_flashcards", "/flashcards"), ("s_flashcard_session", "/flashcards  (study session)")], "Deck list with due counts and the study card."))

    o.append(h2("1.10", "Workflow C7 · Search, bookmarks, orders and profile"))
    o.append(shots2([("s_profile", "/profile"), ("s_orders", "/orders")], "Profile page: details, signed-in devices (end any session), privacy choices, data-rights requests. Orders page: every receipt."))
    o.append(ul(["<b>Search</b> (<code>/search?q=</code>) finds learning modules (by title or summary) and published notes (PostgreSQL full-text search). Results outside the candidate's subjects show the title but no text snippet.", "<b>Bookmarks</b> save a note, a video position or an LM with an optional note (500 characters).",
                 "<b>Devices</b> lists active sessions with a device label such as “Chrome on Windows”; ending one revokes its refresh token immediately."]))

    o.append(h2("1.11", "Staff and admin workflows"))
    o.append(h3("Workflow S0 · Signing in to the console"))
    o.append(p("Staff sign in at <code>/staff/login</code> with email and password, then a six-digit authenticator code. First-time staff are walked through enrolling an authenticator app. Outside local development, MFA is mandatory and the server refuses to start without it."))
    o.append(fig(d_staff_login(), "Staff sign-in with enforced second factor."))
    o.append(shots2([("staff_login", "/staff/login"), ("a_overview", "/admin")], "Staff sign-in and the overview dashboard (students, active registrations, revenue, open data requests)."))
    o.append(h3("Workflow S1 · Content and question lifecycle"))
    o.append(fig(d_content_flow(), "Separation of duties: authors write, reviewers and admins publish. Published content is versioned; a new version never replaces what students see until it is published."))
    o.append(shots2([("a_catalog", "/admin/catalog"), ("a_lm_editor", "/admin/lms/[id]")], "Catalogue list per subject and the LM editor (topics, learning outcome statements, notes, video and PDF upload)."))
    o.append(shots2([("a_questions", "/admin/questions"), ("a_flashcards", "/admin/flashcards")], "Question bank and flashcard management."))
    o.append(callout("info", "Upload safety", "Videos and PDFs are accepted only for allowed MIME types; PDFs must start with the <code>%PDF</code> signature; size is capped at 500 MB; licensed third-party material needs a licence reference. An antivirus scan step is planned before publish (not yet implemented)."))
    o.append(h3("Workflow S2 · Courses, registrations, payments"))
    o.append(fig(d_ops_flow(), "Three money flows an admin handles: online (automatic), offline (manual entry) and refund."))
    o.append(shots2([("a_courses", "/admin/courses"), ("a_orders", "/admin/orders")], "Courses and fees, and the orders list with status filters."))
    o.append(shots2([("a_registrations", "/admin/registrations"), ("a_order_detail", "/admin/orders/[id]")], "Registrations (including offline entry and cancel) and the order detail with refund action."))
    o.append(h3("Workflow S3 · People, batches and access"))
    o.append(shots2([("a_users", "/admin/users"), ("a_user_detail", "/admin/users/[id]")], "User directory and user detail: roles, entitlements (grant or revoke), sessions (force sign-out), deactivate."))
    o.append(shots2([("a_batches", "/admin/batches"), ("a_reports", "/admin/reports")], "Batches (cohorts with start/end dates) and the progress report per course."))
    o.append(h3("Workflow S4 · Privacy requests and audit"))
    o.append(fig(d_privacy(), "Data-subject requests under DPDP: five request types, each with a due date."))
    o.append(shots2([("a_data", "/admin/data-requests"), ("a_audit", "/admin/audit")], "Data-request queue and the audit log. “Verify chain” recomputes the hash chain to prove no row was altered (see Part 5)."))
    o.append(h2("1.12", "Who can open which screen"))
    o.append(p("The staff menu is filtered by permission. This table is the contract between roles and screens; the same permissions guard the underlying API calls."))
    o.append(table(["Screen", "Permission", "Author", "Reviewer", "Admin", "Super"], [
        ["Overview · Progress report", "report:read", "–", "✓", "✓", "✓"], ["Catalogue & content · Question bank · Flashcards", "catalog:read_admin", "✓", "✓", "✓", "✓"],
        ["Courses & fees", "course:manage", "–", "–", "✓", "✓"], ["Registrations · Payments & refunds", "order:read", "–", "–", "✓", "✓"],
        ["Users & staff", "user:read", "–", "–", "✓", "✓"], ["Batches", "batch:manage", "–", "–", "✓", "✓"],
        ["Data requests", "data_request:process", "–", "–", "✓", "✓"], ["Audit log", "audit:read", "–", "–", "✓", "✓"]],
        "tight", widths=["38%", "22%", "10%", "10%", "10%", "10%"]))
    o.append(fig(C.perm_heatmap(), "Full permission matrix: 32 permissions grouped by purpose, one row per role.", wide=True))
    return "".join(o)
