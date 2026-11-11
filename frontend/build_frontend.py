"""Build the static portal and inject its public API URL."""

import os
from pathlib import Path
import shutil


source_dir = Path(__file__).resolve().parent
output_dir = source_dir / "dist"
api_base_url = os.environ.get("API_BASE_URL", "").strip()
if not api_base_url:
    raise RuntimeError("API_BASE_URL must be configured for the frontend build")
if "://" not in api_base_url:
    api_base_url = f"https://{api_base_url}"

if output_dir.exists():
    shutil.rmtree(output_dir)
output_dir.mkdir()

for pattern in ("*.html", "*.css", "*.js", "*.svg"):
    for source_file in source_dir.glob(pattern):
        if source_file.name == "config.js":
            continue
        shutil.copy2(source_file, output_dir / source_file.name)

(output_dir / "config.js").write_text(
    f"window.NHRX_API_BASE = {api_base_url!r};\n",
    encoding="utf-8",
)
