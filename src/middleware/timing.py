import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware

from rich.console import Console
c = Console()
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logging.debug(f'post_response: {1000 * process_time:0.4f}ms')  # {request.client.host} to endpoint {request.url}
        return response