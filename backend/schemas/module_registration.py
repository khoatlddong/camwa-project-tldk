from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ModuleRegistrationResponse(BaseModel):
    module_reg_id: int
    student_id: str
    module_id: str
    lecturer_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ModuleRegistrationCreate(ModuleRegistrationResponse):
    pass


class ModuleRegistrationUpdate(BaseModel):
    student_id: Optional[str] = None
    module_id: Optional[str] = None
    lecturer_id: Optional[str] = None

