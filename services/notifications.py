"""Best-effort desktop notifications."""


def notify(title: str, message: str) -> None:
    """Show a notification when the optional platform backend is available."""
    try:
        from plyer import notification
        notification.notify(title=title, message=message, app_name="AI Search Assistant", timeout=5)
    except Exception:
        pass
