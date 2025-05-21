import jwt
from config.settings import settings


def create_token(payload: dict) -> str:
    """
    Create a JSON Web Token (JWT) from the given payload.

    Args:
        payload (dict): The payload to encode into the JWT. It typically contains
                        claims such as 'sub' (subject) and 'exp' (expiration time).

    Returns:
        str: The encoded JWT as a string.
    """

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode a JSON Web Token (JWT) to extract the payload.

    Args:
        token (str): The encoded JWT as a string.

    Returns:
        dict: The decoded payload from the JWT, which typically contains claims
              such as 'sub' (subject) and 'exp' (expiration time).

    Raises:
        jwt.exceptions.DecodeError: If the token cannot be decoded.
        jwt.exceptions.ExpiredSignatureError: If the token has expired.
        jwt.exceptions.InvalidTokenError: If the token is invalid for other reasons.
    """

    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
