"""初始化聊天模块菜单和权限。

用法：
    python manage.py init_chat
"""

from django.core.management.base import BaseCommand
from apps.rbac.models import Menu, Permission, Role


class Command(BaseCommand):
    help = '初始化聊天模块菜单和权限'

    def handle(self, *args, **options):
        # 获取或创建系统管理菜单（作为聊天菜单的父菜单）
        try:
            system_menu = Menu.objects.get(path='system')
        except Menu.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ✗ 未找到系统管理菜单，请先运行 python manage.py init_rbac'))
            return

        # 创建聊天菜单
        chat_menu, created = Menu.objects.get_or_create(
            path='chat',
            defaults={
                'title': '员工聊天',
                'component': 'chat/index',
                'icon': 'icon-message',
                'parent': system_menu,
                'order': 9,
                'is_hidden': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 创建菜单: {chat_menu.title}'))
        else:
            self.stdout.write(f'  - 菜单已存在: {chat_menu.title}')

        # 创建聊天权限
        base_url = '/api/chat/messages/'
        perms = [
            ('聊天消息列表', 'chat:list', 'GET', base_url),
            ('发送消息', 'chat:create', 'POST', base_url),
            ('查看对话列表', 'chat:conversations', 'GET', f'{base_url}conversations/'),
            ('查看用户消息', 'chat:with_user', 'GET', f'{base_url}with_user/'),
            ('标记已读', 'chat:mark_read', 'POST', f'{base_url}*/mark_read/'),
            ('标记全部已读', 'chat:mark_all_read', 'POST', f'{base_url}mark_all_read/'),
        ]

        created_perms = []
        for name, code, method, url in perms:
            perm, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'http_method': method,
                    'url_pattern': url,
                    'menu': chat_menu,
                    'is_active': True,
                }
            )
            if created:
                created_perms.append(perm)
                self.stdout.write(self.style.SUCCESS(f'  ✓ 创建权限: {name}'))
            else:
                # 更新已存在的权限
                perm.name = name
                perm.http_method = method
                perm.url_pattern = url
                perm.menu = chat_menu
                perm.is_active = True
                perm.save()

        # 将权限授予超级管理员角色
        admin_roles = Role.objects.filter(
            code__in=['ADMIN', 'SUPER_ADMIN']
        ) | Role.objects.filter(
            name__in=['超级管理员', 'SuperAdmin', 'Administrator']
        )
        
        for role in admin_roles:
            role.permissions.add(*created_perms)
            role.menus.add(chat_menu)
            self.stdout.write(self.style.SUCCESS(f'  ✓ 已将权限授予角色: {role.name}'))

        self.stdout.write(self.style.SUCCESS('\n聊天模块初始化完成！'))

