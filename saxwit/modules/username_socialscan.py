"""Quick username/email availability check module — dependency: socialscan."""

from typing import List, Dict, Any

from socialscan.util import Platforms, sync_execute_queries


def scan_queries(queries: List[str], platforms: List[str] = None) -> List[Dict[str, Any]]:
    """Check the availability of a username or email across several platforms.

    Args:
        queries: list of strings, may mix usernames and/or emails.
        platforms: optional list of platform names (case-insensitive) matching
            the socialscan.util.Platforms enum. None = all supported platforms.

    Returns:
        List of dict {query, platform, available, valid, success, message, link}
    """
    if platforms:
        wanted = {p.strip().upper() for p in platforms}
        selected = [p for p in Platforms if p.name.upper() in wanted]
    else:
        selected = list(Platforms)

    raw_results = sync_execute_queries(queries, platforms=selected)

    output = []
    for r in raw_results:
        output.append(
            {
                "query": r.query,
                "platform": r.platform.name,
                "available": r.available,
                "valid": r.valid,
                "success": r.success,
                "message": r.message,
                "link": r.link,
            }
        )
    return output


def list_platforms() -> List[str]:
    return [p.name for p in Platforms]
