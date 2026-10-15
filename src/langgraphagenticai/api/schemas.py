from typing import Literal
from pydantic import BaseModel, Field, SecretStr
class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    api_key: SecretStr
    model_id: str
class FeedbackRequest(BaseModel):
    answer_id: str
    rating: Literal['accepted', 'rejected']
    comment: str = Field(default='', max_length=2000)
