import base64
import unittest
from urllib.parse import quote

from decode_wrapped import decode

DESTINATION = "https://example.com/login"


class DecodeWrappedTests(unittest.TestCase):
    def test_safe_links(self):
        link = (
            "https://nam10.safelinks.protection.outlook.com/?url="
            "https%3A%2F%2Fexample.com%2Flogin&data=05"
        )
        self.assertEqual(decode(link), (["Safe Links"], DESTINATION))

    def test_proofpoint_v1(self):
        link = (
            "https://urldefense.proofpoint.com/v1/url?u="
            "https%3A%2F%2Fexample.com%2Flogin&k=sample"
        )
        self.assertEqual(decode(link), (["Proofpoint"], DESTINATION))

    def test_proofpoint_v2(self):
        link = (
            "https://urldefense.proofpoint.com/v2/url?u="
            "https-3A__example.com_login&d=sample"
        )
        self.assertEqual(decode(link), (["Proofpoint"], DESTINATION))

    def test_proofpoint_v3_plain_destination(self):
        link = "https://urldefense.proofpoint.com/v3/__https://example.com/login__;!"
        self.assertEqual(decode(link), (["Proofpoint"], DESTINATION))

    def test_proofpoint_v3_restores_marked_character(self):
        link = "https://urldefense.proofpoint.com/v3/__https://example.com/a*__;YQ!"
        self.assertEqual(decode(link), (["Proofpoint"], "https://example.com/aa"))

    def test_barracuda_percent_encoded_destination(self):
        link = (
            "https://linkprotect.cudasvc.com/url?a="
            "https%3A%2F%2Fexample.com%2Flogin&c=sample"
        )
        self.assertEqual(decode(link), (["Barracuda"], DESTINATION))

    def test_barracuda_base64_destination(self):
        encoded = base64.urlsafe_b64encode(DESTINATION.encode()).decode().rstrip("=")
        link = f"https://linkprotect.cudasvc.com/url?a={encoded}&c=sample"
        self.assertEqual(decode(link), (["Barracuda"], DESTINATION))

    def test_nested_safe_links_over_proofpoint(self):
        inner = (
            "https://urldefense.proofpoint.com/v2/url?u="
            "https-3A__example.com_login&d=sample"
        )
        link = (
            "https://nam10.safelinks.protection.outlook.com/?url="
            + quote(inner, safe="")
        )
        self.assertEqual(
            decode(link), (["Safe Links", "Proofpoint"], DESTINATION)
        )

    def test_mimecast_short_link_has_no_offline_destination(self):
        link = "https://protect-us.mimecast.com/s/AbCdEf?domain=example.com"
        self.assertEqual(decode(link), (["Mimecast"], None))

    def test_plain_url_is_not_changed(self):
        self.assertEqual(decode(DESTINATION), ([], None))


if __name__ == "__main__":
    unittest.main()
