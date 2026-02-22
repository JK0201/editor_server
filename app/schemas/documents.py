from typing import Literal

from pydantic import BaseModel, Field


class SpeakerCreate(BaseModel):
    temp_id: str
    name: str


class SpeakerUpdate(BaseModel):
    id: int
    name: str


class SpeakerDiff(BaseModel):
    created: list[SpeakerCreate] = Field([])
    updated: list[SpeakerUpdate] = Field([])
    deleted: list[int] = Field([])


class ScriptLineCreate(BaseModel):
    temp_id: str
    speaker_id: str  # 기존 speaker → DB id 문자열, 새 speaker → temp_id
    text: str
    start_time: str | None = Field(None)
    order: int


class ScriptLineUpdate(BaseModel):
    id: int
    speaker_id: int | None = Field(None)
    text: str | None = Field(None)
    start_time: str | None = Field(None)


class OrderItem(BaseModel):
    id: int
    order: int


class ScriptLineDiff(BaseModel):
    speakers: SpeakerDiff = SpeakerDiff()
    created: list[ScriptLineCreate] = Field([])
    updated: list[ScriptLineUpdate] = Field([])
    deleted: list[int] = Field([])
    orders: list[OrderItem] = Field([])
    status: Literal["in_progress", "completed"] | None = Field(None)
