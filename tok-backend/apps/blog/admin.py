from django.contrib import admin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import format_html

from apps.blog.models import *
from apps.dashboard.dashboard import admin_site
from apps.general.admin import CustomGroupAdmin, CustomModelAdmin
from apps.general.models import FileUpload


def comments_list_view(request, blog_id):
    page_number = int(request.GET.get('page', 1))
    per_page = 10  # Number of comments per page

    blog = Blog.objects.get(pk=blog_id)
    comments = Comment.objects.filter(blog=blog, is_active=True).order_by('created_at')

    paginator = Paginator(comments, per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'comment_list.html', {
        'comments': page_obj,
        'paginator': paginator,
        'page_obj': page_obj,
    })


class FileInline(admin.TabularInline):
    model = Blog.file.through
    extra = 0
    fields = ('file_preview',)
    readonly_fields = ('file_preview',)

    def file_preview(self, obj):
        if obj.file_type == 'IMAGE' and obj.file:
            return format_html('<img src="{}" width="200" height="200" />', obj.file.url)
        elif obj.file_type == 'VIDEO' and obj.file:
            return format_html('<video width="200" controls><source src="{}" type="video/mp4"></video>', obj.file.url)
        return ""

    file_preview.short_description = 'File'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Inline admin for LikeComment within CommentInline
class LikeCommentInline(admin.TabularInline):
    model = LikeComment
    extra = 0
    readonly_fields = ('type', 'user', 'created_at')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False


# Inline admin for ReplyComment within CommentInline
class ReplyCommentInline(admin.TabularInline):
    model = ReplyComment
    extra = 0
    fields = ('created_at', 'content', 'user', 'is_active')
    readonly_fields = ('content', 'user', 'created_at', 'count_like')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False

    inlines = [LikeCommentInline]  # Add LikeCommentInline under ReplyCommentInline


# Inline admin for Comment
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('created_at', 'content', 'user', 'is_active')
    readonly_fields = ('content', 'user', 'created_at', 'count_like')
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    inlines = [ReplyCommentInline]  # Add ReplyCommentInline and LikeCommentInline under CommentInline


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('bid', 'user', 'created_at', 'is_active')
    list_filter = ('is_active','created_at')
    exclude = ['user_like', 'updated_at', 'id']
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    search_fields = ('id', 'user__full_name', 'user__phone_number')
    readonly_fields = ('bid', 'user', 'content', 'count_comment', 'count_like', 'count_share', 'display_files')
    fieldsets = (
        ('Thông tin', {
            'fields': (
                'user', 'content', 'is_active'),
        }),
        ('Tương tác', {
            'fields': (
                'count_comment', 'count_like', 'count_share'
            )
        }),
        ('Files', {
            'fields': (
                'display_files',
            )
        }),
    )
    list_per_page = 15
    inlines = [CommentInline]  # Add CommentInline under BlogAdmin

    def has_add_permission(self, request):
        return False

    def display_files(self, obj):
        files = obj.file.all()
        html = ''
        is_audio = False
        for file in files:
            if file.file_type == 'IMAGE':
                is_audio = True
                html += format_html('<img src="{}" width="200" height="200" style="margin: 5px;" />', file.file.url)
            elif file.file_type == 'VIDEO':
                html += format_html(
                    '<video width="200" controls style="margin: 5px;"><source src="{}" type="video/mp4"></video>',
                    file.file.url)
        if is_audio:
            html += format_html(
                '<audio width="200" controls style="margin: 5px;"><source src="{}" type="audio/mp3"></audio>',
                obj.audio.file.url)
        return format_html(html)

    display_files.short_description = 'Files'

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and "country" not in self.list_filter:
            self.list_filter += ("user__country",)
        else:
            self.list_filter = ()
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request)
        else:
            return super().get_queryset(request).filter(user__country=request.user.country)


# Register other related models in admin if needed
@admin.register(LikeBlog)
class LikeBlogAdmin(admin.ModelAdmin):
    list_display = ('type', 'blog', 'user', 'created_at')
    list_filter = ('type',)
    search_fields = ('blog__title', 'user__full_name', 'user__phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('type', 'blog', 'user', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'blog', 'user', 'created_at', 'count_like')
    list_filter = ('is_active',)
    search_fields = ('blog__title', 'user__full_name', 'user__phone_number')
    ordering = ('-created_at',)
    fields = ('is_active', 'content', 'blog', 'user', 'created_at', 'count_like')
    readonly_fields = ('content', 'blog', 'user', 'created_at', 'count_like')

    def has_add_permission(self, request):
        return False


@admin.register(LikeComment)
class LikeCommentAdmin(admin.ModelAdmin):
    list_display = ('type', 'comment', 'user', 'created_at')
    list_filter = ('type',)
    search_fields = ('comment__content', 'user__full_name', 'user__phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('type', 'comment', 'user', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(ReplyComment)
class ReplyCommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'comment', 'user', 'created_at', 'count_like')
    list_filter = ('is_active',)
    search_fields = ('comment__content', 'user__full_name', 'user__phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('content', 'comment', 'user', 'created_at', 'count_like')

    def has_add_permission(self, request):
        return False


@admin.register(LikeReplyComment)
class LikeReplyCommentAdmin(admin.ModelAdmin):
    list_display = ('type', 'reply_comment', 'user', 'created_at')
    list_filter = ('type',)
    search_fields = ('reply_comment__content', 'user__full_name', 'user__phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('type', 'reply_comment', 'user', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(AudioUpload)
class AudioUploadAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('index', 'title', 'display_files')
    ordering = ('index',)
    list_per_page = 10
    exclude = ('description',)
    readonly_fields = ('display_files',)
    fieldsets = (
        ('Chi tiết', {
            'fields': (
                'index', 'title', 'display_files', 'file'),
        }),
    )
    required_group_ids = [2, 3]

    def display_files(self, obj):
        file = obj.file
        html = ''
        html += format_html(
            '<audio width="200" controls style="margin: 5px;"><source src="{}" type="audio/mp3"></audio>',
            file.url)
        return format_html(html)

    display_files.short_description = 'File'
