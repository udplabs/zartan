
import logging

from functools import wraps


logger = logging.getLogger(__name__)

def apply_remote_config(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        logger.debug("apply_remote_config()")



        return f(*args, **kws)
    return decorated_function