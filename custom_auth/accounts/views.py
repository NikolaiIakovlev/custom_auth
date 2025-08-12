from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User, Role, Permission, Resource, UserRole, RolePermission, ResourcePermission
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    RoleSerializer, PermissionSerializer, ResourceSerializer
)
import secrets
from django.core.exceptions import ObjectDoesNotExist

class AuthMixin:
    @staticmethod
    def generate_token():
        return secrets.token_hex(32)
    
    @staticmethod
    def get_user_from_token(request):
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
        if not token:
            return None
        try:
            user = User.objects.get(token=token, is_active=True)
            return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView, AuthMixin):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = self.generate_token()
        user.token = token
        user.save()
        
        response = Response(UserSerializer(user).data)
        response.set_cookie('auth_token', token, httponly=True)
        return response

class LogoutView(APIView, AuthMixin):
    def post(self, request):
        user = self.get_user_from_token(request)
        if user:
            user.token = None
            user.save()
        return Response({'message': 'Logged out successfully'})

class UserProfileView(APIView, AuthMixin):
    def get(self, request):
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserSerializer(user).data)
    
    def put(self, request):
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView, AuthMixin):
    def post(self, request):
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user.is_active = False
        user.token = None
        user.save()
        return Response({'message': 'Account deactivated successfully'})

class RoleListView(APIView, AuthMixin):
    def get(self, request):
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Проверка прав доступа
        if not self.check_permission(user, 'role', 'read'):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

class PermissionListView(APIView, AuthMixin):
    def get(self, request):
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Проверка прав доступа
        if not self.check_permission(user, 'permission', 'read'):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

class ResourceListView(APIView, AuthMixin):
    def get(self, request):
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Проверка прав доступа
        if not self.check_permission(user, 'resource', 'read'):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)

class MockBusinessView(APIView, AuthMixin):
    def get(self, request):
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Проверка прав доступа
        if not self.check_permission(user, 'business_data', 'read'):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        # Моковые бизнес-данные
        mock_data = [
            {'id': 1, 'name': 'Business Object 1', 'value': 100},
            {'id': 2, 'name': 'Business Object 2', 'value': 200},
        ]
        return Response(mock_data)

    def check_permission(self, user, resource_code, action):
        # Получаем все роли пользователя
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        role_ids = [ur.role.id for ur in user_roles]
        
        # Получаем ресурс
        try:
            resource = Resource.objects.get(code=resource_code)
        except Resource.DoesNotExist:
            return False
        
        # Получаем нужное разрешение для ресурса и действия
        try:
            resource_permission = ResourcePermission.objects.get(
                resource=resource,
                action=action
            )
        except ResourcePermission.DoesNotExist:
            return False
        
        # Проверяем, есть ли у ролей пользователя нужное разрешение
        return RolePermission.objects.filter(
            role_id__in=role_ids,
            permission=resource_permission.permission
        ).exists()