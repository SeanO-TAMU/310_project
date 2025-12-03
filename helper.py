class Session:
    token = None
    role = None
    user_id = None

def create_json(keys, values):
    json = {}
    if len(keys) != len(values):
        raise ValueError("length of keys and values mismatch")
    
    for k, v in zip(keys, values):
        json[f"{k}"] = v
        
    return json

