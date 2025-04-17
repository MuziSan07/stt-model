from db import get_token_by_value
from datetime import datetime

def validate_token(token: str):
    token_data = get_token_by_value(token)
    
    if not token_data:
        return None
    
    # Check if the token is active
    if token_data["status"] != "active":
        return None
    
    # Check if the token is expired
    expiration_date = datetime.strptime(token_data["expires_on"], '%Y-%m-%d %H:%M:%S')
    if datetime.utcnow() > expiration_date:
        return None
    
    return token_data
