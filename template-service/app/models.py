from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field
from jinja2 import Template as J2Template
from datetime import datetime

class CreateTemplateReq(BaseModel):
    code: str
    content: str
    language: Optional[str] = 'en'

class TemplateOut(BaseModel):
    id: int
    code: str
    content: str
    language: str

    class Config:
        orm_mode = True

class Template(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=120, unique=True, index=True, nullable=False)
    content: str = Field(nullable=False)
    language: str = Field(default='en', max_length=10)
    created_at: datetime = Field(default_factory=datetime.now)

    def render(self, vars: dict) -> str:
        j = J2Template(self.content)
        return j.render(**(vars or {}))
    
