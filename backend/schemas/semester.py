from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SemesterResponse(BaseModel):
    sem_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SemesterCreate(SemesterResponse):
    pass


class SemesterUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None