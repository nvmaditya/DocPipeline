"""FastAPI application entrypoint for Phase 5 backend foundation."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .adapters.pipeline_adapter import PipelineAdapter
from .api.auth import router as auth_router
from .api.community import router as community_router
from .api.documents import router as docs_router
from .api.search import router as search_router
from .api.study import router as study_router
from .config import get_settings
from .services.auth_service import AuthService
from .services.community_service import CommunityService
from .services.document_service import DocumentService
from .services.rag_service import RagService
from .services.search_service import SearchService
from .services.study_service import StudyService


def create_app() -> FastAPI:
    settings = get_settings()

    auth_service = AuthService(db_dir=settings.user_store_root)
    pipeline_adapter = PipelineAdapter(
        base_config_path=settings.docpipe_config_path,
        store_root=settings.user_store_root,
        community_store_root=settings.community_store_root,
    )
    community_service = CommunityService(
        pipeline_adapter=pipeline_adapter,
        books_root=settings.books_root,
    )
    document_service = DocumentService(pipeline_adapter=pipeline_adapter)
    rag_service = RagService()
    search_service = SearchService(
        pipeline_adapter=pipeline_adapter,
        rag_service=rag_service,
    )
    study_service = StudyService(pipeline_adapter=pipeline_adapter)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            pipeline_adapter.close()

    app = FastAPI(title=settings.project_name, debug=settings.debug, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.auth_service = auth_service
    app.state.community_service = community_service
    app.state.document_service = document_service
    app.state.search_service = search_service
    app.state.study_service = study_service
    app.state.pipeline_adapter = pipeline_adapter

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(community_router)
    app.include_router(docs_router)
    app.include_router(search_router)
    app.include_router(study_router)

    return app


app = create_app()
