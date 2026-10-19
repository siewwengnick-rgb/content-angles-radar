#!/usr/bin/env python3
"""Rebuild data.json (+ embed into index.html) from OT/FF pipeline content_angles.json."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
OUT_DIR = Path("/workspace/viral-research-diy/pipeline/out")
OT_PATH = OUT_DIR / "orthotech" / "content_angles.json"
FF_PATH = OUT_DIR / "foamfresh" / "content_angles.json"
DATA_JSON = ROOT / "data.json"
INDEX_HTML = ROOT / "index.html"
TZ = ZoneInfo("Asia/Kuala_Lumpur")

YT_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?[^#]*v=|youtube\.com/shorts/|youtu\.be/)([A-Za-z0-9_-]{6,})", re.I),
]


def youtube_id(url: str | None) -> str | None:
    if not url:
        return None
    for pat in YT_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    return None


def thumb_for_refs(refs: list) -> dict:
    """Pick first YouTube thumb; else Instagram placeholder meta."""
    for r in refs or []:
        url = r.get("url") or ""
        vid = youtube_id(url)
        if vid:
            return {
                "type": "youtube",
                "youtube_id": vid,
                "url": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                "platform": r.get("platform") or "YouTube",
                "ref_title": r.get("title") or "",
                "ref_url": url,
                "views": r.get("views"),
            }
    for r in refs or []:
        url = (r.get("url") or "").lower()
        if "instagram.com" in url:
            return {
                "type": "instagram",
                "youtube_id": None,
                "url": None,
                "platform": "Instagram",
                "ref_title": r.get("title") or "",
                "ref_url": r.get("url"),
                "views": r.get("views"),
            }
    # fallback: first ref platform label
    if refs:
        r = refs[0]
        return {
            "type": "placeholder",
            "youtube_id": None,
            "url": None,
            "platform": r.get("platform") or "Ref",
            "ref_title": r.get("title") or "",
            "ref_url": r.get("url"),
            "views": r.get("views"),
        }
    return {
        "type": "placeholder",
        "youtube_id": None,
        "url": None,
        "platform": "",
        "ref_title": "",
        "ref_url": None,
        "views": None,
    }


def normalize_hooks(hooks) -> list[dict]:
    out = []
    for h in hooks or []:
        if isinstance(h, dict):
            out.append(
                {
                    "line": h.get("line") or "",
                    "hook_type": h.get("hook_type") or "",
                    "hook_type_zh": h.get("hook_type_zh") or "",
                }
            )
        elif isinstance(h, str):
            out.append({"line": h, "hook_type": "", "hook_type_zh": ""})
    return out


def tag_status(priority_score: float | None, median_perf: float | None) -> str:
    """Simple display tag — pipeline has no NEW flag on angles; mark by strength."""
    ps = float(priority_score or 0)
    mp = float(median_perf or 0)
    if ps >= 0.25 or mp >= 70:
        return "RISING"
    if ps >= 0.15:
        return "保留"
    return "观察"


def slim_refs(refs: list) -> list[dict]:
    out = []
    for r in refs or []:
        out.append(
            {
                "platform": r.get("platform") or "",
                "title": r.get("title") or "",
                "url": r.get("url") or "",
                "views": r.get("views"),
                "views_per_day": r.get("views_per_day"),
                "post_date": r.get("post_date"),
                "perf_pct": r.get("perf_pct"),
                "youtube_id": youtube_id(r.get("url")),
            }
        )
    return out


def load_brand(path: Path, brand: str, brand_name: str) -> tuple[dict, list]:
    if not path.exists():
        print(f"WARN: missing {path}", file=sys.stderr)
        return {}, []
    raw = json.loads(path.read_text(encoding="utf-8"))
    meta = {
        "generated_at_local": raw.get("generated_at_local"),
        "n_passed": raw.get("n_passed"),
        "platforms_in_data": raw.get("platforms_in_data") or {},
        "n_angles": len(raw.get("angles") or []),
    }
    items = []
    for a in raw.get("angles") or []:
        fmt = a.get("format") or {}
        if isinstance(fmt, str):
            fmt = {"name": fmt, "execution": "", "key": ""}
        hooks = normalize_hooks(a.get("hooks"))
        top_hook = hooks[0]["line"] if hooks else ""
        refs = a.get("references") or []
        thumb = thumb_for_refs(refs)
        why = a.get("why_trending") or []
        if isinstance(why, str):
            why = [why]
        items.append(
            {
                "id": f"{brand.lower()}-{a.get('angle_key') or 'x'}",
                "brand": brand,
                "brand_name": brand_name,
                "angle_key": a.get("angle_key") or "",
                "title": a.get("angle") or "",
                "pain_point": a.get("target_pain_point") or "",
                "hooks": hooks,
                "top_hook": top_hook,
                "format_name": fmt.get("name") or "",
                "format_execution": fmt.get("execution") or "",
                "format_key": fmt.get("key") or "",
                "recommended_platforms": a.get("recommended_platforms") or [],
                "why_trending": why[:4],
                "compliance": a.get("compliance") or "",
                "priority_score": a.get("priority_score"),
                "n": a.get("n"),
                "median_perf_pct": a.get("median_perf_pct"),
                "top_quartile_share": a.get("top_quartile_share"),
                "status": tag_status(a.get("priority_score"), a.get("median_perf_pct")),
                "thumb": thumb,
                "references": slim_refs(refs),
                "keywords_observed": (a.get("keywords_observed") or [])[:8],
            }
        )
    return meta, items


def build() -> dict:
    ot_meta, ot_items = load_brand(OT_PATH, "OT", "Orthotech")
    ff_meta, ff_items = load_brand(FF_PATH, "FF", "Foamfresh")
    items = ot_items + ff_items
    # sort: brand OT first then by priority desc
    items.sort(key=lambda x: (0 if x["brand"] == "OT" else 1, -(x.get("priority_score") or 0)))

    now = datetime.now(TZ)
    # prefer latest of the two pipeline stamps
    stamps = [m.get("generated_at_local") for m in (ot_meta, ff_meta) if m.get("generated_at_local")]
    generated = stamps[-1] if stamps else now.strftime("%Y-%m-%d %H:%M:%S %z")

    payload = {
        "generated_at_local": generated,
        "built_at_local": now.strftime("%Y-%m-%d %H:%M:%S %z"),
        "timezone": "Asia/Kuala_Lumpur",
        "sources": {
            "orthotech": str(OT_PATH),
            "foamfresh": str(FF_PATH),
            "orthotech_meta": ot_meta,
            "foamfresh_meta": ff_meta,
        },
        "counts": {
            "ot": len(ot_items),
            "ff": len(ff_items),
            "total": len(items),
        },
        "weekly_md": "/workspace/content_angles_test_weekly_2026-10-19.md",
        "ff_radar_pages": "https://siewwengnick-rgb.github.io/ff-radar-/",
        "angles": items,
    }
    return payload


def embed_into_index(payload: dict) -> None:
    """Keep file:// preview working: inject JSON between markers in index.html."""
    if not INDEX_HTML.exists():
        return
    html = INDEX_HTML.read_text(encoding="utf-8")
    start = "<!-- ANGLES_DATA_START -->"
    end = "<!-- ANGLES_DATA_END -->"
    blob = (
        f"{start}\n"
        f'<script type="application/json" id="angles-data">\n'
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        f"</script>\n"
        f"{end}"
    )
    if start in html and end in html:
        before, rest = html.split(start, 1)
        _, after = rest.split(end, 1)
        html = before + blob + after
    else:
        # insert before closing body
        needle = "</body>"
        if needle not in html:
            print("WARN: no embed markers and no </body>", file=sys.stderr)
            return
        html = html.replace(needle, blob + "\n" + needle, 1)
    INDEX_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build()
    DATA_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    embed_into_index(payload)
    c = payload["counts"]
    print(
        f"Wrote {DATA_JSON} — OT={c['ot']} FF={c['ff']} total={c['total']} "
        f"(generated_at_local={payload['generated_at_local']})"
    )
    if INDEX_HTML.exists():
        print(f"Embedded data into {INDEX_HTML}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
