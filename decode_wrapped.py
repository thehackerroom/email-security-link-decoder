#!/usr/bin/env python3
"""Decode Safe Links, Proofpoint (v1/v2/v3), Barracuda and nested links locally.

Usage: python3 decode_wrapped.py links.txt      (one link per line)
Nothing is fetched or opened. Mimecast short tokens cannot be decoded offline.
"""
import base64
import html
import re
import sys
from urllib.parse import parse_qs, unquote, urlparse

B64CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
V3_RUN = {c: i + 2 for i, c in enumerate(B64CHARS)}  # **A = 2 characters, **B = 3, ...

def pct(value):
    for _ in range(3):  # links are sometimes encoded more than once
        nxt = unquote(value)
        if nxt == value:
            break
        value = nxt
    return value

def b64url(value):
    value += "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value).decode("utf-8", "replace")

def as_url(value):
    for candidate in (pct(value), value):
        if re.match(r"https?://", candidate, re.I):
            return candidate
    try:
        decoded = b64url(value)
    except Exception:
        return None
    return decoded if re.match(r"https?://", decoded, re.I) else None

def proofpoint(link):
    ver = re.search(r"/(v[123])/", link, re.I)
    ver = ver.group(1).lower() if ver else ""
    if ver == "v1":
        m = re.search(r"[?&]u=(.+?)&k=", link, re.I)
        return html.unescape(pct(m.group(1))) if m else None
    if ver == "v2":
        m = re.search(r"[?&]u=(.+?)&[dc]=", link, re.I)
        return html.unescape(pct(m.group(1).replace("-", "%").replace("_", "/"))) if m else None
    if ver == "v3":
        m = re.search(r"v3/__(.+?)__;([^!]*)!", link, re.I)
        if not m:
            return None
        url = m.group(1)
        fix = re.match(r"([a-z0-9+.-]+:/)([^/].+)", url, re.I)
        if fix:
            url = fix.group(1) + "/" + fix.group(2)
        url = pct(url)
        if not m.group(2):
            return url
        repl, pos, out, last = b64url(m.group(2)), 0, "", 0
        for t in re.finditer(r"\*(?:\*.)?", url):
            out += url[last:t.start()]
            if t.group() == "*":
                out += repl[pos:pos + 1]
                pos += 1
            else:
                n = V3_RUN[t.group()[2]]
                out += repl[pos:pos + n]
                pos += n
            last = t.end()
        return out + url[last:]
    return None

def unwrap_once(link):
    u = urlparse(link)
    host = (u.hostname or "").lower()
    q = parse_qs(u.query)
    if host.endswith("safelinks.protection.outlook.com"):
        return "Safe Links", pct(q["url"][0]) if "url" in q else None
    if re.fullmatch(r"urldefense(\.proofpoint)?\.(com|us)", host):
        return "Proofpoint", proofpoint(link)
    if host.endswith("cudasvc.com") and ("linkprotect" in host or u.path.startswith("/url")):
        for key in ("a", "u"):
            if key in q:
                return "Barracuda", as_url(q[key][0])
        return "Barracuda", None
    if host.endswith("mimecastprotect.com") or (host.endswith("mimecast.com") and (host.startswith("protect-") or u.path.startswith("/s/"))):
        return "Mimecast", None  # the destination lives on Mimecast's servers
    return None, None

def decode(link):
    link = html.unescape(link.strip()).strip("<>")
    layers = []
    for _ in range(8):
        vendor, inner = unwrap_once(link)
        if vendor is None:
            break
        layers.append(vendor)
        if not inner or inner == link:
            return layers, None
        link = inner
    return layers, (link if layers else None)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: decode_wrapped.py FILE")
    with open(sys.argv[1], encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                layers, dest = decode(line)
                print(" > ".join(layers) or "not wrapped", "|", dest or "(destination not recoverable here)")
