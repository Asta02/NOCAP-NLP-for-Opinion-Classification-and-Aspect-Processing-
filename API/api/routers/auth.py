from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from api.schemas.auth_requests import (
    LoginRequest,
)

from api.schemas.auth_responses import (
    LoginResponse,
)

from api.dependencies import (
    get_auth_service,
)

from services.auth_service import (
    AuthService,
)

router = APIRouter(
    prefix="/auth",
)


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    service: AuthService = Depends(
        get_auth_service,
    ),
):

    try:

        return service.login(

            username=request.username,

            password=request.password,

        )

    except ValueError as exc:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=str(exc),

        )