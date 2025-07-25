from database.engine import _base_model_session_ctx, _sessionmaker


async def inject_session(request):
    request.ctx.session = _sessionmaker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()
