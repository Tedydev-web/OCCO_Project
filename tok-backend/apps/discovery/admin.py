from django.contrib import admin
from django.utils.safestring import mark_safe
from django_admin_inline_paginator.admin import TabularInlinePaginated
from modeltranslation.admin import TranslationAdmin
from modeltranslation.translator import TranslationOptions, translator

from apps.discovery.models import *
from apps.general.admin import CustomGroupAdmin, CustomModelAdmin
from apps.general.models import DefaultAvatar


class LiveUserIncline(TabularInlinePaginated):
    model = LiveUser
    extra = 1
    max_num = 10
    fields = ('user', 'role')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LiveStreamBaseAdmin(CustomGroupAdmin, admin.ModelAdmin):
    list_display = ('id_show', 'name', 'user_view', 'created_at')
    ordering = ('side', '-created_at',)
    search_fields = ('id_show', 'name', 'side')
    list_per_page = 20
    readonly_fields = ('display_avatar_image', 'display_avatar_link', 'name')
    fieldsets = (
        ('Thông tin', {
            'fields': (
                'id_show', 'display_avatar_image', 'display_avatar_link', 'name'),
        }),
    )
    raw_id_fields = ('cover_image',)
    inlines = [
        LiveUserIncline
    ]
    required_group_ids = [2, 5]

    def render_change_form(
            self, request, context, add=False, change=True, form_url="", obj=None
    ):
        return super().render_change_form(
            request, context, add, True, form_url, obj
        )

    def has_add_permission(self, request):
        return False

    def display_avatar_link(self, obj):
        if obj.cover_image:
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(obj.cover_image.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(default_avatar_url))

    def display_avatar_image(self, obj):
        if obj.cover_image:
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(obj.cover_image.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(default_avatar_url))

    display_avatar_link.short_description = "Url"
    display_avatar_image.short_description = "Ảnh"

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and "country" not in self.list_filter:
            self.list_filter += ("host__country",)
        else:
            self.list_filter = ()
        return super().changelist_view(request, extra_context)




@admin.register(LiveChatProxy)
class LiveChatAdmin(LiveStreamBaseAdmin):
    list_display = ('id_show', 'name', 'side', 'user_view')
    list_filter = ('side',)
    ordering = ('-user_view',)

    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).select_related('cover_image').defer('view').filter(type='CHAT')
        else:
            return super().get_queryset(request).filter(host__country=request.user.country).select_related('cover_image').defer('view').filter(type='CHAT')

@admin.register(LiveAudioProxy)
class LiveAudioAdmin(LiveStreamBaseAdmin):
    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).select_related('cover_image').defer('view').filter(type='AUDIO')
        else:
            return super().get_queryset(request).filter(host__country=request.user.country).select_related('cover_image').defer('view').filter(type='AUDIO')


    def has_delete_permission(self, request, obj=None):
        return True




@admin.register(LiveVideoProxy)
class LiveVideoAdmin(LiveStreamBaseAdmin):
    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).select_related('cover_image').defer('view').filter(type='VIDEO')
        else:
            return super().get_queryset(request).filter(host__country=request.user.country).select_related('cover_image').defer('view').filter(type='VIDEO')



@admin.register(LiveStreamProxy)
class LiveStreamAdmin(LiveStreamBaseAdmin):
    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).select_related('cover_image').defer('view').filter(type='STREAM')
        else:
            return super().get_queryset(request).filter(host__country=request.user.country).select_related('cover_image').defer('view').filter(type='STREAM')



class GiftTranslationOptions(TranslationOptions):
    fields = ('title',)


translator.register(Gift, GiftTranslationOptions)


@admin.register(Gift)
class GiftAdmin(CustomModelAdmin, TranslationAdmin):
    list_display = ('display_image', 'title', 'price')
    list_per_page = 10
    fieldsets = (
        ('Thông tin', {
            'fields': (
                'title', 'price', 'display_image', 'image'),
        }),
    )

    ordering = ('price',)
    readonly_fields = ('display_image',)
    required_group_ids = [2, 5]

    def display_image(self, obj):
        if obj.image:
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(obj.image.url))

    display_image.short_description = 'Ảnh'
