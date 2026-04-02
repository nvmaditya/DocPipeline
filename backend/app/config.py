"""Runtime settings for the backend app."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    project_name: str = "Document Intelligence API"
    api_prefix: str = "/api/v1"
    debug: bool = False
    docpipe_config_path: str = "config.yaml"
    user_store_root: str = "store/backend_users"
    community_store_root: str = "store/community_books"
    books_root: str = "Books"


def get_settings() -> Settings:
    return Settings(
        project_name=os.getenv("BACKEND_PROJECT_NAME", "Document Intelligence API"),
        api_prefix=os.getenv("BACKEND_API_PREFIX", "/api/v1"),
        debug=os.getenv("BACKEND_DEBUG", "false").lower() == "true",
        docpipe_config_path=os.getenv("BACKEND_DOCPIPE_CONFIG", "config.yaml"),
        user_store_root=os.getenv("BACKEND_USER_STORE_ROOT", "store/backend_users"),
        community_store_root=os.getenv("BACKEND_COMMUNITY_STORE_ROOT", "store/community_books"),
        books_root=os.getenv("BACKEND_BOOKS_ROOT", "Books"),
    )
