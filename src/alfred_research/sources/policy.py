"""Bounded offline parsing and pure future-network validation. No networking."""
from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlsplit, urljoin
import time

from ..contracts import require


class ExtractionLimit(ValueError):
    pass


@dataclass(frozen=True)
class ProcessingLimits:
    input_bytes: int = 1_000_000
    files: int = 128
    characters: int = 64_000
    segments: int = 128
    work_units: int = 100_000
    milliseconds: int = 2000

    def __post_init__(self):
        ceilings = (1_000_000, 256, 128_000, 256, 1_000_000, 10_000)
        for (name, value), ceiling in zip(vars(self).items(), ceilings):
            require(type(value) is int and 0 < value <= ceiling, 'invalid processing limit: ' + name)


class Meter:
    def __init__(self, limits, clock=time.monotonic):
        self.limits = limits
        self.clock = clock
        self.started = clock()
        self.work = 0
        self.characters = 0
        self.segments = 0

    def check(self, units=1):
        exceeded = units > self.limits.work_units - self.work
        self.work = min(self.limits.work_units, self.work + units)
        if exceeded or (self.clock() - self.started) * 1000 > self.limits.milliseconds:
            raise ExtractionLimit('processing time/work budget exhausted')


@dataclass(frozen=True)
class FutureNetworkPolicy:
    """Planning primitive only. Never resolves DNS, opens sockets or follows URLs.

    Future transport must pin/revalidate every resolved address at connection,
    validate each redirect, forbid proxy bypass, and enforce timeout/body limits.
    """
    max_redirects: int = 3

    def __post_init__(self):
        require(type(self.max_redirects) is int and 0 <= self.max_redirects <= 5, 'bounded redirect limit required')

    def validate(self, url, resolved_addresses):
        require(type(url) is str and len(url) <= 2048, 'bounded URL required')
        parsed = urlsplit(url)
        require(parsed.scheme == 'https' and bool(parsed.hostname) and parsed.username is None and
                parsed.password is None and parsed.port in (None, 443) and
                not any(ord(c) <= 32 for c in url), 'unsafe URL')
        host = parsed.hostname.lower().rstrip('.')
        require(host != 'localhost' and not host.endswith(('.localhost', '.local', '.internal')),
                'private hostname')
        require(type(resolved_addresses) is tuple and bool(resolved_addresses), 'resolved IPs required')
        candidates = list(resolved_addresses)
        try:
            candidates.append(str(ip_address(host)))
        except ValueError:
            pass
        for address in candidates:
            ip = ip_address(address)
            require(ip.is_global and not ip.is_multicast and not ip.is_unspecified and
                    not (getattr(ip, 'ipv4_mapped', None) and not ip.ipv4_mapped.is_global),
                    'nonpublic destination forbidden')
        return url

    def redirect(self, current, location, addresses, hops):
        require(type(hops) is int and 0 <= hops < self.max_redirects, 'redirect limit')
        return self.validate(urljoin(current, location), addresses)
