"""FastAPI application entrypoint for Phase 5 backend foundation."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .adapters.pipeline_adapter import PipelineAdapter
from .api.auth import router as auth_router
from .api.documents import router as docs_router
from .api.search import router as search_router
from .config import get_settings
from .services.auth_service import AuthService
from .services.document_service import DocumentService
from .services.rag_service import RagService
from .services.search_service import SearchService


def create_app() -> FastAPI:
    settings = get_settings()

    auth_service = AuthService()
    pipeline_adapter = PipelineAdapter(
        base_config_path=settings.docpipe_config_path,
        store_root=settings.user_store_root,
    )
    document_service = DocumentService(pipeline_adapter=pipeline_adapter)
    rag_service = RagService()
    search_service = SearchService(
        pipeline_adapter=pipeline_adapter,
        rag_service=rag_service,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            pipeline_adapter.close()

    app = FastAPI(title=settings.project_name, debug=settings.debug, lifespan=lifespan)

    app.state.auth_service = auth_service
    app.state.document_service = document_service
    app.state.search_service = search_service
    app.state.pipeline_adapter = pipeline_adapter

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(docs_router)
    app.include_router(search_router)

    return app


app = create_app()
