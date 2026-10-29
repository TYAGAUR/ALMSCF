"""Run with the backend venv from backend/: extracts real facts (routes, tables, RBAC) to facts.json."""
import json, pathlib, re, sys
sys.path.insert(0, ".")
import app.main  # noqa: F401  (registers all models)
from app.core.db import Base
from app.core import rbac

out = {"tables": {}, "rbac": {}, "routes": []}
for name, t in sorted(Base.metadata.tables.items()):
    out["tables"][name] = {
        "cols": [{"n": c.name, "t": str(c.type).split("(")[0], "pk": c.primary_key, "null": c.nullable,
                  "uq": bool(c.unique)} for c in t.columns],
        "fks": [{"c": fk.parent.name, "to": fk.column.table.name, "on": fk.ondelete} for fk in t.foreign_keys],
        "idx": len(t.indexes),
    }
out["rbac"] = {k: sorted(v) for k, v in rbac.ROLE_PERMISSIONS.items()}

root = pathlib.Path("app/modules")
for f in root.rglob("*.py"):
    t = f.read_text(encoding="utf8")
    m = re.search(r"APIRouter\((.*?)\)", t)
    if not m:
        continue
    pre = re.search(r'prefix="([^"]*)"', m.group(1)); pre = pre.group(1) if pre else ""
    for d in re.finditer(r'@router\.(get|post|put|patch|delete)\("([^"]*)"[^\n]*\n((?:(?!\n@router|\n\n\n).)*)', t, re.S):
        sig = d.group(3)[:700].split('\n    """')[0]
        p = re.findall(r'require\(([^)]*)\)', sig)
        if p:
            a = ("perm", p[0].replace('"', "").split(",")[0].strip())
        elif "allow_pending" in sig: a = ("pending", "")
        elif "optional_user" in sig: a = ("optional", "")
        elif "current_user" in sig: a = ("session", "")
        elif "/admin/resources" in pre + d.group(2) and d.group(1) == "post": a = ("perm", "resource:write")
        else: a = ("public", "")
        mod = f.parent.name if f.parent.name != "admin" else "admin"
        mod = f"admin/{f.stem}" if f.parent.name == "admin" else f.parent.name
        out["routes"].append({"mod": mod, "m": d.group(1).upper(), "path": "/api/v1" + pre + d.group(2),
                              "auth": a[0], "perm": a[1]})
out["routes"] += [{"mod": "system", "m": "GET", "path": "/api/v1/healthz", "auth": "public", "perm": ""},
                  {"mod": "system", "m": "GET", "path": "/api/v1/readyz", "auth": "public", "perm": ""}]
pathlib.Path(sys.argv[1]).write_text(json.dumps(out, indent=1), encoding="utf8")
print(len(out["routes"]), "routes", len(out["tables"]), "tables")
