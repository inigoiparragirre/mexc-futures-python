"""Header generation utilities for MEXC Futures SDK."""

import hashlib
import json
import time
from typing import Any, Dict, Optional

from .constants import DEFAULT_HEADERS


class SDKOptions:
    """SDK configuration options."""
    
    def __init__(
        self,
        auth_token: str,
        user_agent: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.auth_token = auth_token
        self.user_agent = user_agent
        self.custom_headers = custom_headers or {}


def mexc_crypto(key: str, obj: Any) -> Dict[str, str]:
    """
    Generate MEXC crypto signature using MD5 algorithm.
    
    Args:
        key: WEB authentication key
        obj: Request object to sign
        
    Returns:
        Dictionary with timestamp and signature
    """
    date_now = str(int(time.time() * 1000))
    g = hashlib.md5((key + date_now).encode()).hexdigest()[7:]
    s = json.dumps(obj, separators=(',', ':'))  # Compact JSON without spaces
    sign = hashlib.md5((date_now + s + g).encode()).hexdigest()
    
    return {"time": date_now, "sign": sign}


def generate_headers(
    options: SDKOptions,
    include_auth: bool = True,
    request_body: Optional[Any] = None,
) -> Dict[str, str]:
    """
    Generate HTTP headers for API requests.
    
    Args:
        options: SDK configuration options
        include_auth: Whether to include authentication headers
        request_body: Request body for signature (optional)
        
    Returns:
        Dictionary of HTTP headers
    """
    headers = dict(DEFAULT_HEADERS)
    
    # Override user agent if provided
    if options.user_agent:
        headers["user-agent"] = options.user_agent
    
    # Add custom headers if provided
    headers.update(options.custom_headers)
    
    # Add authentication headers for private endpoints
    if include_auth:
        # Use WEB token for authentication
        headers["authorization"] = options.auth_token
        
        # Add MEXC signature for POST requests with body
        if request_body is not None:
            signature = mexc_crypto(options.auth_token, request_body)
            
            headers["x-mxc-nonce"] = signature["time"]
            headers["x-mxc-sign"] = signature["sign"]
    
    return headers