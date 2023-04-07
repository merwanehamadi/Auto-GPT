import os
import uvicorn
from app.settings import settings


def main() -> None:
    log_config_path = os.path.join(os.path.dirname(__file__), "logging_config.yaml")

    uvicorn.run(
        "app.web.application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.value.lower(),
        log_config=log_config_path,
        factory=True,
    )


if __name__ == "__main__":
    main()
