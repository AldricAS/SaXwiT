"""Username OSINT module across hundreds of sites — dependency: maigret."""

import asyncio
import logging
import os
from typing import List, Dict, Any

from maigret.checking import maigret as maigret_search
from maigret.sites import MaigretDatabase

logging.getLogger("maigret").setLevel(logging.CRITICAL)

_DB_PATH = os.path.join(os.path.dirname(__import__("maigret").__file__), "resources", "data.json")


def _load_database() -> MaigretDatabase:
    return MaigretDatabase().load_from_path(_DB_PATH)


def search_username(
    username: str,
    top_sites: int = 500,
    timeout: int = 10,
    max_connections: int = 50,
) -> List[Dict[str, Any]]:
    """Search for a username across many sites using the maigret database.

    Args:
        username: the username to search for.
        top_sites: limit to the most popular sites for speed.
        timeout: per-request timeout in seconds.
        max_connections: maximum number of parallel connections.

    Returns:
        List of dict {site, url, status, tags}
    """
    db = _load_database()
    site_dict = db.ranked_sites_dict(top=top_sites)

    logger = logging.getLogger("maigret_run")
    logger.setLevel(logging.CRITICAL)

    search_results = asyncio.run(
        maigret_search(
            username=username,
            site_dict=site_dict,
            logger=logger,
            timeout=timeout,
            max_connections=max_connections,
            no_progressbar=True,
        )
    )

    found = []
    for site_name, site_result in search_results.items():
        check_result = site_result.get("status")
        status_enum = getattr(check_result, "status", None)
        status_str = status_enum.name if status_enum is not None else "UNKNOWN"
        if status_str == "CLAIMED":
            site_obj = site_dict.get(site_name)
            found.append(
                {
                    "site": site_name,
                    "url": site_result.get("url_user")
                    or getattr(check_result, "site_url_user", None),
                    "status": status_str,
                    "tags": list(getattr(site_obj, "tags", []) or []),
                }
            )
    found.sort(key=lambda r: r["site"].lower())
    return found
