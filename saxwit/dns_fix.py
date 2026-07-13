"""Workaround for aiohttp's async DNS resolver failing on Termux/Android.

socialscan and maigret both use aiohttp under the hood. When the optional
`aiodns` package is installed, aiohttp defaults to a c-ares based resolver
that reads /etc/resolv.conf directly. On Termux (and some other Android
setups) that file is often missing or not populated correctly even though
the device's actual network/DNS works fine — which produces errors like:

    ClientConnectorDNSError - Cannot connect to host ... ssl:default
    [Could not contact DNS servers]

Forcing aiohttp to use its built-in ThreadedResolver instead sidesteps the
problem entirely, since that resolver just calls socket.getaddrinfo(),
the same mechanism the OS/Android itself uses to resolve names. This is
safe on Linux/Windows too — it's simply a touch less "async-pure" than the
c-ares resolver, with no real downside for a CLI tool like this.

Import this module once, before running any aiohttp-based check.
"""

import aiohttp.connector
import aiohttp.resolver

# aiohttp.connector does `from .resolver import DefaultResolver` at import
# time, which copies the name into connector's own namespace. Patching only
# aiohttp.resolver.DefaultResolver is therefore not enough — the connector
# already holds its own reference to the old (c-ares based) class. Both
# names must be overwritten for TCPConnector to actually pick up the fix.
aiohttp.resolver.DefaultResolver = aiohttp.resolver.ThreadedResolver
aiohttp.connector.DefaultResolver = aiohttp.resolver.ThreadedResolver
