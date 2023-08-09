import random
import string
import uuid

from app.models import ApiKey

def generate_api_key():
    # Generate a random prefix of 7 characters
    prefix = ''.join(random.choices(string.ascii_letters, k=7))
    
    # Generate a UUID as the main part of the key
    key = str(uuid.uuid4())
    
    # Combine prefix and key
    token = f"{prefix}.{key}"
    
    return prefix, token  # We return both the prefix and the token for easier assignment in the model
  
def is_authenticated(request):
  api_key = request.headers.get("X-Api-Key")
  is_api_key_valid = check_api_key(api_key)
  is_authenticated = check_auth(request.user.is_authenticated, is_api_key_valid)
  return is_authenticated
  
def check_api_key(api_key):
    # Get the API key from the request
    if api_key is None:
        return False
    else:
        # Split the API key into prefix and key
        prefix, key = api_key.split(".")
        
        # Check if the prefix exists in the database
        try:
            api_key = ApiKey.objects.get(prefix=prefix)
        except:
            return False
        
        # Check if the key matches
        if api_key.key == key:
            return True
        else:
            return False

def check_auth(is_user_authenticated, is_api_key_valid):
    if is_user_authenticated or is_api_key_valid:
        return True
    else:
        return False