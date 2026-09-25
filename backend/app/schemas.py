from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class RecordIn(BaseModel):
    module: str
    name: str
    code: str = ""
    category: str = "General"
    status: str = "Active"
    notes: str = ""

class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float = Field(default=0, ge=0)
    source: str = "MOBILE"
    tracking_context: str = "TRANSPORT"
    status: str = "ACTIVE"

class SosIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    message: str = ""

class AIChatRequest(BaseModel):
    message: str


class InstitutionIn(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    institution_type: str
    code: str = Field(min_length=2, max_length=50)
