from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from api.services.firebase import send_and_save_notification
from apps.user.models import *


# Register your models here.
@admin.register(WorkInformation, CharacterInformation, SearchInformation, HobbyInformation, CommunicateInformation)
class AllInformationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_per_page = 15
    ordering = ('created_at',)


# Tạo custom admin class cho mô hình CustomUser và đăng ký nó bằng decorator
class BaseInformationInline(admin.TabularInline):
    model = BaseInformation
    extra = 0  # Số lượng form trống hiển thị để thêm mới
    raw_id_fields = ('work', 'hobby', 'search', 'communicate', 'character')

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     return queryset.select_related('user').prefetch_related(
    #         'searchinformation_set', 'workinformation_set', 'characterinformation_set', 'hobbyinformation_set', 'communicateinformation_set'
    #     )


class FriendShipAdmin(admin.TabularInline):
    model = FriendShip
    fk_name = 'sender'


class BlockUserAdmin(admin.TabularInline):
    model = Block
    fk_name = 'from_user'


class ProfileImageTabular(admin.TabularInline):
    model = ProfileImage
    fields = ['display_avatar_image', ]
    readonly_fields = ['display_avatar_image', ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('image')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def display_avatar_image(self, obj):
        if obj.image:
            return mark_safe('<div style="text-align:center;"><img src="{0}" width="200" height="200" /></div>'.format(
                obj.image.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<div style="text-align:center;"><img src="{0}" width="200" height="200" /></div>'.format(
                default_avatar_url))

    display_avatar_image.short_description = 'Ảnh profile'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('uid', 'display_avatar_admin', 'full_name', 'email', 'phone_number', 'date_joined', 'is_active','view_messages_link')
    list_editable = ('is_active',)

    search_fields = ('full_name', 'phone_number', 'email', 'uid')
    list_filter = ('is_active', 'is_fake')
    readonly_fields = ('display_work_info', 'display_character_info', 'display_hobby_info', 'display_communicate_info',
                       'display_search_info', 'display_avatar_link', 'display_avatar_image', 'token',
                       'display_avatar_admin', 'is_online', 'phone_number', 'display_lat_lng', 'province',
                       'id_card_detail','view_messages_link')
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': (
                'is_active', 'uid',
                'display_avatar_image', 'display_avatar_link', 'full_name', 'email', 'height', 'weight', 'phone_number',
                'date_of_birth', 'age', 'gender', 'province'
            ),
        }),
        ('Thông tin cơ bản', {
            'fields': ('display_work_info', 'display_character_info', 'display_hobby_info',
                       'display_communicate_info', 'display_search_info'),
            'classes': ('collapse',)  # Đặt collapse để ẩn fieldset này mặc định
        }),
        ('CCCD', {
            'fields': ('id_card_detail',)
        }),
        ('Hoạt động', {
            'fields': ('view_messages_link',)
        }),

    )
    inlines = [ProfileImageTabular]
    ordering = ('-created_at', '-updated_at',)
    list_per_page = 15
    required_group_ids = [2, 4]

    def render_change_form(
            self, request, context, add=False, change=False, form_url="", obj=None
    ):
        return super().render_change_form(
            request, context, add, False, form_url, obj
        )

    def display_lat_lng(self, obj):
        return f"{obj.lat}, {obj.lng}"

    def has_add_permission(self, request):
        return False

    def display_work_info(self, obj):
        return ", ".join([str(work) for work in obj.baseinformation.work.all()])

    display_work_info.short_description = 'Nghề nghiệp'

    def display_avatar_link(self, obj):
        if obj.avatar:
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(obj.avatar.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<a href="{0}" target="_blank">{0}</a>'.format(default_avatar_url))

    display_avatar_link.short_description = 'Link ảnh đại diện'

    def display_avatar_image(self, obj):
        if obj.avatar:
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(obj.avatar.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(default_avatar_url))

    display_avatar_image.short_description = 'Ảnh đại diện'

    def display_avatar_admin(self, obj):
        if obj.avatar:
            return mark_safe('<img src="{0}" width="60" height="60" />'.format(obj.avatar.file.url))
        else:
            default_avatar_url = DefaultAvatar.objects.get(key='avatar').image.url
            return mark_safe('<img src="{0}" width="60" height="60" />'.format(default_avatar_url))

    display_avatar_admin.short_description = 'Ảnh đại diện'

    def display_character_info(self, obj):
        return ", ".join([str(character) for character in obj.baseinformation.character.all()])

    display_character_info.short_description = 'Tính cách'

    def display_hobby_info(self, obj):
        return ", ".join([str(hobby) for hobby in obj.baseinformation.hobby.all()])

    display_hobby_info.short_description = 'Sở thích'

    def display_communicate_info(self, obj):
        return ", ".join([str(communicate) for communicate in obj.baseinformation.communicate.all()])

    display_communicate_info.short_description = 'Nhu cầu'

    def display_search_info(self, obj):
        return ", ".join([str(search) for search in obj.baseinformation.search.all()])

    display_search_info.short_description = 'Tìm kiếm'

    def id_card_detail(self, obj):
        try:
            id_card = IDCard.objects.get_or_create(user=obj)[0]
            return format_html(
                '<img src="{}" alt="Face Image" class="zoomable-image">'
                '<div class="image-container">'
                '<img src="{}" alt="Front Image" class="zoomable-image">'
                '<img src="{}" alt="Back Image" class="zoomable-image">'
                '</div>'
                '<div><strong>Mã định danh:</strong> {}</div>'
                '<div><strong>Họ và tên:</strong> {}</div>'
                '<div><strong>Giới tính:</strong> {}</div>'
                '<div><strong>Ngày tháng năm sinh:</strong> {}</div>'
                '<div><strong>Ngày cấp:</strong> {}</div>'
                '<div><strong>Nơi thường trú:</strong> {}</div>',
                id_card.id_face_image.url if id_card.id_face_image else '',
                id_card.id_front_image.url,
                id_card.id_back_image.url,
                id_card.id_identifier,
                id_card.id_full_name,
                id_card.get_id_gender_display(),
                id_card.id_date_of_birth,
                id_card.id_date_issuance,
                id_card.id_place_of_residence,
            )
        except Exception as e:
            print(e)
            return ''

    id_card_detail.short_description = ''

    def get_queryset(self, request):
        if request.user.country == 'All':
            return super().get_queryset(request).exclude(is_superuser=True)
        else:
            return super().get_queryset(request).exclude(is_superuser=True).filter(country=request.user.country)

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and "country" not in self.list_filter:
            self.list_filter += ("country",)
        return super().changelist_view(request, extra_context)

    def view_messages_link(self, obj):
        url = reverse('userTimeline', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Xem hoạt động</a>', url)

    view_messages_link.short_description = 'Xem hoạt động'


@admin.register(ReportMessage)
class ReportMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'count', 'banned_to')
    exclude = ('created_at', 'updated_at')
    ordering = ('-banned_to', '-count')
    readonly_fields = ('user',)
    required_group_ids = [2, 6]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and "country" not in self.list_filter:
            self.list_filter += ("user__country",)
        else:
            self.list_filter = ()
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        if request.user.country != 'All':
            return super().get_queryset(request).filter(user__country=request.user.country)
        else:
            return super().get_queryset(request).all()

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('log', 'user', 'code', 'active', 'created_at')
    list_per_page = 20
    ordering = ('-created_at',)


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    list_per_page = 15
    search_fields = ('user', 'phone_number')


@admin.register(IDCard)
class IDCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'status_verify')
    fieldsets = (
        ('Thông tin', {
            'fields': ('status_verify', 'id_card_detail',)
        }),
    )
    readonly_fields = ('id_card_detail',)
    ordering = ('-created_at', 'status_verify')
    list_filter = ('status_verify',)
    search_fields = ('user__full_name', 'user__phone_number', 'user__uid')

    # def get_queryset(self, request):
    #     return p
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def id_card_detail(self, obj):
        return format_html(
            '<img src="{}" alt="Face Image" class="zoomable-image">'
            '<div class="image-container">'
            '<img src="{}" alt="Front Image" class="zoomable-image">'
            '<img src="{}" alt="Back Image" class="zoomable-image">'
            '</div>'
            '<div><strong>Mã định danh:</strong> {}</div>'
            '<div><strong>Họ và tên:</strong> {}</div>'
            '<div><strong>Giới tính:</strong> {}</div>'
            '<div><strong>Ngày tháng năm sinh:</strong> {}</div>'
            '<div><strong>Ngày cấp:</strong> {}</div>'
            '<div><strong>Nơi thường trú:</strong> {}</div>',
            obj.id_face_image.url if obj.id_face_image else '',
            obj.id_front_image.url,
            obj.id_back_image.url,
            obj.id_identifier,
            obj.id_full_name,
            obj.get_id_gender_display(),
            obj.id_date_of_birth,
            obj.id_date_issuance,
            obj.id_place_of_residence,
        )

    id_card_detail.short_description = ''

    def save_model(self, request, obj, form, change):
        if obj.status_verify == 'verified':
            send_and_save_notification(user=obj.user,
                                       title='Thông báo',
                                       body=f'Thông tin bảo mật CCCD của bạn đã được duyệt',
                                       direct_type='ID_CARD_VERIFIED'
                                       )
        elif obj.status_verify == 'rejected':
            send_and_save_notification(user=obj.user,
                                       title='Thông báo',
                                       body=f'Thông tin bảo mật CCCD của bạn đã bị từ chối',
                                       direct_type='ID_CARD_REJECTED'
                                       )
            obj.id_face_image = None
            obj.id_front_image = None
            obj.id_back_image = None
            obj.id_date_of_birth = None
            obj.id_date_issuance = None
            obj.id_place_of_residence = None
            obj.id_gender = None
            obj.id_full_name = None
            obj.id_identifier = None

        obj.verified_by = request.user
        obj.save()

    def get_queryset(self, request):
        if request.user.country != 'All':
            return super().get_queryset(request).filter(user__country=request.user.country).exclude(status_verify='start')
        return super().get_queryset(request).all().exclude(status_verify='start')

    def changelist_view(self, request, extra_context=None):
        if request.user.country == 'All' and "country" not in self.list_filter:
            self.list_filter += ("user__country",)
        return super().changelist_view(request, extra_context)
