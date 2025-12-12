def normalize_log(log: dict) -> dict:
    """
    Convert raw log into standardized internal format.
    """

    return {
        "user": log["user_id"],
        "device": log["device_id"],
        "event_type": "app_usage",
        "event_data": log["event"],
        "source": log["source"],
        "timestamp": log["timestamp"]
    }

# the above function normalize_log will take incoming raw log (from collector API) and convert it into a standard internal format
# that the worker will read later

