"""Matplotlib charts built from real extracted facts. Each returns an <img> tag with an inline SVG data URI."""
import base64, io, json, math, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

HERE = pathlib.Path(__file__).parent
F = json.loads((HERE / "facts.json").read_text(encoding="utf8"))

NAVY = "#1B2559"; INDIGO = "#4F5BD5"; TEAL = "#17A2A0"; AMBER = "#F2A33A"; ROSE = "#E5484D"
GREEN = "#2E9E6B"; INK = "#1F2433"; MUTED = "#6B7390"; GRID = "#E3E7F3"; VIOLET = "#7C5CD6"

names = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Segoe UI" if "Segoe UI" in names else "DejaVu Sans", "svg.fonttype": "none",
    "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
    "axes.titlesize": 12, "axes.labelsize": 10, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
})


def emit(fig, alt=""):
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)
    b = base64.b64encode(buf.getvalue().encode()).decode()
    return f'<img class="chart" alt="{alt}" src="data:image/svg+xml;base64,{b}"/>'


# ---------------------------------------------------------------- API
MOD_LABEL = {"auth": "Auth & profile", "privacy": "Privacy & consent", "commerce": "Courses & registration",
             "payments": "Payments", "learning": "Learning & progress", "qbank": "Tests & question bank",
             "flashcards": "Flashcards", "admin/users": "Admin · users & batches", "admin/commerce": "Admin · commerce",
             "admin/catalog": "Admin · catalogue & content", "admin/ops": "Admin · ops & audit", "system": "System"}
METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
MCOL = {"GET": TEAL, "POST": INDIGO, "PUT": AMBER, "PATCH": VIOLET, "DELETE": ROSE}


def api_by_module():
    mods = list(MOD_LABEL)
    cnt = {m: {k: 0 for k in METHODS} for m in mods}
    for r in F["routes"]:
        cnt[r["mod"]][r["m"]] += 1
    order = sorted(mods, key=lambda m: sum(cnt[m].values()))
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    left = np.zeros(len(order))
    for k in METHODS:
        v = np.array([cnt[m][k] for m in order])
        ax.barh([MOD_LABEL[m] for m in order], v, left=left, color=MCOL[k], label=k, height=0.66, edgecolor="white")
        for i, (l, x) in enumerate(zip(left, v)):
            if x >= 2: ax.text(l + x / 2, i, int(x), ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        left += v
    for i, t in enumerate(left): ax.text(t + 0.4, i, int(t), va="center", color=NAVY, fontweight="bold", fontsize=9.5)
    ax.set_xlabel("Endpoints"); ax.legend(ncol=5, frameon=False, loc="lower right", fontsize=9)
    ax.grid(axis="y", visible=False); ax.set_xlim(0, max(left) + 4)
    ax.set_title("118 endpoints by module and HTTP method", loc="left")
    return emit(fig, "Endpoints by module")


def api_by_auth():
    c = {}
    for r in F["routes"]: c[r["auth"]] = c.get(r["auth"], 0) + 1
    labels = {"perm": "Permission required (RBAC)", "public": "Public / token-in-URL", "pending": "Signed in (incl. pending guardian)",
              "session": "Signed in & active", "optional": "Optional sign-in"}
    cols = {"perm": INDIGO, "public": AMBER, "pending": TEAL, "session": GREEN, "optional": VIOLET}
    order = ["perm", "public", "pending", "session", "optional"]
    fig, ax = plt.subplots(figsize=(5.4, 3.9))
    w, _ = ax.pie([c[k] for k in order], colors=[cols[k] for k in order], startangle=90, counterclock=False,
                  wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2))
    ax.text(0, 0.06, "118", ha="center", fontsize=26, fontweight="bold", color=NAVY)
    ax.text(0, -0.2, "endpoints", ha="center", fontsize=10, color=MUTED)
    ax.legend(w, [f"{labels[k]} · {c[k]}" for k in order], loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=9)
    ax.set_title("Who may call an endpoint", loc="left"); ax.grid(False)
    return emit(fig, "Access class donut")


def perm_heatmap():
    roles = ["student", "author", "reviewer", "admin", "super_admin"]
    perms = sorted({p for r in roles for p in F["rbac"][r]})
    groups = {"Learner": ["profile:self", "consent:self", "data_request:create", "progress:write", "bookmark:self",
                          "course:register", "order:self", "test:take", "flashcard:review"],
              "Content": ["catalog:read_admin", "catalog:write", "content:write", "resource:write", "qbank:write",
                          "flashcard:write", "staff:console"],
              "Review/publish": ["content:publish", "resource:publish", "qbank:publish", "catalog:publish", "report:read"],
              "Operations": ["user:read", "user:write", "batch:manage", "enrolment:manage", "entitlement:grant", "course:manage",
                             "order:read", "order:refund", "order:offline", "session:revoke", "data_request:process"],
              "Governance": ["audit:read", "role:assign_admin", "settings:global", "audit:read_security"]}
    order = [p for g in groups.values() for p in g if p in perms]
    M = np.array([[1 if p in F["rbac"][r] else 0 for p in order] for r in roles])
    fig, ax = plt.subplots(figsize=(8.8, 3.1))
    from matplotlib.colors import ListedColormap
    ax.imshow(M, cmap=ListedColormap(["#F1F3FA", INDIGO]), aspect="auto")
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=65, ha="right", fontsize=7.8)
    ax.set_yticks(range(len(roles))); ax.set_yticklabels([r.replace("_", " ") for r in roles], fontsize=9.5)
    ax.set_xticks(np.arange(-.5, len(order)), minor=True); ax.set_yticks(np.arange(-.5, len(roles)), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.6); ax.grid(which="major", visible=False)
    ax.tick_params(which="both", length=0)
    for sp in ax.spines.values(): sp.set_visible(False)
    i = 0
    for g, ps in groups.items():
        k = len([p for p in ps if p in perms])
        ax.text(i + k / 2 - .5, -1.05, g, ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
        if i: ax.axvline(i - .5, color=NAVY, lw=1.2, alpha=.5)
        i += k
    return emit(fig, "Role permission heatmap")


def perm_counts():
    roles = ["student", "author", "reviewer", "admin", "super_admin"]
    v = [len(F["rbac"][r]) for r in roles]
    cols = [TEAL, VIOLET, AMBER, INDIGO, NAVY]
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    b = ax.bar([r.replace("_", " ") for r in roles], v, color=cols, width=.62)
    for x, y in zip(b, v): ax.text(x.get_x() + x.get_width() / 2, y + .5, y, ha="center", color=NAVY, fontweight="bold")
    ax.set_ylabel("Permissions held"); ax.grid(axis="x", visible=False); ax.set_ylim(0, 37)
    ax.set_title("Permissions per role", loc="left")
    return emit(fig, "Permissions per role")


# ---------------------------------------------------------------- DB
DOMAINS = {"Identity & access": ["users", "user_roles", "guardians", "sessions", "otp_challenges"],
           "Catalogue & content": ["subjects", "learning_modules", "topics", "los", "content_items", "content_versions", "resources"],
           "Commerce & enrolment": ["courses", "course_subjects", "registrations", "batches", "enrolments", "entitlements",
                                    "orders", "payments", "payment_events", "refunds"],
           "Learning activity": ["lm_progress", "resource_progress", "revision_logs", "eoc_entries", "bookmarks",
                                 "flashcards", "card_reviews"],
           "Assessment": ["questions", "test_attempts", "attempt_items"],
           "Privacy & governance": ["consents", "data_requests", "audit_log", "outbox", "settings"]}
DCOL = {"Identity & access": NAVY, "Catalogue & content": INDIGO, "Commerce & enrolment": AMBER,
        "Learning activity": TEAL, "Assessment": VIOLET, "Privacy & governance": ROSE}


def tables_chart():
    rows = []
    for d, ts in DOMAINS.items():
        for t in ts: rows.append((t, len(F["tables"][t]["cols"]), d))
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    ax.barh([r[0] for r in rows], [r[1] for r in rows], color=[DCOL[r[2]] for r in rows], height=.68)
    for i, r in enumerate(rows): ax.text(r[1] + .25, i, r[1], va="center", fontsize=8.5, color=NAVY, fontweight="bold")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=d) for d, c in DCOL.items()], frameon=False, loc="lower right", fontsize=9)
    ax.set_xlabel("Columns"); ax.grid(axis="y", visible=False)
    ax.set_title("37 tables · 399 columns · 58 foreign keys", loc="left")
    return emit(fig, "Columns per table")


def domain_donut():
    d = {k: len(v) for k, v in DOMAINS.items()}
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    w, _ = ax.pie(d.values(), colors=[DCOL[k] for k in d], startangle=90, counterclock=False,
                  wedgeprops=dict(width=.4, edgecolor="white", linewidth=2))
    ax.text(0, 0, "37\ntables", ha="center", va="center", fontsize=15, fontweight="bold", color=NAVY)
    ax.legend(w, [f"{k} · {v}" for k, v in d.items()], loc="center left", bbox_to_anchor=(1, .5), frameon=False, fontsize=9)
    ax.grid(False)
    return emit(fig, "Tables per domain")


# ---------------------------------------------------------------- content footprint
def content_chart():
    subj = [("Ethics", 4), ("Quant", 5), ("Econ", 4), ("Corp", 5), ("FSA", 6), ("Equity", 8), ("Fixed Inc", 6),
            ("Deriv", 10), ("Alt Inv", 4), ("Port Mgmt", 4)]
    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    cols = [NAVY, INDIGO, VIOLET, TEAL, GREEN, AMBER, "#E07B39", ROSE, "#8A93B8", "#3B82C4"]
    b = ax.bar([s[0] for s in subj], [s[1] for s in subj], color=cols, width=.66)
    for x, s in zip(b, subj): ax.text(x.get_x() + x.get_width() / 2, s[1] + .2, s[1], ha="center", color=NAVY, fontweight="bold")
    ax.set_ylabel("Learning modules (LMs)"); ax.grid(axis="x", visible=False); ax.set_ylim(0, 12)
    ax.set_title("Catalogue footprint: 10 subjects · 56 learning modules", loc="left")
    return emit(fig, "LMs per subject")


# ---------------------------------------------------------------- security / auth
def lifetimes():
    items = [("OTP code", 5 * 60, "DB-hashed, 5 attempts", TEAL), ("MFA step-up token", 5 * 60, "JWT purpose=mfa", VIOLET),
             ("Access token (cookie)", 15 * 60, "JWT purpose=access", INDIGO), ("Signup token", 20 * 60, "JWT purpose=signup", VIOLET),
             ("Order reuse window", 30 * 60, "unpaid order reused", AMBER), ("Signed media URL", 2 * 3600, "JWT purpose=media", TEAL),
             ("Staff session (refresh)", 12 * 3600, "rotating, HttpOnly", NAVY), ("Guardian consent link", 7 * 86400, "JWT purpose=guardian", VIOLET),
             ("Student session (refresh)", 30 * 86400, "rotating, HttpOnly", NAVY)]
    items.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.barh([i[0] for i in items], [i[1] for i in items], color=[i[3] for i in items], height=.62)
    ax.set_xscale("log")
    ticks = [60, 300, 900, 3600, 6 * 3600, 86400, 7 * 86400, 30 * 86400]
    ax.set_xticks(ticks); ax.set_xticklabels(["1 min", "5 min", "15 min", "1 h", "6 h", "1 day", "7 days", "30 days"])
    ax.minorticks_off(); ax.set_xlim(150, 5e6)
    def fmt(s):
        return f"{s // 60} min" if s < 3600 else (f"{s // 3600} h" if s < 86400 else f"{s // 86400} days")
    for i, it in enumerate(items): ax.text(it[1] * 1.12, i, f"{fmt(it[1])}  ·  {it[2]}", va="center", fontsize=8.6, color=NAVY)
    ax.grid(axis="y", visible=False); ax.set_xlabel("Lifetime (log scale)")
    ax.set_title("How long each credential or token lives", loc="left")
    return emit(fig, "Token lifetimes")


def lockouts():
    labels = ["OTP requests\n/ hour / destination", "OTP wrong guesses\n/ challenge", "Staff wrong passwords\n→ 15 min lock",
              "Concurrent student\nsessions"]
    vals = [5, 5, 5, 2]
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    b = ax.bar(labels, vals, color=[TEAL, TEAL, ROSE, INDIGO], width=.55)
    for x, v in zip(b, vals): ax.text(x.get_x() + x.get_width() / 2, v + .15, v, ha="center", fontweight="bold", color=NAVY)
    ax.set_ylim(0, 7); ax.tick_params(axis="x", labelsize=7.6); ax.grid(axis="x", visible=False)
    ax.set_title("Brute-force and abuse limits", loc="left")
    return emit(fig, "Limits")


# ---------------------------------------------------------------- performance
def slo_chart():
    items = [("API read p95 (SLO-2)", 400, TEAL), ("Progress write p95 (SLO-3)", 300, TEAL), ("Test submit p95 (SLO-3)", 1000, INDIGO),
             ("Read p99 (SLO-2)", 1000, TEAL), ("User action → rendered, p95 (SLO-5)", 2000, VIOLET),
             ("Video first frame, p90 (SLO-6)", 3000, AMBER), ("LCP mobile p75 (SLO-4)", 2500, AMBER)]
    items.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    ax.barh([i[0] for i in items], [i[1] for i in items], color=[i[2] for i in items], height=.6)
    for i, it in enumerate(items): ax.text(it[1] + 40, i, f"{it[1]/1000:g} s" if it[1] >= 1000 else f"{it[1]} ms", va="center", fontsize=9, fontweight="bold", color=NAVY)
    ax.set_xlim(0, 3600); ax.set_xlabel("Latency target (ms)"); ax.grid(axis="y", visible=False)
    ax.set_title("Latency objectives from the NFR specification (N-01)", loc="left")
    return emit(fig, "SLO latency targets")


def availability_chart():
    lv = [99.0, 99.5, 99.9, 99.95]
    mins = [(1 - x / 100) * 30 * 24 * 60 for x in lv]
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    cols = [GRID, INDIGO, GRID, GRID]
    b = ax.bar([f"{x}%" for x in lv], mins, color=cols, edgecolor=[MUTED, INDIGO, MUTED, MUTED], width=.58)
    for x, m in zip(b, mins): ax.text(x.get_x() + x.get_width() / 2, m + 8, f"{m/60:.1f} h" if m >= 60 else f"{m:.0f} min", ha="center", fontweight="bold", color=NAVY, fontsize=9.5)
    ax.annotate("SLO-1 target", (1, mins[1]), xytext=(1.6, mins[0] * .8), color=INDIGO, fontsize=9, arrowprops=dict(arrowstyle="-", color=INDIGO))
    ax.set_ylabel("Allowed downtime / month (min)"); ax.grid(axis="x", visible=False)
    ax.set_title("Availability target vs error budget", loc="left")
    return emit(fig, "Availability")


def capacity_curve():
    users = np.linspace(0, 1000, 200)
    rps = users * 0.5  # N-01: 300 concurrent ≈ 150 req/s
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    ax.plot(users, rps, color=INDIGO, lw=2.4)
    ax.fill_between(users, rps, color=INDIGO, alpha=.08)
    for u, lab, col in [(300, "Planned peak\n300 users · 150 req/s", TEAL), (500, "Contest start\n500 users", AMBER),
                        (900, "3× headroom target\n900 users · 450 req/s", ROSE)]:
        ax.scatter([u], [u * .5], s=60, color=col, zorder=5); ax.vlines(u, 0, u * .5, color=col, ls=":", lw=1.2)
        ax.annotate(lab, (u, u * .5), xytext=(u - 70, u * .5 + 60), fontsize=8.6, color=col, fontweight="bold", ha="right" if u > 400 else "center",
                    arrowprops=dict(arrowstyle="-", color=col, lw=.8))
    ax.set_xlabel("Concurrent users"); ax.set_ylabel("API requests / second")
    ax.set_title("Workload model: concurrent users → request rate (N-01 assumption: ~0.5 req/s per user)", loc="left", fontsize=10.5)
    ax.set_ylim(0, 560)
    return emit(fig, "Capacity model")


def littles_law():
    hold = np.linspace(10, 120, 100)  # ms of DB connection time per request
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    for pool, col in [(10, INDIGO), (20, TEAL), (40, VIOLET)]:
        ax.plot(hold, pool / (hold / 1000), color=col, lw=2.2, label=f"pool = {pool} connections" + ("  (current setting)" if pool == 10 else ""))
    ax.axhline(150, color=AMBER, ls="--", lw=1.4); ax.text(118, 160, "planned peak 150 req/s", ha="right", color="#9A6410", fontsize=9)
    ax.axhline(450, color=ROSE, ls="--", lw=1.4); ax.text(118, 460, "3× target 450 req/s", ha="right", color=ROSE, fontsize=9)
    ax.set_ylim(0, 1100); ax.set_xlim(10, 120)
    ax.set_xlabel("Average time a request holds a DB connection (ms)"); ax.set_ylabel("Max req/s per API process")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_title("Connection-pool ceiling (Little's law: throughput ≤ pool ÷ hold time)", loc="left", fontsize=10.5)
    return emit(fig, "Little's law")


def scaling_ranges():
    sv = [("Web (Next.js)", 2, 6), ("API (FastAPI)", 2, 8), ("Worker", 1, 4)]
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    for i, (n, lo, hi) in enumerate(sv):
        ax.barh(i, hi, color="#DDE2F5", height=.5); ax.barh(i, lo, color=INDIGO, height=.5)
        ax.text(lo / 2, i, f"min {lo}", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
        ax.text(hi + .15, i, f"max {hi}", va="center", color=NAVY, fontsize=9, fontweight="bold")
    ax.set_yticks(range(3)); ax.set_yticklabels([s[0] for s in sv]); ax.invert_yaxis()
    ax.set_xlim(0, 9.5); ax.set_xlabel("ECS Fargate tasks"); ax.grid(axis="y", visible=False)
    ax.set_title("Target autoscaling envelope (A-05)", loc="left")
    return emit(fig, "Autoscaling ranges")


def tests_chart():
    d = [("Auth, privacy & consent", 12), ("Payments & learning", 11), ("Tests & flashcards", 9)]
    fig, ax = plt.subplots(figsize=(5.0, 2.6))
    b = ax.barh([x[0] for x in d][::-1], [x[1] for x in d][::-1], color=[TEAL, INDIGO, VIOLET][::-1], height=.55)
    for x in b: ax.text(x.get_width() + .2, x.get_y() + x.get_height() / 2, int(x.get_width()), va="center", fontweight="bold", color=NAVY)
    ax.set_xlim(0, 15); ax.grid(axis="y", visible=False); ax.set_title("32 automated backend tests", loc="left")
    return emit(fig, "Tests")


def srs_chart():
    """Review interval growth for a card rated 'known' every time vs. one that is 'difficult' once."""
    ease = 2.5; iv = []; reps = 0; day = 0; days = [0]; ivs = []
    interval = 0
    for r in range(9):
        interval = 1 if reps == 0 else 3 if reps == 1 else max(interval + 1, round(interval * ease)); reps += 1
        day += interval; days.append(day); ivs.append(interval)
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    ax.plot(range(1, len(ivs) + 1), ivs, marker="o", color=TEAL, lw=2.2)
    for i, v in enumerate(ivs): ax.text(i + 1, v * 1.25 + 0.5, v, ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    ax.set_yscale("log"); ax.set_xlabel("Successive 'Known' reviews"); ax.set_ylabel("Next review in (days)")
    ax.set_yticks([1, 3, 10, 30, 100, 300]); ax.set_yticklabels(["1", "3", "10", "30", "100", "300"]); ax.minorticks_off()
    ax.set_title("Spaced-repetition: interval after each 'Known'", loc="left")
    return emit(fig, "SRS growth")


def mapping_heat():
    """Counts of API endpoints per UI area (rough: derived from frontend api() calls)."""
    return ""
