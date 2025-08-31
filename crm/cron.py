import logging
from datetime import datetime

logging.basicConfig(
    filename="/tmp/crm_heartbeat_log.txt",
    level=logging.INFO,
    format="%(message)s",
    filemode="a",
)

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    logging.info(f"{timestamp} CRM is alive")