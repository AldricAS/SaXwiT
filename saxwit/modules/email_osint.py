"""Email OSINT module — dependency: holehe."""

from typing import List, Dict, Any

import httpx
import trio

from holehe.core import import_submodules, get_functions


def _load_websites():
    modules = import_submodules("holehe.modules")
    return get_functions(modules)


async def _safe_call(site_func, email, client, out):
    name = getattr(site_func, "__name__", "unknown")
    try:
        await site_func(email, client, out)
    except Exception:
        out.append({"name": name, "domain": name, "rateLimit": True,
                     "exists": False, "emailrecovery": None,
                     "phoneNumber": None, "others": None})


async def _run_check(email, websites):
    out = []
    async with httpx.AsyncClient(timeout=15) as client:
        async with trio.open_nursery() as nursery:
            for site_func in websites:
                nursery.start_soon(_safe_call, site_func, email, client, out)
    return out


def check_email(email):
    websites = _load_websites()
    results = trio.run(_run_check, email, websites)
    results.sort(key=lambda r: r.get("domain", r.get("name", "")))
    return results


def summarize(results):
    used = sum(1 for r in results if r.get("exists") is True)
    not_used = sum(1 for r in results if r.get("exists") is False and not r.get("rateLimit"))
    rate_limited = sum(1 for r in results if r.get("rateLimit"))
    return {"total": len(results), "used": used, "not_used": not_used, "rate_limited": rate_limited}
