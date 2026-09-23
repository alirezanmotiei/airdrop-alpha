"""
Unified Main Entrypoint for AirdropAlpha.
Supports interactive CLI, Modern Web Dashboard, and Data Export.
"""

import sys
import os
import argparse
import uvicorn

# Ensure UTF-8 output on Windows consoles to support emojis and symbols
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from airdrop_alpha.core.config import settings
from airdrop_alpha.collectors.aggregator import AirdropAggregator
from airdrop_alpha.ui.cli import display_dashboard, display_memo_cli


def setup_proxy(proxy_arg: str = None):
    """Sets HTTP/HTTPS/ALL proxy if supplied via CLI."""
    if proxy_arg:
        os.environ["HTTP_PROXY"] = proxy_arg
        os.environ["HTTPS_PROXY"] = proxy_arg
        os.environ["ALL_PROXY"] = proxy_arg
        settings.http_proxy = proxy_arg
        settings.https_proxy = proxy_arg
        settings.all_proxy = proxy_arg


def main():
    parser = argparse.ArgumentParser(
        prog="airdrop-alpha",
        description="🚀 Institutional Quantitative Airdrop Scouting & Valuation Engine",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run interactive terminal dashboard")
    cli_parser.add_argument("--free-only", action="store_true", help="Filter 100% Free / Zero-Capital airdrops only")
    cli_parser.add_argument("--sort", default="alpha_score", choices=["alpha_score", "hourly_wage", "hours_per_10usd", "safety_score", "expected_reward", "implied_fdv"], help="Sort metric")
    cli_parser.add_argument("--limit", type=int, default=15, help="Number of records to display")
    cli_parser.add_argument("--memo", type=str, default=None, help="Display 1-Page Investment Memo for specific project")
    cli_parser.add_argument("--proxy", type=str, default=None, help="Proxy URL (e.g. socks5://127.0.0.1:10808 or http://127.0.0.1:7890)")
    cli_parser.add_argument("--refresh", action="store_true", help="Bypass local cache and fetch fresh live data")

    # Web Dashboard command
    web_parser = subparsers.add_parser("web", help="Launch Modern Glassmorphism Web Dashboard")
    web_parser.add_argument("--host", default="127.0.0.1", help="Host interface")
    web_parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    web_parser.add_argument("--proxy", type=str, default=None, help="Proxy URL")

    # Memo command shortcut
    memo_parser = subparsers.add_parser("memo", help="Quickly view 1-Page Investment Memo")
    memo_parser.add_argument("project", type=str, help="Project name or slug")
    memo_parser.add_argument("--proxy", type=str, default=None, help="Proxy URL")

    args = parser.parse_args()

    # Default to CLI dashboard if no command given
    if not args.command:
        args.command = "cli"
        args.free_only = False
        args.sort = "alpha_score"
        args.limit = 15
        args.memo = None
        args.proxy = None
        args.refresh = False

    setup_proxy(getattr(args, "proxy", None))

    if args.command == "cli":
        aggregator = AirdropAggregator()
        projects = aggregator.run_pipeline(use_cache=not getattr(args, "refresh", False))
        
        if args.memo:
            display_memo_cli(projects, args.memo)
        else:
            display_dashboard(
                projects=projects,
                free_only=args.free_only,
                sort_by=args.sort,
                limit=args.limit,
            )
            
    elif args.command == "memo":
        aggregator = AirdropAggregator()
        projects = aggregator.run_pipeline(use_cache=True)
        display_memo_cli(projects, args.project)

    elif args.command == "web":
        print(f"\n🚀 Launching AirdropAlpha Dashboard at http://{args.host}:{args.port}")
        uvicorn.run("airdrop_alpha.ui.web.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
