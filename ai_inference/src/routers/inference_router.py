from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from infrastructure.jwt_service import decode_token
from src.application.dto.inference_dto import InferenceRequest, InferenceResponse
from src.application.services.inference_service import perform_inference

router = APIRouter()
auth_scheme = HTTPBearer()


@router.post("/infer", response_model=InferenceResponse)
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

    try:
        decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = perform_inference(request.text)
    return InferenceResponse(result=result)
