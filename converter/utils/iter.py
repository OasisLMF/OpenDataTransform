def ensure_row_iterable(obj):
    if hasattr(obj, "iterrows"):
        return [dict(v) for i, v in obj.iterrows()]
    else:
        return obj
