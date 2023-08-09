import random
import string
import uuid

def generate_api_key():
    # Generate a random prefix of 7 characters
    prefix = ''.join(random.choices(string.ascii_letters, k=7))
    
    # Generate a UUID as the main part of the key
    key = str(uuid.uuid4())
    
    # Combine prefix and key
    token = f"{prefix}.{key}"
    
    return prefix, token  # We return both the prefix and the token for easier assignment in the model
