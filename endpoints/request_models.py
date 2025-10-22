import json
from fastapi import Form, UploadFile, File
from pydantic import BaseModel
from datetime import date

from starlette.datastructures import FormData


class AskQuestionModel(BaseModel):
    question: str
    conversation_id: int | None = None
    top_k: int = 5
    history: list[dict | list] = []


async def parse_form_data(form_data: Form) -> (AskQuestionModel, UploadFile):
    question = form_data.get("question")
    conversation_id = form_data.get("conversation_id")
    top_k = form_data.get("top_k")
    history = form_data.get("history")
    if history:
        history = json.loads(history)
    image: UploadFile = form_data.get("image")
    return (
        AskQuestionModel(question=question,
                         conversation_id=conversation_id,
                         top_k=top_k,
                         history=history),
        image
    )


class QuestionFetchImageModel(BaseModel):
    questions: list[str]


class KeywordsModel(BaseModel):
    keywords: list[str]
    title: str


