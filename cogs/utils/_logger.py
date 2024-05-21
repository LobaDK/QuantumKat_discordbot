from logging import DEBUG
from helpers import LogHelper

log_helper = LogHelper()

# Create loggers for each cog and module.
# It is possible to dynamically create them all in a for loop
# but then IDEs won't be able to provide autocompletion or linting
quantumkat_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="QuantumKat", log_file="logs/quantumkat/QuantumKat.log"
    )
)

activity_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Activity", log_file="logs/activity/Activity.log"
    )
)

auth_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Auth", log_file="logs/auth/Auth.log"
    )
)

chat_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Chat", log_file="logs/chat/Chat.log"
    )
)

chat_history_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="ChatHistory", log_file="logs/chat/ChatHistory.log"
    )
)

control_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Control", log_file="logs/control/Control.log"
    )
)

entanglement_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Entanglement", log_file="logs/entanglement/Entanglement.log"
    )
)

field_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Field", log_file="logs/field/Field.log"
    )
)

tunnel_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Tunnel", log_file="logs/tunnel/Tunnel.log"
    )
)

timer_logger = log_helper.create_logger(
    log_helper.TimedRotatingFileAndStreamHandler(
        logger_name="Timer", log_file="logs/timer/Timer.log", file_log_level=DEBUG
    )
)
