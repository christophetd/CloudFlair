import unittest

import utils


class TestUtils(unittest.TestCase):
    def test_get_random_user_agent(self):
        self.assertIsNotNone(utils.get_user_agent())
