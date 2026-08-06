"""Logging setup shared by the application."""
import logging
from config import LOGS_DIR


def configure_logging() -> None:
    """Configure activity and error logs once."""
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    activity = logging.FileHandler(LOGS_DIR / "activity.log", encoding="utf-8")
    activity.setFormatter(formatter)
    errors = logging.FileHandler(LOGS_DIR / "errors.log", encoding="utf-8")
    errors.setLevel(logging.ERROR)
    errors.setFormatter(formatter)
    root.addHandler(activity)
    root.addHandler(errors)
