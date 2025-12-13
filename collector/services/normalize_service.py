def normalize_log(log: dict) -> dict:
    """
    Convert raw log into standardized internal format.
    """

    return {
        "timestamp": log["ts"],
        "user": log["user_id"],
        "domain": log["domain"],
        "url": log["url"],
        "method": log["method"],
        "upload_size_bytes": log["upload_size_bytes"]
    }

# the above function normalize_log will take incoming raw log (from collector API) and convert it into a standard internal format
# that the worker will read later

