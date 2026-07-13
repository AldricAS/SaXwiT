"""SaXwiT — main CLI.

Wires up the OSINT modules (phonenumbers, holehe, maigret,
socialscan, ignorant) into a single clean command-line interface,
powered by rich for the display.
"""

import argparse
import sys
import time
import traceback

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import box

from saxwit.banner import console, render_banner, section
from saxwit.modules.phone_intel import analyze_phone
from saxwit.modules.email_osint import check_email, summarize as summarize_email
from saxwit.modules.phone_osint import check_phone
from saxwit.modules.username_maigret import search_username
from saxwit.modules.username_socialscan import scan_queries


# --------------------------------------------------------------------------- #
# Display helpers
# --------------------------------------------------------------------------- #

def _timed(label: str, func, *args, **kwargs):
    with console.status(f"[accent]{label}...[/accent]", spinner="dots12"):
        start = time.time()
        try:
            result = func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            console.print(f"[bad]Failed:[/bad] {exc}")
            console.print(f"[dim]{traceback.format_exc(limit=1)}[/dim]")
            return None
        elapsed = time.time() - start
    console.print(f"[dim]Done in {elapsed:.2f}s[/dim]")
    return result


# --------------------------------------------------------------------------- #
# 1) Phone intel — phonenumbers
# --------------------------------------------------------------------------- #

def run_phone_intel(number: str, region: str = "US") -> None:
    section("📞 Phone Number Intelligence", "dependency: phonenumbers")
    info = analyze_phone(number, default_region=region)

    if info.error:
        console.print(f"[bad]Could not parse number:[/bad] {info.error}")
        return

    table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 1))
    table.add_column("Field", style="accent", no_wrap=True)
    table.add_column("Value", style="white")

    valid_style = "ok" if info.valid else "bad"
    table.add_row("Valid?", f"[{valid_style}]{info.valid}[/{valid_style}]")
    table.add_row("Possible?", str(info.possible))
    table.add_row("E.164", info.e164 or "-")
    table.add_row("International", info.international or "-")
    table.add_row("National", info.national or "-")
    table.add_row("Country code", f"+{info.country_code}" if info.country_code else "-")
    table.add_row("Region", info.region_code or "-")
    table.add_row("Estimated location", info.location or "-")
    table.add_row("Carrier", info.carrier_name or "-")
    table.add_row("Line type", info.line_type or "-")
    table.add_row("Timezone(s)", ", ".join(info.timezones) if info.timezones else "-")

    console.print(Panel(table, title=f"[title]{number}[/title]", border_style="brand"))


# --------------------------------------------------------------------------- #
# 2) Email OSINT — holehe
# --------------------------------------------------------------------------- #

def run_email_osint(email: str) -> None:
    section("📧 Email OSINT", "dependency: holehe — checks an email across many platforms")
    results = _timed(f"Scanning {email} across hundreds of platforms", check_email, email)
    if results is None:
        return

    used = [r for r in results if r.get("exists") is True]
    stats = summarize_email(results)

    table = Table(box=box.SIMPLE_HEAVY, title="Platforms that recognize this email")
    table.add_column("Platform", style="accent")
    table.add_column("Extra info", style="white")

    if used:
        for r in used:
            extra_bits = []
            if r.get("emailrecovery"):
                extra_bits.append(f"recovery: {r['emailrecovery']}")
            if r.get("phoneNumber"):
                extra_bits.append(f"phone: {r['phoneNumber']}")
            others = r.get("others") or {}
            if "FullName" in others:
                extra_bits.append(f"name: {others['FullName']}")
            table.add_row(r.get("domain", r.get("name", "?")), " | ".join(extra_bits) or "-")
        console.print(table)
    else:
        console.print("[warn]No trace found on any platform.[/warn]")

    console.print(
        f"\n[ok]{stats['used']} used[/ok] · "
        f"[dim]{stats['not_used']} not used[/dim] · "
        f"[warn]{stats['rate_limited']} rate-limited[/warn] · "
        f"total checked: {stats['total']}"
    )


# --------------------------------------------------------------------------- #
# 3) Phone account OSINT — ignorant
# --------------------------------------------------------------------------- #

def run_phone_osint(country_code: str, national_number: str) -> None:
    section("📱 Phone Account OSINT", "dependency: ignorant — checks accounts registered with a phone number")
    results = _timed(
        f"Scanning {country_code}{national_number}",
        check_phone,
        national_number,
        country_code,
    )
    if results is None:
        return

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Service", style="accent")
    table.add_column("Status", style="white")

    for r in results:
        if r.get("rateLimit"):
            status = "[warn]rate limited[/warn]"
        elif r.get("exists"):
            status = "[ok]registered[/ok]"
        else:
            status = "[dim]not registered[/dim]"
        table.add_row(r.get("name", "?"), status)

    console.print(table)


# --------------------------------------------------------------------------- #
# 4) Username OSINT — maigret
# --------------------------------------------------------------------------- #

def run_username_maigret(username: str, top_sites: int, timeout: int) -> None:
    section("🕵️ Username OSINT", "dependency: maigret — checks a username across many sites")
    results = _timed(
        f"Searching for username '{username}' (top {top_sites} sites)",
        search_username,
        username,
        top_sites,
        timeout,
    )
    if results is None:
        return

    if not results:
        console.print("[warn]No matching accounts found.[/warn]")
        return

    table = Table(box=box.SIMPLE_HEAVY, title=f"Accounts found for '{username}'")
    table.add_column("Site", style="accent")
    table.add_column("URL", style="info")
    table.add_column("Tags", style="dim")

    for r in results:
        table.add_row(r["site"], r["url"] or "-", ", ".join(r["tags"]) or "-")

    console.print(table)
    console.print(f"\n[ok]{len(results)} account(s) found[/ok]")


# --------------------------------------------------------------------------- #
# 5) Username/email availability — socialscan
# --------------------------------------------------------------------------- #

def run_socialscan(queries_raw: str) -> None:
    section("🔍 Quick Availability Scan", "dependency: socialscan — quick username/email availability check")
    queries = [q.strip() for q in queries_raw.split(",") if q.strip()]
    if not queries:
        console.print("[bad]No valid query provided.[/bad]")
        return

    results = _timed(f"Checking {', '.join(queries)}", scan_queries, queries)
    if results is None:
        return

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Query", style="accent")
    table.add_column("Platform", style="white")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    for r in results:
        if not r["success"]:
            status = "[warn]error[/warn]"
        elif r["available"]:
            status = "[ok]available[/ok]"
        elif r["valid"]:
            status = "[bad]taken[/bad]"
        else:
            status = "[dim]invalid[/dim]"
        table.add_row(r["query"], r["platform"], status, r["message"] or "-")

    console.print(table)


# --------------------------------------------------------------------------- #
# Interactive menu
# --------------------------------------------------------------------------- #

MENU_OPTIONS = {
    "1": "Phone Number Intelligence (phonenumbers)",
    "2": "Email OSINT (holehe)",
    "3": "Phone Account OSINT (ignorant)",
    "4": "Username OSINT (maigret)",
    "5": "Quick Availability Scan (socialscan)",
    "0": "Exit",
}


def show_menu() -> None:
    table = Table(box=box.ROUNDED, show_header=False, border_style="brand")
    table.add_column("No", style="accent", width=4, justify="center")
    table.add_column("Module", style="white")
    for key, label in MENU_OPTIONS.items():
        table.add_row(key, label)
    console.print(table)


def interactive_loop() -> None:
    render_banner()
    while True:
        show_menu()
        choice = Prompt.ask("[brand]Choose a module[/brand]", choices=list(MENU_OPTIONS), default="0")

        if choice == "0":
            console.print("[accent]See you next time! 👋[/accent]")
            break
        elif choice == "1":
            number = Prompt.ask("Phone number (e.g. +14155552671)")
            region = Prompt.ask("Default region if no country code is given", default="US")
            run_phone_intel(number, region)
        elif choice == "2":
            email = Prompt.ask("Target email address")
            run_email_osint(email)
        elif choice == "3":
            cc = Prompt.ask("Country code (e.g. +1)")
            num = Prompt.ask("National number without country code (e.g. 4155552671)")
            run_phone_osint(cc, num)
        elif choice == "4":
            username = Prompt.ask("Target username")
            top = IntPrompt.ask("Number of top sites to check", default=500)
            timeout = IntPrompt.ask("Timeout per request (seconds)", default=10)
            run_username_maigret(username, top, timeout)
        elif choice == "5":
            queries = Prompt.ask("Username/email (comma-separated for multiple queries)")
            run_socialscan(queries)

        console.print()
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="", show_default=False)
        console.clear()
        render_banner()


# --------------------------------------------------------------------------- #
# Argparse (non-interactive / scripting mode)
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="saxwit",
        description="SaXwiT — OSINT CLI toolkit (phonenumbers, holehe, maigret, socialscan, ignorant)",
    )
    sub = parser.add_subparsers(dest="command")

    p_phone = sub.add_parser("phone", help="Analyze a phone number (phonenumbers)")
    p_phone.add_argument("number", help="Phone number, e.g. +14155552671")
    p_phone.add_argument("--region", default="US", help="Default region (ISO-2), default: US")

    p_email = sub.add_parser("email", help="Check an email's footprint across many platforms (holehe)")
    p_email.add_argument("email", help="Target email address")

    p_phoneacc = sub.add_parser("phoneacc", help="Check accounts registered via a phone number (ignorant)")
    p_phoneacc.add_argument("country_code", help="Country code, e.g. +1")
    p_phoneacc.add_argument("national_number", help="National number without country code")

    p_user = sub.add_parser("username", help="Check a username across many sites (maigret)")
    p_user.add_argument("username", help="Target username")
    p_user.add_argument("--top", type=int, default=500, help="Number of top sites to check, default 500")
    p_user.add_argument("--timeout", type=int, default=10, help="Timeout per request (seconds)")

    p_scan = sub.add_parser("scan", help="Quick username/email availability check (socialscan)")
    p_scan.add_argument("queries", help="One or more queries, comma-separated")

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        try:
            interactive_loop()
        except KeyboardInterrupt:
            console.print("\n[accent]Cancelled. See you next time! 👋[/accent]")
        return

    render_banner()

    if args.command == "phone":
        run_phone_intel(args.number, args.region)
    elif args.command == "email":
        run_email_osint(args.email)
    elif args.command == "phoneacc":
        run_phone_osint(args.country_code, args.national_number)
    elif args.command == "username":
        run_username_maigret(args.username, args.top, args.timeout)
    elif args.command == "scan":
        run_socialscan(args.queries)


if __name__ == "__main__":
    sys.exit(main())
