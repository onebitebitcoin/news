from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CustomSourceAnalyzeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    list_url: str = Field(min_length=1, max_length=2000)


class CustomSourcePreviewItem(BaseModel):
    title: str
    url: str
    published_at: str
    summary: Optional[str] = None
    image_url: Optional[str] = None


class CustomSourceDraft(BaseModel):
    slug_suggestion: str
    name: str
    list_url: str
    fetch_mode: str = "scrape"
    extraction_rules: dict[str, Any]
    normalization_rules: Optional[dict[str, Any]] = None
    ai_model: Optional[str] = None


class CustomSourceAnalyzeResponse(BaseModel):
    draft: CustomSourceDraft
    preview_items: list[CustomSourcePreviewItem]
    warnings: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
    is_valid: bool = True


class CustomSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=120)
    list_url: str = Field(min_length=1, max_length=2000)
    extraction_rules: dict[str, Any]
    normalization_rules: Optional[dict[str, Any]] = None
    is_active: bool = True
    ai_model: Optional[str] = None


class CustomSourceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=120)
    list_url: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    extraction_rules: Optional[dict[str, Any]] = None
    normalization_rules: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    ai_model: Optional[str] = None


class CustomSourceResponse(BaseModel):
    id: int
    name: str
    slug: str
    list_url: str
    fetch_mode: str
    is_active: bool
    ai_model: Optional[str] = None
    extraction_rules: dict[str, Any]
    normalization_rules: Optional[dict[str, Any]] = None
    last_analyzed_at: Optional[datetime] = None
    last_validation_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CustomSourceListResponse(BaseModel):
    sources: list[CustomSourceResponse]
