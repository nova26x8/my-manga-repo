"""Generate index.json (with SHA-256 checksums) from the files in sources/.

Run from the repo root, using your own GitHub details:

    python tools/make_index.py --base-url https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main

Run it again every time you change a file in sources/ (and bump that file's "version").
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["schema_version", "id", "name", "version", "languages", "description", "domains"]


def fail(message):
    sys.exit(f"Error: {message}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--base-url",
        default="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main",
        help="Public URL of the repo root (no trailing slash).",
    )
    parser.add_argument("--name", default="Official APIs", help="Repository name shown to users.")
    parser.add_argument("--repo-version", type=int, default=1)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    if not base.startswith("https://"):
        fail("--base-url must start with https://")

    sources, seen_ids = [], set()
    for path in sorted((ROOT / "sources").glob("*.json")):
        raw = path.read_bytes()
        if b"\r\n" in raw:
            fail(f"{path.name} has Windows line endings (CRLF). Save it with LF endings, "
                 "otherwise the checksum will not match after upload.")

        data = json.loads(raw)
        missing = [key for key in REQUIRED if key not in data]
        if missing:
            fail(f"{path.name} is missing: {', '.join(missing)}")
        if data["id"] in seen_ids:
            fail(f"duplicate source id: {data['id']}")
        seen_ids.add(data["id"])

        for domain in data["domains"]:
            if not isinstance(domain, str) or "/" in domain or ":" in domain or not domain:
                fail(f"{path.name}: domains must be plain host names, got {domain!r}")

        languages = data["languages"]
        sources.append(
            {
                "id": data["id"],
                "name": data["name"],
                "language": languages[0] if len(languages) == 1 else "multi",
                "version": data["version"],
                "url": f"{base}/sources/{path.name}",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "domains": data["domains"],
                "description": data["description"],
            }
        )

    if not sources:
        fail("no source files found in sources/")

    index = {"name": args.name, "version": args.repo_version, "sources": sources}
    with open(ROOT / "index.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote index.json with {len(sources)} source(s).")


if __name__ == "__main__":
    main()
