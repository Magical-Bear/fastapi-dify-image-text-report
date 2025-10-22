import os
import hmac
from typing import Optional
from functools import lru_cache
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache()
def _get_expected_api_key() -> str:
    api_key = os.getenv("FASTAPI_API_KEY")
    if not api_key:
        raise RuntimeError("FASTAPI_API_KEY is not set in environment variables")
    return api_key


async def verify_bearer_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> None:
    """
    全局依赖：验证 Authorization: Bearer <token>
    - 缺失或 scheme 不为 Bearer -> 401
    - 值不匹配 -> 401
    """
    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        # 返回标准 WWW-Authenticate 头，便于客户端与文档 UI 处理
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    provided = credentials.credentials or ""
    expected = _get_expected_api_key()

    # 常量时间比较，避免时序攻击
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )