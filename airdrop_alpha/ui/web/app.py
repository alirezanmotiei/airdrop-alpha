"""
FastAPI Web Dashboard Server for AirdropAlpha.
Provides interactive REST APIs and serves modern Glassmorphism frontend.
"""

from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from airdrop_alpha.collectors.aggregator import AirdropAggregator
from airdrop_alpha.ranking.scorer import filter_projects, sort_projects
from airdrop_alpha.reporting.memo import generate_investment_memo
from airdrop_alpha.core.models import CostTier

WEB_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="AirdropAlpha",
    description="Institutional-Grade Quantitative Airdrop Scouting & Valuation Engine",
    version="0.1.0",
)

jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
aggregator = AirdropAggregator()

# In-memory cached dataset
_cached_projects = []


def get_dataset(refresh: bool = False):
    global _cached_projects
    if not _cached_projects or refresh:
        _cached_projects = aggregator.run_pipeline(use_cache=not refresh)
    return _cached_projects


@app.get("/", response_class=HTMLResponse)
async def dashboard_page():
    """Renders the main Glassmorphism Web Dashboard."""
    projects = get_dataset()
    free_count = sum(1 for p in projects if p.cost_tier == CostTier.FREE_TASKS_ONLY)
    avg_wage = (
        sum(p.metrics.hourly_wage_usd for p in projects) / len(projects)
        if projects else 0.0
    )
    max_wage = max((p.metrics.hourly_wage_usd for p in projects), default=0.0)
    avg_safety = (
        sum(p.risk.safety_score for p in projects) / len(projects)
        if projects else 0.0
    )
    
    template = jinja_env.get_template("index.html")
    return template.render(
        total_projects=len(projects),
        free_count=free_count,
        avg_wage=round(avg_wage, 2),
        max_wage=round(max_wage, 2),
        avg_safety=round(avg_safety, 1),
    )


@app.get("/api/airdrops")
async def get_airdrops_api(
    free_only: bool = False,
    min_safety: float = 0.0,
    category: Optional[str] = None,
    chain: Optional[str] = None,
    sort_by: str = "alpha_score",
    search: Optional[str] = None,
    limit: int = 50,
):
    """Returns filtered and sorted airdrops as JSON."""
    projects = get_dataset()
    
    # 1. Text Search Filter
    if search:
        q = search.lower()
        projects = [
            p for p in projects
            if q in p.name.lower() or q in p.category.lower() or any(q in c.lower() for c in p.chains)
        ]
        
    # 2. Structured Filters
    filtered = filter_projects(
        projects,
        free_only=free_only,
        min_safety_score=min_safety,
        category=category,
        chain=chain,
    )
    
    # 3. Sort
    sorted_items = sort_projects(filtered, sort_by=sort_by)
    results = [p.model_dump() for p in sorted_items[:limit]]
    return {"count": len(results), "data": results}


@app.get("/api/memo/{slug}")
async def get_memo_api(slug: str):
    """Returns 1-Page Investment Memo in Markdown for specified project."""
    projects = get_dataset()
    target = next((p for p in projects if p.slug == slug or p.id == slug), None)
    if not target:
        raise HTTPException(status_code=404, detail="Project not found")
        
    memo_md = generate_investment_memo(target)
    return {
        "slug": target.slug,
        "name": target.name,
        "memo_markdown": memo_md,
    }


@app.get("/api/refresh")
async def refresh_dataset():
    """Forces a live pipeline refresh ignoring cache."""
    projects = get_dataset(refresh=True)
    return {"status": "ok", "refreshed_count": len(projects)}
