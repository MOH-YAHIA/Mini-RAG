from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Response, FastAPI
request_counter_metric = Counter("request_counter", "Total number of requests", ["endpoint", "method", "status_code"])
request_duration_metric = Histogram("request_duration_seconds", "Request duration in seconds", ["endpoint", "method"])

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        """
        Collect request count and request duration metrics.
        """
        endpoint = request.url.path
        method = request.method

        # Measure the complete request duration.
        with request_duration_metric.labels(
            endpoint=endpoint,
            method=method,
        ).time():
            response = await call_next(request)

        # Count the request after we know its status code.
        status_code = str(response.status_code)

        request_counter_metric.labels(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
        ).inc()

        return response

def setup_metrics(app: FastAPI):
    """
    expose the metrics we collected by the middeleware in format that prometheus can understand.
    prometheus will scrape the metrics from this endpoint.
    """
    app.add_middleware(MetricsMiddleware)

    @app.get("/adfljiad_Adkeci", include_in_schema=False) # give a random endpoint name so that it is not easily guessable
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)