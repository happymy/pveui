"""客服系统模型。"""

import uuid
from django.conf import settings
from django.db import models
from apps.common.models import BaseAuditModel


class GuestSession(BaseAuditModel):
    """访客会话：用于访客与客服之间的会话上下文。"""

    STATUS_CHOICES = [
        ('pending', '待接入'),
        ('active', '会话中'),
        ('closed', '已关闭'),
    ]

    session_id = models.CharField(max_length=64, unique=True, default='', verbose_name='会话ID')
    secret_token = models.CharField(max_length=64, verbose_name='访客令牌')
    app_id = models.CharField(max_length=64, verbose_name='应用ID')
    visitor_id = models.CharField(max_length=128, blank=True, default='', verbose_name='访客ID')
    nickname = models.CharField(max_length=64, blank=True, default='访客', verbose_name='访客昵称')
    contact = models.CharField(max_length=128, blank=True, default='', verbose_name='联系方式')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    source_url = models.URLField(blank=True, default='', verbose_name='来源页面')
    user_agent = models.CharField(max_length=255, blank=True, default='', verbose_name='UserAgent')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_service_sessions',
        verbose_name='当前客服',
    )
    last_message = models.TextField(blank=True, default='', verbose_name='最后消息')
    last_message_at = models.DateTimeField(null=True, blank=True, verbose_name='最后消息时间')
    metadata = models.JSONField(blank=True, default=dict, verbose_name='附加信息')

    class Meta:
        verbose_name = '访客会话'
        verbose_name_plural = '访客会话'
        ordering = ['-last_message_at', '-updated_at']
        indexes = [
            models.Index(fields=['app_id']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]

    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = uuid.uuid4().hex
        if not self.secret_token:
            self.secret_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.nickname}({self.session_id})"


class GuestMessage(BaseAuditModel):
    """访客消息。"""

    SENDER_CHOICES = [
        ('guest', '访客'),
        ('agent', '客服'),
        ('system', '系统'),
    ]

    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
        ('event', '事件'),
    ]

    session = models.ForeignKey(
        GuestSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='会话',
    )
    sender_type = models.CharField(max_length=16, choices=SENDER_CHOICES, default='guest', verbose_name='消息来源')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_service_messages',
        verbose_name='客服用户',
    )
    content = models.TextField(verbose_name='内容')
    message_type = models.CharField(max_length=16, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    metadata = models.JSONField(blank=True, default=dict, verbose_name='附加信息')
    is_read = models.BooleanField(default=False, verbose_name='已读')

    class Meta:
        verbose_name = '访客消息'
        verbose_name_plural = '访客消息'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['sender_type']),
        ]

    def __str__(self) -> str:
        return f"{self.session.session_id} - {self.sender_type}"


