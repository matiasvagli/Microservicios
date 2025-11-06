from pydantic import BaseModel
from typing import Any, Optional

class FailedPaymentEvent(BaseModel):
    event_type: str
    payload: Any
    status: str = "pending"
    retry_count: int = 0
    last_error: Optional[str] = None
