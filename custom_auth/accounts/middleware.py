# from django.http import JsonResponse
# from .models import User, Session


# class AuthenticationMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
    
#     def __call__(self, request):
#         # Пропускаем запросы к админке
#         if request.path.startswith('/admin/'):
#             return self.get_response(request)
#         # Проверяем аутентификацию по токену
#         auth_header = request.META.get('HTTP_AUTHORIZATION', '')
#         if auth_header.startswith('Bearer '):
#             token = auth_header.split(' ')[1]
#             user = User.verify_token(token)
#             if user:
#                 request.user = user
#                 return self.get_response(request)
        
#         # Проверяем аутентификацию по сессии (куки)
#         session_id = request.COOKIES.get('sessionid')
#         if session_id:
#             try:
#                 session = Session.objects.get(session_id=session_id)
#                 if session.is_valid():
#                     request.user = session.user
#                     return self.get_response(request)
#             except Session.DoesNotExist:
#                 pass
        
#         # Если аутентификация не удалась
#         request.user = None
#         return self.get_response(request)