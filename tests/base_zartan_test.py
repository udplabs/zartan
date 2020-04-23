import os
import unittest
import logging
import logging.config

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config", os.getenv("PYTESTS_LOGGER_CONFIG", "pytests_logger.config"))
logging.config.fileConfig(fname=log_file_path, disable_existing_loggers=False)


class BaseZartanTest(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        self.logger.info('set_up()')

    def tearDown(self):
        self.logger.info('tear_down()')
