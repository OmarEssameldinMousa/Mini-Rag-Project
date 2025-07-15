from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str
    chuk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[bool] = 0