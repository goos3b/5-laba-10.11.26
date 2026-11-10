def summarize(data):
    if not data:
        return {"count": 0, "mean": 0, "min": 0, "max": 0}
    return {
        "count": len(data),
        "mean": sum(data) / len(data),
        "min": min(data),
        "max": max(data)
    }
