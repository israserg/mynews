"""Build dist/mynews-<version>.zip: the deployment package (app/, requirements.txt, VERSION)."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
version = (ROOT / "VERSION").read_text().strip()
out = ROOT / "dist" / f"mynews-{version}.zip"
out.parent.mkdir(exist_ok=True)

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted((ROOT / "app").rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            z.write(p, p.relative_to(ROOT).as_posix())
    z.write(ROOT / "requirements.txt", "requirements.txt")
    z.write(ROOT / "VERSION", "VERSION")

print(out)
