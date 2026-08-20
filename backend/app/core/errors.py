from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class APIException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})
        self.code = code
        self.message = message

async def api_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", None)
    
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        code = exc.detail["code"]
        message = exc.detail["message"]
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)

    error_payload = {
        "detail": message,
        "error": {
            "code": code,
            "message": message
        },
        "request_id": request_id
    }
    return JSONResponse(status_code=exc.status_code, content=error_payload)
