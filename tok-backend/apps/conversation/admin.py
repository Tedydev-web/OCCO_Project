from django.contrib import admin
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import format_html

from apps.conversation.models import Room, RoomUser, Message
from django_admin_inline_paginator.admin import TabularInlinePaginated

from apps.general.admin import CustomModelAdmin
from apps.general.models import FileUpload


# Register your models here.
class RoomUserInline(TabularInlinePaginated):
    model = RoomUser
    extra = 1
    per_page = 10
    readonly_fields = ('role', 'user')
    exclude = ('date_removed', 'last_message', 'total_unseen')


class MessageInline(TabularInlinePaginated):
    model = Message
    extra = 1
    max_num = 10

    fields = ('sender', 'type', 'text', 'created_at')
    readonly_fields = ('created_at', 'sender', 'type', 'text')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(type='TEXT').select_related('sender')

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else "N/A"

    get_sender_name.short_description = 'Người gửi'
    get_sender_name.admin_order_field = 'sender__last_name'

    # Thêm phân trang
    per_page = 15
    pagination_key = 'page-model'
    ordering = ('-created_at',)


def room_messages(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    messages = room.message_set.all().prefetch_related('file', 'sender').order_by(
        '-created_at')  # Hoặc cách khác tùy thuộc vào mô hình của bạn
    return render(request, 'room_message.html', {'room': room, 'messages': messages})


@admin.register(Room)
class RoomChatAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('type', 'name', 'get_member_names', 'newest_at', 'total_message', 'view_messages_link')
    search_fields = ['name', 'id', 'roomuser__user__full_name', 'roomuser__user__phone_number']
    inlines = [RoomUserInline]
    list_per_page = 15
    date_hierarchy = 'newest_at'
    list_filter = ('newest_at',)
    ordering = ('-newest_at',)
    exclude = ('is_used', 'newest_at', 'is_accepted', 'is_leaved')
    readonly_fields = ('get_member_names',)

    def get_member_names(self, obj):
        return ", ".join([
            user.user.full_name if hasattr(user.user, 'full_name') and user.user.full_name else (
                user.user.google_auth if hasattr(user.user, 'google_auth') and user.user.google_auth else ''
            ) for user in obj.roomuser_set.all().select_related('user')
        ])

    get_member_names.short_description = 'Thành viên'

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(type='PRIVATE').exclude(newest_at=None).prefetch_related(
            'roomuser_set')

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def view_messages_link(self, obj):
        url = reverse('room_messages', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Xem tin nhắn</a>', url)

    view_messages_link.short_description = 'Xem tin nhắn'

    def total_message(self, obj):
        return obj.message_set.count()
