from accounts.models import Role, Permission, Resource, RolePermission, ResourcePermission, User, UserRole

def create_initial_data():
    # Создаем роли
    admin_role = Role.objects.create(name='admin', description='Administrator')
    user_role = Role.objects.create(name='user', description='Regular user')
    
    # Создаем разрешения
    user_read = Permission.objects.create(
        name='Read user data',
        code='user_read',
        description='Permission to read user data'
    )
    user_write = Permission.objects.create(
        name='Write user data',
        code='user_write',
        description='Permission to modify user data'
    )
    role_read = Permission.objects.create(
        name='Read role data',
        code='role_read',
        description='Permission to read role data'
    )
    permission_read = Permission.objects.create(
        name='Read permission data',
        code='permission_read',
        description='Permission to read permission data'
    )
    resource_read = Permission.objects.create(
        name='Read resource data',
        code='resource_read',
        description='Permission to read resource data'
    )
    business_data_read = Permission.objects.create(
        name='Read business data',
        code='business_data_read',
        description='Permission to read business data'
    )
    
    # Создаем ресурсы
    user_resource = Resource.objects.create(
        name='User',
        code='user',
        description='User resource'
    )
    role_resource = Resource.objects.create(
        name='Role',
        code='role',
        description='Role resource'
    )
    permission_resource = Resource.objects.create(
        name='Permission',
        code='permission',
        description='Permission resource'
    )
    resource_resource = Resource.objects.create(
        name='Resource',
        code='resource',
        description='Resource resource'
    )
    business_resource = Resource.objects.create(
        name='Business Data',
        code='business_data',
        description='Business data resource'
    )
    
    # Связываем разрешения с ресурсами и действиями
    ResourcePermission.objects.create(
        resource=user_resource,
        permission=user_read,
        action='read'
    )
    ResourcePermission.objects.create(
        resource=user_resource,
        permission=user_write,
        action='write'
    )
    ResourcePermission.objects.create(
        resource=role_resource,
        permission=role_read,
        action='read'
    )
    ResourcePermission.objects.create(
        resource=permission_resource,
        permission=permission_read,
        action='read'
    )
    ResourcePermission.objects.create(
        resource=resource_resource,
        permission=resource_read,
        action='read'
    )
    ResourcePermission.objects.create(
        resource=business_resource,
        permission=business_data_read,
        action='read'
    )
    
    # Назначаем разрешения ролям
    RolePermission.objects.create(role=admin_role, permission=user_read)
    RolePermission.objects.create(role=admin_role, permission=user_write)
    RolePermission.objects.create(role=admin_role, permission=role_read)
    RolePermission.objects.create(role=admin_role, permission=permission_read)
    RolePermission.objects.create(role=admin_role, permission=resource_read)
    RolePermission.objects.create(role=admin_role, permission=business_data_read)
    
    RolePermission.objects.create(role=user_role, permission=user_read)
    RolePermission.objects.create(role=user_role, permission=business_data_read)
    
    # Создаем тестовых пользователей
    admin = User.objects.create(
        first_name='Admin',
        last_name='User',
        email='admin@example.com',
        is_active=True
    )
    admin.set_password('admin123')
    admin.save()
    
    regular_user = User.objects.create(
        first_name='Regular',
        last_name='User',
        email='user@example.com',
        is_active=True
    )
    regular_user.set_password('user123')
    regular_user.save()
    
    # Назначаем роли пользователям
    UserRole.objects.create(user=admin, role=admin_role)
    UserRole.objects.create(user=regular_user, role=user_role)