from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from modeltranslation.admin import TranslationAdmin
from modeltranslation.translator import TranslationOptions, translator

from api.services.firebase import send_and_save_notification, send_and_save_admin_notification
from apps.notification.models import UserDevice, Notification
from apps.user.models import CustomUser


# Register your models here.
@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'name', 'model', 'created_at')
    search_fields = ('user__full_name', 'name', 'model')
    list_filter = ('created_at', 'user')
    list_per_page = 10
    ordering = ('-created_at',)

class NotificationTranslationOptions(TranslationOptions):
    fields = ('title', 'body')


translator.register(Notification, NotificationTranslationOptions)


class SendNotificationForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all(), required=False,
                                           widget=admin.widgets.FilteredSelectMultiple("Users", is_stacked=False))
    exclude = ('title_en', 'body_en')

    class Meta:
        model = Notification
        fields = ['title_vi', 'body_vi', 'users']

    def clean_users(self):
        users = self.cleaned_data.get('users')
        if users and users.filter(email__in=['all']).exists():
            return CustomUser.objects.all()
        return users


@admin.register(Notification)
class SendNotificationAdmin(TranslationAdmin):
    form = SendNotificationForm
    list_display = ('nid', 'user', 'title_vi', 'body_vi', 'is_read', 'created_at')
    search_fields = ('user__phone_number', 'title', 'body')
    list_filter = ('created_at', 'is_read', 'user')
    readonly_fields = ('nid',)
    list_per_page = 10
    ordering = ('-created_at',)
    raw_id_fields = ('user',)  # Sử dụng raw_id_fields cho trường users

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Gửi và lưu thông báo khi người dùng lưu form

        title_vi = form.cleaned_data['title_vi']
        body_vi = form.cleaned_data['body_vi']
        try:
            # Backup noti English
            title_en = form.cleaned_data['title_en']
            body_en = form.cleaned_data['body_en']
        except Exception as e:
            title_en = ''
            body_en = ''
        direct_type = "Test"  # Giá trị mặc định, bạn có thể điều chỉnh tùy theo nhu cầu
        direct_value = "Test"  # Giá trị mặc định, bạn có thể điều chỉnh tùy theo nhu cầu
        direct_user = None  # Giá trị mặc định, bạn có thể điều chỉnh tùy theo nhu cầu
        users = form.cleaned_data['users']
        for user in users:
            notification = send_and_save_admin_notification(user,
                                                            [title_vi, title_en],
                                                            [body_vi, body_en],
                                                            direct_type,
                                                            direct_value,
                                                            request=request,
                                                            custom_data=None,
                                                            direct_user=None,
                                                            app_name='TOK')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type='SYSTEM').select_related('user','direct_user')