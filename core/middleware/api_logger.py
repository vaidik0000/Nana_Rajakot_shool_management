import time
import uuid
from django.utils.deprecation import MiddlewareMixin

class APILoggerMiddleware(MiddlewareMixin):
    """
    Simple middleware that only tracks request timing for performance metrics.
    No logging functionality is implemented.
    """
    def process_request(self, request):
        # Set a unique ID for the request and record start time
        request.api_id = str(uuid.uuid4())
        request.start_time = time.time()

    def process_response(self, request, response):
        # Calculate request duration if start_time exists
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            # Store duration in response headers for debugging if needed
            response['X-Request-Duration'] = f"{duration:.3f}s"
        
        return response
