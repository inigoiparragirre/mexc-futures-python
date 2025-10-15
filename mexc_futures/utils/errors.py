"""Error handling utilities for MEXC Futures SDK."""

import json
from datetime import datetime
from typing import Any, Dict, Optional, Union


class MexcFuturesError(Exception):
    """Base error class for MEXC Futures SDK."""
    
    def __init__(
        self,
        message: str,
        code: Optional[Union[str, int]] = None,
        status_code: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.original_error = original_error
        self.timestamp = datetime.now()
    
    def get_user_friendly_message(self) -> str:
        """Get a user-friendly error message."""
        return str(self)
    
    def get_details(self) -> Dict[str, Any]:
        """Get error details for logging."""
        return {
            "name": self.__class__.__name__,
            "message": str(self),
            "code": self.code,
            "status_code": self.status_code,
            "timestamp": self.timestamp.isoformat(),
        }


class MexcAuthenticationError(MexcFuturesError):
    """Authentication related errors."""
    
    def __init__(
        self, 
        message: Optional[str] = None, 
        original_error: Optional[Exception] = None
    ) -> None:
        default_message = "Authentication failed. Please check your authorization token."
        super().__init__(
            message or default_message,
            code="AUTH_ERROR",
            status_code=401,
            original_error=original_error,
        )
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly authentication error message."""
        if self.code == 401:
            return (
                "❌ Authentication failed. Your authorization token may be expired or invalid. "
                "Please update your WEB token from browser Developer Tools."
            )
        return f"❌ Authentication error: {self}"


class MexcApiError(MexcFuturesError):
    """API related errors (4xx, 5xx responses)."""
    
    def __init__(
        self,
        message: str,
        code: Union[str, int],
        status_code: int,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        response_data: Optional[Any] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, code, status_code, original_error)
        self.endpoint = endpoint
        self.method = method
        self.response_data = response_data
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly API error message."""
        status = self.status_code
        message = str(self)
        
        if status == 400:
            return f"❌ Bad Request: {message}. Please check your request parameters."
        elif status == 401:
            return f"❌ Unauthorized: {message}. Your authorization token may be expired."
        elif status == 403:
            return f"❌ Forbidden: {message}. You don't have permission for this operation."
        elif status == 404:
            return f"❌ Not Found: {message}. The requested resource was not found."
        elif status == 429:
            return f"❌ Rate Limit Exceeded: {message}. Please reduce request frequency."
        elif status == 500:
            return f"❌ Server Error: {message}. MEXC server is experiencing issues."
        elif status in (502, 503, 504):
            return f"❌ Service Unavailable: {message}. MEXC service is temporarily unavailable."
        else:
            return f"❌ API Error ({status}): {message}"
    
    def get_details(self) -> Dict[str, Any]:
        """Get detailed error information."""
        details = super().get_details()
        details.update({
            "endpoint": self.endpoint,
            "method": self.method,
            "response_data": self.response_data,
        })
        return details


class MexcNetworkError(MexcFuturesError):
    """Network related errors (timeouts, connection issues)."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        super().__init__(
            message,
            code="NETWORK_ERROR",
            original_error=original_error,
        )
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly network error message."""
        message = str(self)
        if "timeout" in message.lower():
            return "❌ Request timeout. Please check your internet connection and try again."
        elif any(x in message for x in ["connection", "refused", "unreachable"]):
            return "❌ Connection failed. Please check your internet connection."
        return f"❌ Network error: {message}"


class MexcValidationError(MexcFuturesError):
    """Validation errors for request parameters."""
    
    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly validation error message."""
        if self.field:
            return f"❌ Validation error for field '{self.field}': {self}"
        return f"❌ Validation error: {self}"


class MexcSignatureError(MexcFuturesError):
    """Signature related errors."""
    
    def __init__(
        self, 
        message: Optional[str] = None, 
        original_error: Optional[Exception] = None
    ) -> None:
        default_message = "Request signature verification failed"
        super().__init__(
            message or default_message,
            code="SIGNATURE_ERROR",
            status_code=602,
            original_error=original_error,
        )
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly signature error message."""
        return (
            "❌ Signature verification failed. This usually means your authorization token "
            "is invalid or expired. Please get a fresh WEB token from your browser."
        )


class MexcRateLimitError(MexcFuturesError):
    """Rate limiting errors."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(
            message,
            code="RATE_LIMIT",
            status_code=429,
            original_error=original_error,
        )
        self.retry_after = retry_after
    
    def get_user_friendly_message(self) -> str:
        """Get user-friendly rate limit error message."""
        retry_msg = f" Please retry after {self.retry_after} seconds." if self.retry_after else ""
        return f"❌ Rate limit exceeded: {self}.{retry_msg}"


def parse_httpx_error(
    error: Exception,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
) -> MexcFuturesError:
    """Parse httpx error and convert to appropriate MEXC error."""
    
    # Import here to avoid circular imports
    import httpx
    
    # Network/connection errors
    if isinstance(error, (httpx.ConnectError, httpx.NetworkError)):
        return MexcNetworkError(str(error), error)
    
    # Timeout errors
    if isinstance(error, httpx.TimeoutException):
        return MexcNetworkError("Request timeout", error)
    
    # HTTP response errors
    if isinstance(error, httpx.HTTPStatusError):
        response = error.response
        status_code = response.status_code
        
        try:
            data = response.json()
            message = data.get("message", str(error))
            code = data.get("code", status_code)
        except Exception:
            message = str(error)
            code = status_code
        
        # Specific error types
        if status_code == 401:
            return MexcAuthenticationError(message, error)
        elif status_code == 429:
            retry_after = response.headers.get("retry-after")
            retry_after_int = int(retry_after) if retry_after else None
            return MexcRateLimitError(message, retry_after_int, error)
        else:
            # Check for signature error by code or message
            if (
                code == 602
                or "signature" in str(message).lower()
            ):
                return MexcSignatureError(message, error)
            
            try:
                response_data = response.json()
            except Exception:
                response_data = response.text
                
            return MexcApiError(
                message,
                code,
                status_code,
                endpoint,
                method,
                response_data,
                error,
            )
    
    # Fallback for unknown errors
    return MexcFuturesError(
        str(error),
        code="UNKNOWN_ERROR",
        original_error=error,
    )


def format_error_for_logging(error: MexcFuturesError) -> str:
    """Format error for logging."""
    details = error.get_details()
    return f"{error.get_user_friendly_message()}\nDetails: {json.dumps(details, indent=2)}"