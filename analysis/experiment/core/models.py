"""ReviewGate — response/request models (single source of truth)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=2000)
    rating: int = Field(ge=1, le=5)


class VoteIn(BaseModel):
    value: int = Field(ge=-1, le=1)


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str


class ReviewOut(BaseModel):
    id: int
    title: str
    body: str
    author: str
    status: str
    rating: int
    votes: int


class ReviewListOut(BaseModel):
    items: list[ReviewOut]
    total: int


class CommentOut(BaseModel):
    id: int
    review_id: int
    author: str
    body: str


class CommentListOut(BaseModel):
    items: list[CommentOut]


class UserListOut(BaseModel):
    items: list[UserOut]


class ReviewStats(BaseModel):
    total: int
    approved: int
    flagged: int
    pending: int


class AuditOut(BaseModel):
    id: int
    actor: str
    action: str


class AuditListOut(BaseModel):
    items: list[AuditOut]


class DashboardOut(BaseModel):
    n_users: int
    n_reviews: int
    n_approved: int
    n_flags: int


class ConfigOut(BaseModel):
    max_editors: str
    backup_interval_h: str
    audit_enabled: str


class OkOut(BaseModel):
    ok: bool = True