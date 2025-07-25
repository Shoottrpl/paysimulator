import sentry_sdk
from sanic import Sanic
from sanic_ext import Config, Extend
from sentry_sdk.integrations.asyncio import AsyncioIntegration

from app.blueprints import api
from app.middleware.jwt_auth import jwt_authentication
from app.middleware.session import close_session, inject_session
from database.models.base import Base
from settings import settings


def create_app() -> Sanic:
    app = Sanic("App")

    @app.listener("before_server_start")
    async def init_sentry(_):
        sentry_sdk.init(
            dsn=settings.sentry_dns.get_secret_value(),
            integrations=[AsyncioIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False,
            debug=settings.debug,
        )

    Extend(app, config=Config(oas=True, cors=True))

    app.register_middleware(inject_session, "request")
    app.register_middleware(jwt_authentication, "request")
    app.register_middleware(close_session, "response")

    app.ext.openapi.add_security_scheme(
        "token",
        "http",
        scheme="bearer",
        bearer_format="JWT",
    )

    app.blueprint(api)

    @app.listener("after_server_start")
    async def print_routes(app, _):
        for route in app.router.routes:
            print(f"Path: {route.path}, Methods: {route.methods}")

    from app.error_handling import global_error_handler

    app.error_handler.add(Exception, global_error_handler)
    print(f"Final DB URL: {settings.db_url}")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=settings.debug, auto_reload=settings.debug)
