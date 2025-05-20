from infrastructure.jwt_service import create_token
from datetime import datetime, timedelta

payload = {"sub": "user123", "exp": datetime.utcnow() + timedelta(hours=1)}

token = create_token(payload)
print(token)
