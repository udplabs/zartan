import pytest

from utils.udp import get_udp_oauth_access_token, is_udp_config_valid
from tests.base_zartan_test import BaseZartanTest


class UdpTest(BaseZartanTest):

    GOOD_UDP_CONFIG = {
        "issuer": "https://udp.okta.com/oauth2/default",
        "client_id": "test_id",
        "client_secret": "test_secret"
    }

    BAD_UDP_CONFIG = {
        "issuer": "",
        "client_id": "",
        "client_secret": None
    }

    def setUp(self):
        super().setUp()
        self.logger.info('set_up()')

    def test_is_udp_config_valid(self):
        self.logger.info("test_is_udp_config_valid()")

        good_result = is_udp_config_valid(self.GOOD_UDP_CONFIG)
        self.assertTrue(good_result)

        bad_result = is_udp_config_valid(self.BAD_UDP_CONFIG)
        self.assertFalse(bad_result)

    @pytest.mark.skip(reason="Used for debuging but not meant for unit test")
    def test_get_udp_oauth_access_token(self, mocker):
        self.logger.info("test_get_udp_oauth_access_token()")

        result = get_udp_oauth_access_token(self.GOOD_UDP_CONFIG)
        self.logger.debug("result: {0}".format(result))
        self.assertIsNotNone(result)
