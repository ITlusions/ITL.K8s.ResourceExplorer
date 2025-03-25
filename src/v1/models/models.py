from pydantic import BaseModel
from typing import List, Optional, Dict


class ExampleModel(BaseModel):
    key1: str
    key2: int
    key3: Optional[str] = None

