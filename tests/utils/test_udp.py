import pytest

from utils.udp import get_udp_oauth_access_token
from tests.base_zartan_test import BaseZartanTest


class UdpTest(BaseZartanTest):

    @pytest.mark.skip(reason="Work in progress")
    def test_get_udp_oauth_access_token(self):
        self.logger.info("test_get_udp_oauth_access_token()")
        result = get_udp_oauth_access_token()
        self.logger.debug("result: {0}".format(result))
        self.assertIsNotNone(result)
