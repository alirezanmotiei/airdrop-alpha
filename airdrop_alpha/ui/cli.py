"""
Rich Interactive Terminal Interface for AirdropAlpha.
Renders financial dashboards, cost-tier badges, and investment memos in terminal.
"""

from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from airdrop_alpha.core.models import AirdropProject, CostTier
from airdrop_alpha.ranking.scorer import filter_projects, sort_projects
from airdrop_alpha.reporting.memo import generate_investment_memo

console = Console(force_terminal=True, legacy_windows=False)


def display_dashboard(
    projects: List[AirdropProject],
    free_only: bool = False,
    sort_by: str = "alpha_score",
    limit: int = 15,
) -> None:
    """
    Renders an institutional terminal dashboard for airdrops.
    """
    # Apply filters and sorting
    filtered = filter_projects(projects, free_only=free_only)
    sorted_projects = sort_projects(filtered, sort_by=sort_by)
    display_list = sorted_projects[:limit]
    
    # 1. Header Banner
    free_count = sum(1 for p in projects if p.cost_tier == CostTier.FREE_TASKS_ONLY)
    avg_wage = (
        sum(p.metrics.hourly_wage_usd for p in projects) / len(projects)
        if projects else 0.0
    )
    top_pick = sorted_projects[0].name if sorted_projects else "None"
    
    stats_text = (
        f"[bold cyan]Total Airdrops Tracked:[/bold cyan] {len(projects)}  |  "
        f"[bold green]100% Free (Zero Capital):[/bold green] {free_count}  |  "
        f"[bold yellow]Avg Hourly Return:[/bold yellow] ${avg_wage:.2f}/hr  |  "
        f"[bold magenta]Top Alpha Pick:[/bold magenta] {top_pick}"
    )
    
    filter_label = "[bold green]100% FREE ONLY (ZERO CAPITAL)[/bold green]" if free_only else "[bold blue]ALL TIERS[/bold blue]"
    console.print(Panel(
        f"[bold white]🚀 AIRDROP-ALPHA: INSTITUTIONAL QUANTITATIVE SCOUT[/bold white]\n"
        f"{stats_text}\n"
        f"Active Filter: {filter_label} | Sorted By: [bold cyan]{sort_by.upper()}[/bold cyan]",
        border_style="cyan",
    ))
    
    # 2. Main Table
    table = Table(
        title=f"Top {len(display_list)} Airdrop Opportunities",
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    
    table.add_column("#", justify="center", width=3)
    table.add_column("Project", style="bold white", width=18)
    table.add_column("Category", style="cyan", width=12)
    table.add_column("Cost Profile", justify="center", width=22)
    table.add_column("Safety", justify="center", width=8)
    table.add_column("Exp. Reward", justify="right", width=12)
    table.add_column("$/Hour (Ω)", justify="right", style="bold green", width=12)
    table.add_column("Hours / $10 (H10)", justify="right", style="bold yellow", width=16)
    table.add_column("Alpha Score", justify="center", style="bold cyan", width=12)

    for idx, p in enumerate(display_list, 1):
        m = p.metrics
        r = p.risk
        
        # Cost Profile Badge
        if p.cost_tier == CostTier.FREE_TASKS_ONLY:
            cost_str = "[bold green]FREE (Task Only)[/bold green]"
        elif p.cost_tier == CostTier.GAS_ONLY:
            cost_str = "[yellow]Gas Only (<$5)[/yellow]"
        else:
            cost_str = "[red]Capital Req.[/red]"
            
        # Safety Color
        if r.safety_score >= 70:
            safety_str = f"[bold green]{r.safety_score:.0f}[/bold green]"
        elif r.safety_score >= 45:
            safety_str = f"[yellow]{r.safety_score:.0f}[/yellow]"
        else:
            safety_str = f"[bold red]{r.safety_score:.0f}[/bold red]"
            
        table.add_row(
            str(idx),
            p.name[:17],
            p.category[:11],
            cost_str,
            safety_str,
            f"${m.expected_reward_usd:,.0f}",
            f"${m.hourly_wage_usd:,.2f}/h",
            f"{m.hours_per_10usd:.2f} hrs",
            f"{m.alpha_score:.1f}",
        )

    console.print(table)
    console.print(
        "[dim]Tips: Run with '--memo <ProjectName>' to view full 1-page investment memo, "
        "or '--free-only' to isolate 100% zero-capital tasks.[/dim]\n"
    )


def display_memo_cli(projects: List[AirdropProject], project_name_or_slug: str) -> None:
    """
    Displays the 1-Page Investment Memo for a matching project in terminal.
    """
    target = None
    query = project_name_or_slug.lower()
    for p in projects:
        if query in p.name.lower() or query in p.slug.lower():
            target = p
            break
            
    if not target:
        console.print(f"[bold red]Error:[/bold red] Project matching '{project_name_or_slug}' not found.")
        return
        
    memo_md = generate_investment_memo(target)
    console.print(Markdown(memo_md))
