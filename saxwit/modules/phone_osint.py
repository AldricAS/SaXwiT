"""Phone-based account OSINT module — dependency: ignorant."""

from typing import List, Dict, Any

import httpx
import trio

from ignorant.core import import_submodules, get_functions


def _load_websites():
    modules = import_submodules("ignorant.modules")
    return get_functions(modules)


async def _safe_call(site_func, phone, country_code, client, out):
    name = getattr(site_func, "__name__", "unknown")
    try:
        await site_func(phone, country_code, client, out)
    except Exception:
        out.append({"name": name, "rateLimit": True, "exists": False})


async def _run_check(phone, country_code, websites):
    out = []
    async with httpx.AsyncClient(timeout=15) as client:
        async with trio.open_nursery() as nursery:
            for site_func in websites:
                nursery.start_soon(_safe_call, site_func, phone, country_code, client, out)
    return out


def check_phone(phone_national, country_code):
    websites = _load_websites()
    results = trio.run(_run_check, phone_national, country_code, websites)
    results.sort(key=lambda r: r.get("name", ""))
    return results
