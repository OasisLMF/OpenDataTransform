def ensure_row_iterable(obj):
    if hasattr(obj, "iterrows"):
        return obj.iterrows()
    else:
        return obj
