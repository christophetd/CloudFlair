import unittest
import cloudflair
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_id = os.environ['CENSYS_API_ID']
api_secret = os.environ['CENSYS_API_SECRET']

if None in [ api_id, api_secret ]:
    raise Exception('Missing Censys API ID or secret')

class TestCloudFlair(unittest.TestCase):
    def test_cloudflair(self):
        candidates = cloudflair.find_hosts('myvulnerable.site', api_id, api_secret)
        self.assertEquals(candidates, set([ '188.226.197.73' ]))
        origins = cloudflair.find_origins('myvulnerable.site', candidates)
        self.assertEquals(origins[0][0], '188.226.197.73')

if __name__ == '__main__':
    unittest.main()
