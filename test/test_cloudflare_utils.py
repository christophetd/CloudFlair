import unittest
import cloudflare_utils

class TestCloudFlareUtils(unittest.TestCase):
    def test_uses_cloudflare(self):
        self.assertTrue(cloudflare_utils.uses_cloudflare('myvulnerable.site'))
        
    def test_does_not_use_cloudflare(self):
        self.assertFalse(cloudflare_utils.uses_cloudflare('google.com'))
