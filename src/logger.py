import logging
import os

import logzero

log_level = os.getenv("LOG_LEVEL", "DEBUG")
log_output_file = os.getenv("LOG_OUTPUT_FILE", "/tmp/message_bus.log")
logzero.loglevel(log_level)

if log_level == "DEBUG":
    logzero.loglevel(logging.DEBUG)

logzero.logfile(log_output_file)
logger = logzero.logger
