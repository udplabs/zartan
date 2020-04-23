from app import healthcheck
from tests.base_zartan_test import BaseZartanTest


class AppTest(BaseZartanTest):

    def test_healthcheck(self):
        self.logger.info("test_healthcheck()")
        result = healthcheck()
        self.logger.debug("result: {0}".format(result))
        self.assertEqual("OK", result)
