import logging
from typing import List
from hikari import Snowflake

from lib.log_helper.log_helper import LogHelper

quantum_kat_logger: logging.Logger = LogHelper.create_logger(
    logger_name="quantum_kat",
    log_file="logs/quantum_kat.log",
    file_log_level=logging.DEBUG,
    stream_log_level=logging.INFO,
    rotate_logs=True,
)

loaded_extensions: List[str] = []
owner_ids: List[Snowflake] = []
