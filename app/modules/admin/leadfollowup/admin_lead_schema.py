from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, ConfigDict


class FollowUpCreateRequest(BaseModel):
    lead_id: UUID
    note: str
    next_followup_date: Optional[datetime] = None



class FollowUpResponse(BaseModel):
    id: UUID
    lead_id: UUID
    note: str
    next_followup_date: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LeadFollowupFilter(BaseModel):
    lead_id: UUID
