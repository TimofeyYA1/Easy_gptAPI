from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID

class DialogQuery(BaseModel):
    dialog_id: UUID
    token: str
    message: str
    max_tokens: int

class DialogRename(BaseModel):
    dialog_id: UUID
    token: str
    new_title: str

class DialogCreateRequest(BaseModel):
    token: str
    title: Optional[str] = "Диалог"
    model: Optional[str] = "gpt-4o mini"
    temperature: Optional[float] = 0.3
    system: Optional[str] = None
