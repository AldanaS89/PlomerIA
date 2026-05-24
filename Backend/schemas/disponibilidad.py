from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BloqueOut(BaseModel):
    id: int
    inicio: datetime
    fin: datetime
    ocupado: bool
    descripcion: Optional[str] = None
    class Config:
        from_attributes = True


class BloquearRequest(BaseModel):
    inicio: datetime
    fin: datetime
    descripcion: Optional[str] = None

