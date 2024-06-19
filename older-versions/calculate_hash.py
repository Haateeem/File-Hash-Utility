import hashlib

def calculate_hash(file_path, algorithm='sha256'):
    try:
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' does not exist.")
        return None
