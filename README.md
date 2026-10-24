# Email Security Link Decoder

A small, offline Python CLI for expanding common email security URL wrappers during security triage. It prints the recovered destination without opening the link or making network requests.

> Decoding is not a safety verdict. Treat recovered destinations as untrusted and inspect them in an appropriate isolated workflow.

## Supported wrappers

- Microsoft Safe Links
- Proofpoint URL Defense v1, v2, and v3
- Barracuda LinkProtect
- Nested combinations of supported wrappers (up to eight layers)

Mimecast short-link destinations are held server-side and cannot be recovered by this offline script. Cisco Secure Email links are not implemented here.

## Requirements

Python 3.8+; standard library only. No packages or network access are required.

## Usage

Save one URL per line in `links.txt`, then run:

```sh
python3 decode_wrapped.py links.txt
```

Example output:

```text
Safe Links > Proofpoint | https://example.com/login
not wrapped | (destination not recoverable here)
```

The tool only parses the input text. It never fetches, resolves, or opens decoded URLs.

## Synthetic examples

Use reserved `example.com` URLs only; these are examples, not live destinations.

```text
https://nam10.safelinks.protection.outlook.com/?url=https%3A%2F%2Fexample.com%2Flogin&data=05&sdata=abc&reserved=0
https://urldefense.proofpoint.com/v1/url?u=https%3A%2F%2Fexample.com%2Flogin&k=abc
https://urldefense.proofpoint.com/v2/url?u=https-3A__example.com_login&d=DwICAg&c=abc
https://urldefense.proofpoint.com/v3/__https://example.com/path__;!
https://linkprotect.cudasvc.com/url?a=https%3A%2F%2Fexample.com%2Flogin&c=E,1,token
https://protect-us.mimecast.com/s/AbCdEf?domain=login.example.com
```

## Tests

Run the synthetic unit tests with:

```sh
python3 -m unittest discover -s tests -v
```

The tests use only synthetic URLs and do not make network requests.

## Related resources

- [The Hacker Room URL Decoder tool](https://thehackerroom.com/tools/url-decoder/)
- [Article: How to Decode Safe Links, Proofpoint, Mimecast and Barracuda URLs](https://thehackerroom.com/blog/how-to-decode-email-security-links/)

This repository accompanies the article’s command-line example. The web tool and this CLI may support different providers.
