from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import User, Role, UserSession
from .utils import generate_session_key, get_expiration_time
from django.utils import timezone
from accounts.auth_decorators import require_auth

@csrf_exempt
def register_user(request):
    if request.method == 'GET':
        return render(request, 'accounts/register.html')

    if request.method != 'POST' and request.method != 'GET':
        return JsonResponse({'error': 'Only GET and POST methods are allowed'}, status=405)

    try:
        # POST через форму или JSON
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST

        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name', '')
        role_id = data.get('role_id')

        if not all([email, password, first_name]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)

        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                user.role = role
            except Role.DoesNotExist:
                return JsonResponse({'error': 'Invalid role ID'}, status=400)

        user.save()

        return JsonResponse({'message': 'User registered successfully'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def login_user(request):
    if request.method == 'GET':
        return render(request, 'accounts/login.html')

    if request.method != 'POST' and request.method != 'GET':
        return JsonResponse({'error': 'Only GET and POST methods are allowed'}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST

        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return JsonResponse({'error': 'Missing email or password'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        if not user.check_password(password):
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        if not user.is_active:
            return JsonResponse({'error': 'User is inactive'}, status=403)

        user.last_login = timezone.now()
        user.save()

        session_key = generate_session_key()
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        session = UserSession.objects.create(
            user=user,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=get_expiration_time()
        )

        return JsonResponse({
            'message': 'Login successful',
            'session_key': session.session_key,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role.name if user.role else None
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_auth
def logout_user(request):
    if request.method == 'GET':
        return render(request, 'accounts/logout.html')
    session = request.session_obj
    session.expires_at = timezone.now()  # делаем сессию неактивной
    session.save()
    return JsonResponse({'message': 'Logged out successfully'})


@csrf_exempt
@require_auth
def update_profile(request):
    if request.method == 'GET':
        return render(request, 'accounts/update_profile.html')
    if request.method != 'POST' and request.method != 'GET':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    data = request.POST if request.content_type != 'application/json' else json.loads(request.body.decode('utf-8'))

    user = request.user
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)

    if data.get('password'):
        if data.get('password') != data.get('password_repeat'):
            return JsonResponse({'error': 'Passwords do not match'}, status=400)
        user.set_password(data['password'])

    user.save()
    return JsonResponse({'message': 'Profile updated successfully'})


@csrf_exempt
@require_auth
def delete_account(request):
    if request.method == 'GET':
        return render(request, 'accounts/delete_account.html')
    if request.method != 'POST' and request.method != 'GET':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    user = request.user
    user.is_active = False
    user.save()

    # Завершаем сессию
    request.session_obj.expires_at = timezone.now()
    request.session_obj.save()

    return JsonResponse({'message': 'Account deactivated and logged out'})
