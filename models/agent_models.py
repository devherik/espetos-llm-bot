from pydantic import BaseModel

class RunResponse(BaseModel):
    answer: str
    content: str
    
    class Config:
        orm_mode = True