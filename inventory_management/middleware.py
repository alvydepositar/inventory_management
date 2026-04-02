from django.shortcuts import redirect
from django.http import JsonResponse

EXEMPT_PATHS = [
    '/',
    '/logout/',
    '/admin/login/',
]

def _is_exempt(path: str) -> bool:
    if path.startswith('/static/'):
        return True
    return path in EXEMPT_PATHS

def _is_api_request(request) -> bool:
    # Treat XHR, JSON-accepting, or any *data* endpoint as API
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return True
    accept = request.headers.get('accept', '')
    if 'application/json' in accept:
        return True
    path = request.path or ''
    if 'data' in path:
        return True
    return False

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not _is_exempt(request.path):
            # Return JSON 401 for API-like endpoints to avoid DataTables parsing HTML
            if _is_api_request(request):
                return JsonResponse({'detail': 'Authentication required'}, status=401)
            return redirect('/')
        return self.get_response(request)
