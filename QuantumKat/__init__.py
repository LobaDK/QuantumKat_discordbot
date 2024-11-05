import logging

from lib.log_helper.log_helper import LogHelper

quantum_kat_logger: logging.Logger = LogHelper.create_logger(
    logger_name="quantum_kat",
    log_file="logs/quantum_kat.log",
    file_log_level=logging.DEBUG,
    stream_log_level=logging.INFO,
    rotate_logs=True,
)
