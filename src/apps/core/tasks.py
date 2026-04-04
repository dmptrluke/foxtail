import time
from pathlib import Path

from huey import crontab
from huey.contrib.djhuey import periodic_task

HEARTBEAT_FILE = Path('/tmp/huey-heartbeat')  # noqa: S108


@periodic_task(crontab(minute='*'))
def heartbeat():
    """Write a timestamp so the container healthcheck can verify the worker is alive."""
    HEARTBEAT_FILE.write_text(str(time.time()))
