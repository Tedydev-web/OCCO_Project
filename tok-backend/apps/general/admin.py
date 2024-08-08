import json

from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.general.models import *
from django import forms

from apps.user.models import CustomUser

admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')

    def has_add_permission(self, request):
        if request.user.phone_number == '+84987654321' or request.user.phone_number == '+84398765432':
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.phone_number == '+84987654321' or request.user.phone_number == '+84398765432':
            return True
        return False

    def has_view_or_change_permission(self, request, obj=None):
        if request.user.phone_number == '+84987654321' or request.user.phone_number == '+84398765432':
            return True
        return False


class CustomModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        try:
            return request.user.country == 'All' and request.user.is_superuser
        except:
            return False

    def has_view_permission(self, request, obj=None):
        try:
            return request.user.country == 'All' and request.user.is_superuser
        except:
            return False


class DevSettingForm(CustomModelAdmin, forms.ModelForm):
    key = forms.CharField(required=False)
    value = forms.CharField(required=False)
    delete_key = forms.BooleanField(required=False)
    required_group_ids = [2]

    class Meta:
        model = DevSetting
        fields = ['key', 'value', 'delete_key']

    def __init__(self, *args, **kwargs):
        super(DevSettingForm, self).__init__(*args, **kwargs)
        if self.instance.config:
            for key, value in self.instance.config.items():
                self.fields[key] = forms.CharField(initial=value, required=False)

    def save(self, commit=True):
        instance = super(DevSettingForm, self).save(commit=False)
        config = instance.config or {}
        if self.cleaned_data['delete_key'] and self.cleaned_data['key'] in config:
            del config[self.cleaned_data['key']]
        else:
            if self.cleaned_data['key']:
                config[self.cleaned_data['key']] = self.cleaned_data['value']
        instance.config = config
        if commit:
            instance.save()
        return instance


@admin.register(DevSetting)
class DevSettingAdmin(admin.ModelAdmin):
    # form = DevSettingForm
    list_display = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Configuration', {
            'fields': ('config_display', 'config'),
        }),
    )

    readonly_fields = ('config_display',)

    def config_display(self, obj):
        if obj.config:
            return json.dumps(obj.config, indent=4)
        return ''

    config_display.short_description = 'Configuration'


@admin.register(AppConfig)
class AdminAppConfig(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('key', 'value')
    readonly_fields = ('key', 'note')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(key__in=['MAXIMUM_CHAT_ROOM', 'AGE_RANGE_RECOMMENDED'])


@admin.register(DefaultAvatar)
class DefaultAvatarAdmin(admin.ModelAdmin):
    list_display = ('key', 'image_display', 'created_at')
    required_group_ids = [2]

    def image_display(self, obj):
        if obj.image:
            return obj.image.url
        return ''


class FileUploadIncline(admin.TabularInline):
    model = FileUpload

    readonly_fields = ('display_avatar_image',)

    def display_avatar_image(self, obj):
        if obj.file:
            return mark_safe('<img src="{0}" width="300" height="300" />'.format(obj.file.url))

    display_avatar_image.short_description = 'Ảnh báo cáo'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('type', 'is_verified', 'user', 'direct_user', 'content', 'created_at')
    list_filter = ['type', 'is_verified']
    search_fields = ('user__full_name', 'direct_user__full_name',
                     'user__uid', 'direct_user__uid')
    readonly_fields = ('display_images', 'user','id', 'direct_user', 'type', 'content')
    fieldsets = (
        ('Chi tiết', {
            'fields': ('is_verified', 'type','id', 'user', 'direct_user', 'content'),
        }),
        ('Ảnh báo cáo', {
            'fields': ('display_images',),
        }),
    )
    ordering = ('-created_at',)
    list_per_page = 15
    required_group_ids = [2, 6]

    def display_images(self, obj):
        images_html = ""
        for image in obj.image.all():
            images_html += (f'<img src="{image.file.url}" style="max-width: 500px; max-height: 500px;margin-right: '
                            f'10px;">')
        return mark_safe(images_html)

    display_images.short_description = 'Ảnh báo cáo'

    def save_model(self, request, obj, form, change):
        obj.verifier = request.user  # Nếu đúng, gán người chỉnh sửa là verifier
        obj.save()

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and "direct_user__country" not in self.list_filter:
            self.list_filter += ["direct_user__country", ]


        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).select_related('direct_user', 'user')
        else:
            return super().get_queryset(request).filter(
                direct_user__country=request.user.country).select_related('direct_user', 'user')


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'file_name', 'created_at')
    ordering = ('-created_at',)
    list_filter = ('owner',)
    list_per_page = 15

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FeedBack)
class FeedBackSerializer(admin.ModelAdmin):
    list_display = ('fid', 'full_name', 'phone_number', 'description', 'is_resolve', 'created_at')
    list_filter = ('is_resolve',)
    search_fields = ('full_name', 'phone_number',)
    exclude = ('updated_at',)
    ordering = ('-created_at',)
    list_per_page = 15
    readonly_fields = ('fid', 'sender', 'phone_number', 'description', 'full_name')
    list_editable = ('is_resolve',)
    required_group_ids = [2, 6]

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and "sender__country" not in self.list_filter:
            self.list_filter += ("sender__country",)
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).select_related('sender')
        else:
            return super().get_queryset(request).filter(
                sender__country=request.user.country).select_related('sender')


class AdminProxy(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Admin'
        verbose_name_plural = 'Admin'


class AdminProxyForm(forms.ModelForm):
    class Meta:
        model = AdminProxy
        fields = ['phone_number', 'country', 'password', 'email', 'full_name']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(AdminProxyForm, self).__init__(*args, **kwargs)
        if request and request.user.country != 'All':
            # Limit the country field choices to the user's country
            self.fields['country'].choices = [
                (request.user.country, request.user.country)
            ]


@admin.register(AdminProxy)
class AdminProxyAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'country', 'created_at')
    list_filter = ()
    ordering = ('-created_at',)
    list_per_page = 15
    fields = ('phone_number', 'country', 'password', 'email', 'full_name')
    required_group_ids = [2]
    form = AdminProxyForm

    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).filter(is_superuser=True)
        return super().get_queryset(request).filter(is_superuser=True, country=request.user.country)

    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminProxyAdmin, self).get_form(request, obj, **kwargs)
        if request.user.country != 'All':
            form.base_fields['country'].choices = [
                (request.user.country, request.user.country)
            ]
        return form

    def save_model(self, request, obj, form, change):
        obj.is_superuser = True
        obj.is_staff = True
        obj.set_password(form.cleaned_data['password'])
        obj.save()

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All':
            self.list_filter = ("country",)
        else:
            self.list_filter = ()
        return super().changelist_view(request, extra_context)


# color input field
class BackGroundColorForm(ModelForm):
    class Meta:
        model = BackGroundColor
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }


@admin.register(BackGroundColor)
class BackGroundColorAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('display_color', 'title', 'is_active')
    form = BackGroundColorForm
    fieldsets = (
        (None, {
            'fields': ('color', 'title', 'is_active')
        }),
    )

    def display_color(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 50px; height: 25px;"></div>',
            obj.color,
        )

    display_color.short_description = 'Màu'


@admin.register(CoinTrading)
class CoinTradingAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('coin_price', 'vnd_price')
    list_per_page = 10
    ordering = ('coin_price',)
    exclude = ['title']


@admin.register(MoneyTrading)
class MoneyTradingAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('coin_price', 'vnd_price')
    list_per_page = 10
    ordering = ('coin_price',)
    exclude = ['title']


@admin.register(UIDTrading)
class UIDTradingAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('uid', 'coin_price', 'is_active')
    search_fields = ('uid',)
    list_filter = ('is_active',)
    list_per_page = 20
    ordering = ('-coin_price',)
    readonly_fields = ('is_active',)

    def has_delete_permission(self, request, obj=None):
        return False


class StickerForm(forms.ModelForm):
    class Meta:
        model = Sticker
        fields = ['file', 'is_active']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff')):
                raise ValidationError('Chỉ cho phép upload tệp có đuôi (jpg, jpeg, png, gif, webp, bmp, tiff).')
        return file


@admin.register(StickerCategory)
class StickerAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('image_preview', 'is_active')
    fields = ('image', 'image_preview', 'is_active')
    list_filter = ('is_active',)
    list_per_page = 20
    ordering = ('-created_at',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "-"

    image_preview.short_description = 'Ảnh bộ nhãn dán'


@admin.register(FileUploadAudio)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'owner', 'created_at', 'audio_display')
    ordering = ('-created_at',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    search_fields = ['owner__full_name', 'owner__phone_number']
    list_per_page = 15
    readonly_fields = ['audio_display']
    fieldsets = (
        (None, {
            'fields': ('owner', 'file', 'file_url', 'file_size', 'audio_display')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request).order_by('-upload_finished_at')
        if request.user.country == 'All':
            return queryset.filter(file_type='AUDIO')
        else:
            return queryset.filter(file_type='AUDIO', owner__country=request.user.country)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def audio_display(self, obj):
        return format_html(
            '<audio width="200" controls style="margin: 5px;"><source src="{}" type="audio/mp3"></audio>',
            obj.file_url)

    audio_display.short_description = 'File'

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and 'owner__country' not in self.list_filter:
            self.list_filter += ('owner__country',)
        else:
            self.list_filter = ('created_at',)
        return super().changelist_view(request, extra_context)


class AvatarFrameForm(forms.ModelForm):
    class Meta:
        model = AvatarFrame
        fields = ['frame', 'is_active']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        # if file:
        #     if not file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff')):
        #         raise ValidationError('Chỉ cho phép upload tệp có đuôi (jpg, jpeg, png, gif, webp, bmp, tiff).')
        return file


@admin.register(AvatarFrame)
class AvatarFrameAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('image_preview', 'coin_price', 'is_active')
    fields = ('frame', 'image_preview', 'coin_price', 'is_active')
    list_filter = ('is_active',)
    list_per_page = 20
    ordering = ('-created_at',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        try:
            if obj.frame:
                return mark_safe(f'<img src="{obj.frame.url}" width="50" height="50" />')
        except:
            return "-"

    image_preview.short_description = 'Khung avatar'


@admin.register(AppInformation)
class AppInformationAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('title',)
    fields = ('value',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(SupportAndTraining)
class SupportTrainingAdmin(admin.ModelAdmin):
    list_display = ('index', 'title', 'created_at')
    list_per_page = 15
    ordering = ('-created_at',)
    fields = ('index', 'title', 'description',
              'file')
    def has_delete_permission(self, request, obj=None):
        return request.user.country == 'All'


    def has_add_permission(self, request):
        return request.user.country == 'All'

    def has_change_permission(self, request, obj=None):
        return request.user.country == 'All'


@admin.register(Vip)
class VipFrameAdmin(CustomModelAdmin, admin.ModelAdmin):
    list_display = ('coin_price', 'total_month')
    fields = ('coin_price', 'total_month')
    list_per_page = 20
    ordering = ('-created_at',)
