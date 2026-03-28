from __future__ import annotations

from fastapi import APIRouter, Depends

import duckdb

from test_story.db.queries import providers as prov_q
from test_story.models.common import PaginatedResponse
from test_story.models.provider import Provider, ProviderCreate, ProviderUpdate
from test_story.server.deps import get_db

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("", status_code=201, response_model=Provider)
def create_provider(data: ProviderCreate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return prov_q.create_provider(db, data).masked()


@router.get("", response_model=PaginatedResponse[Provider])
def list_providers(type: str | None = None, page: int = 1, per_page: int = 20,
                   db: duckdb.DuckDBPyConnection = Depends(get_db)):
    items, total = prov_q.list_providers(db, type_filter=type, page=page, per_page=per_page)
    return PaginatedResponse(items=[i.masked() for i in items], total=total, page=page, per_page=per_page)


@router.get("/{provider_id}", response_model=Provider)
def get_provider(provider_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return prov_q.get_provider(db, provider_id).masked()


@router.patch("/{provider_id}", response_model=Provider)
def update_provider(provider_id: str, data: ProviderUpdate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return prov_q.update_provider(db, provider_id, data).masked()


@router.delete("/{provider_id}", status_code=204)
def delete_provider(provider_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    prov_q.delete_provider(db, provider_id)
