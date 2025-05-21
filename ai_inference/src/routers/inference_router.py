from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from infrastructure.jwt_service import decode_token, create_token
from src.schema.dto.inference_dto import InferenceRequest, InferenceResponse, InferenceTokenResponse
from src.application.services.inference_service import perform_inference
from config.response_handler import ResponseHandler

router = APIRouter(prefix="/infer", tags=["Inference"])
auth_scheme = HTTPBearer()


@router.post("", response_model=InferenceResponse)
def infer(
    request: InferenceRequest,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """
    Perform inference on the given text by reversing it.

    Args:
        request (InferenceRequest): The input text to be processed.
        credentials (HTTPAuthorizationCredentials): The JWT token to authorize the request.

    Returns:
        InferenceResponse: The reversed version of the input text.

    Raises:
        HTTPException: If the token is invalid.
    """
    decode_token(credentials.credentials)
    result = perform_inference(request.text)
    return ResponseHandler.success(data=InferenceResponse(result=result))


@router.get("/token", response_model=InferenceTokenResponse)
def create_infer_token():
    """
    Generate a JWT token for inference authorization.

    This endpoint creates a new JSON Web Token (JWT) for a user, which can be
    used to authorize inference requests.

    Returns:
        InferenceTokenResponse: A response containing the generated JWT token.

    Raises:
        HTTPException: If an error occurs during token creation.
    """

    try:
        payload = {"sub": "user123", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = create_token(payload=payload)
        return ResponseHandler.success(data=InferenceTokenResponse(token=token))
    except Exception as e:
        return ResponseHandler.error(exception=e)