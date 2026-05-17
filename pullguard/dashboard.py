from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pullguard.store import ScoreStore

router = APIRouter()
store = ScoreStore()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    analyses = store.recent_analyses(limit=50)
    rows_html = ""
    for a in analyses:
        slop = a["slop_score"]
        arch = a["arch_score"]
        slop_class = _score_class(slop) if slop is not None else ""
        arch_class = _score_class(arch) if arch is not None else ""
        flagged = (slop is not None and slop < 25) or (arch is not None and arch < 40)
        rows_html += f"""
        <tr>
            <td>{a['repo']}</td>
            <td>#{a['pr_number']}</td>
            <td class="{slop_class}">{slop or '—'}</td>
            <td class="{arch_class}">{arch or '—'}</td>
            <td>{'🚩' if flagged else '✓'}</td>
            <td>{a['analysed_at']}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PullGuard Dashboard</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem; background: #0f172a; color: #e2e8f0; }}
        h1 {{ color: #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }}
        .score-good {{ color: #22c55e; }}
        .score-warn {{ color: #f59e0b; }}
        .score-bad {{ color: #ef4444; }}
        .stats {{ display: flex; gap: 2rem; margin: 1rem 0; }}
        .stat-card {{ background: #1e293b; padding: 1rem; border-radius: 0.5rem; flex: 1; }}
        .stat-card h3 {{ margin: 0; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 2rem; font-weight: bold; color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>PullGuard Dashboard</h1>
    <div class="stats">
        <div class="stat-card">
            <h3>Recent Analyses</h3>
            <div class="value">{len(analyses)}</div>
        </div>
    </div>
    <table>
        <thead>
            <tr>
                <th>Repo</th>
                <th>PR</th>
                <th>Slop</th>
                <th>Arch</th>
                <th>Status</th>
                <th>Time</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</body>
</html>"""


@router.get("/dashboard/health")
async def dashboard_health():
    return {"status": "ok", "analyses_today": len(store.recent_analyses(limit=50)), "uptime_seconds": 0}


def _score_class(score: int | None) -> str:
    if score is None:
        return ""
    if score >= 70:
        return "score-good"
    if score >= 40:
        return "score-warn"
    return "score-bad"
