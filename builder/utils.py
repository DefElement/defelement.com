def to_array(data):
    import numpy as np

    if isinstance(data, (list, tuple)):
        return np.array([to_array(i) for i in data])
    return float(data)
