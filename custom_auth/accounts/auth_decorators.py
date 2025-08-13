from functools import wraps
from django.http import JsonResponse
from .models import UserSession
from django.utils import timezone

def require_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Session '):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        session_key = auth_header.split(' ')[1]
        try:
            session = UserSession.objects.get(session_key=session_key)
            if not session.is_active():
                return JsonResponse({'error': 'Session expired'}, status=401)
        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session'}, status=401)

        request.user = session.user
        request.session_obj = session  # если пригодится
        return view_func(request, *args, **kwargs)

    return wrapper
