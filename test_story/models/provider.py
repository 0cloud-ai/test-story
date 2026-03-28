from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProviderConfig(BaseModel):
    base_url: str
    api_key: str | None = None
    model: str
    max_tokens: int = 16384


class ProviderCreate(BaseModel):
    name: str
    type: str
    config: ProviderConfig


class ProviderUpdate(BaseModel):
    config: ProviderConfig | None = None


class Provider(BaseModel):
    id: str
    name: str
    type: str
    config: ProviderConfig
    created_at: datetime
    updated_at: datetime

    def masked(self) -> Provider:
        cfg = self.config.model_copy()
        if cfg.api_key:
            cfg.api_key = cfg.api_key[:6] + "***"
        return self.model_copy(update={"config": cfg})
