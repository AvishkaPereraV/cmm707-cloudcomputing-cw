from pydantic import BaseModel
from typing import Optional

class AnalyticsEvent(BaseModel):
    event_type: str
    page_url: str
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
