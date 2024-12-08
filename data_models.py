from pydantic import BaseModel


class Chat(BaseModel):
    id: int


class Message(BaseModel):
    message_id: int
    text: str
    chat: Chat


class Update(BaseModel):
    update_id: int
    message: Message
