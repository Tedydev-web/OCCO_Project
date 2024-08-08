import datetime

from django.contrib import admin
from django.utils.html import format_html

from api.services.firebase import send_and_save_notification
from apps.ads.models import Advertisement, RateCoinPerView
from apps.payment.models import Transaction, Wallet
from apps.user.models import HobbyInformation, SearchInformation


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('status_verify', 'user', 'title', 'status_coming', 'start_date', 'end_date', 'created_at',)
    list_filter = ('status_verify', 'status_coming', 'target_type')
    search_fields = ('title', 'description', 'image', 'user__full_name', 'user__id')

    ordering = ('-created_at', 'status_verify')
    list_per_page = 15
    readonly_fields = (
        'user', 'image_preview', 'status_coming', 'video_preview', 'title', 'target_type', 'description', 'count_view',
        'count_click', 'targets', 'start_date', 'end_date',)
    fieldsets = (
        ('Thông tin cơ bản',
         {'fields': (
             'status_verify', 'note', 'status_coming', 'target_type', 'is_active', 'user', 'title', 'description',
             'start_date',
             'end_date', 'image_preview',
             'video_preview',)}),
        ('Mục tiêu hướng đến', {'fields': ('targets',)}),
        ('Báo cáo view/click', {'fields': ('count_view', 'count_click',)}),

    )

    def save_model(self, request, obj, form, change):
        if obj.status_verify == 'verified':
            obj.verified_by = request.user
            obj.verified_at = datetime.datetime.now()
            send_and_save_notification(user=obj.user,
                                       title='Thông báo',
                                       body='Chiến lược quảng bá của bạn đã được duyệt',
                                       custom_data={
                                           'direct_type': 'ADS_VERIFIED',
                                           'direct_value': str(obj.id)
                                       }
                                       )
        elif obj.status_verify == 'rejected':
            obj.verified_by = request.user
            obj.verified_at = datetime.datetime.now()
            send_and_save_notification(user=obj.user,
                                       title='Thông báo',
                                       body='Chiến lược quảng bá của bạn đã bị từ chối',
                                       custom_data={
                                           'direct_type': 'ADS_REJECTED',
                                           'direct_value': str(obj.id)
                                       })
            # trans = Transaction.objects.create(to_user=request.user,
            #                                    funds='Coin',
            #                                    transaction_type='refund',
            #                                    amount=obj.coin_price,
            #                                    return_code='00'
            #                                    )
            # trans.add_detail('advertisement', {
            #     'id': str(obj.id)
            # })
            # wallet = Wallet.objects.get_or_create(user=obj.user)[0]
            # wallet.add_balance(obj.coin_price)
            # send_and_save_notification(user=request.user,
            #                            title='Hoàn trả giao dịch quảng bá',
            #                            body=f'Số dư thóc hiện tại: {wallet.current_balance}')

        super(AdvertisementAdmin, self).save_model(request, obj, form, change)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" />', obj.image.file.url)
        elif obj.file_type == 'VIDEO' and obj.file:
            return format_html('<video width="200" controls><source src="{}" type="video/mp4"></video>',
                               obj.image.file.url)
        return ""

    def video_preview(self, obj):
        if obj.video:
            return format_html('<video width="200" controls><source src="{}" type="video/mp4"></video>',
                               obj.video.file.url)
        return ""

    def targets(self, obj):
        # Chuyển đổi giới tính
        gender_mapping = {
            'MALE': 'Nam',
            'FEMALE': 'Nữ',
            'GAY': 'Gay',
            'LESBIAN': 'Lesbian'
        }

        # Lấy giá trị và thay thế nếu cần
        gender_display = ', '.join(gender_mapping.get(g, '---') for g in obj.target.get('gender', [])) or '---'
        from_age = obj.target.get('from_age', '---')
        to_age = obj.target.get('to_age', '---')
        country = obj.target.get('country', '---') if obj.target.get('country') else '---'
        province = ', '.join(obj.target.get('province', '---')) if obj.target.get('province') else '---'
        distance = obj.target.get('distance', '---') if obj.target.get('distance') else '---'
        habit = obj.target.get('habit', '---')
        habit = ', '.join(HobbyInformation.objects.filter(id__in=habit).values_list('title', flat=True))
        search = obj.target.get('search', '---')
        search = ', '.join(SearchInformation.objects.filter(id__in=search).values_list('title', flat=True))

        html_target = ""
        if obj.platform == 'ANDROID':
            html_target += f"Link: {obj.android_url}"
        elif obj.platform == 'IOS':
            html_target += f"Link: {obj.ios_url}"
        if obj.target_type == 'WEB':
            html_target += f"Link: {obj.direct_url}"

        # Tạo chuỗi HTML với các thông tin trên
        html_return = (f"Giới tính: {gender_display}<br>"
                       f"Độ tuổi: {from_age} - {to_age}<br>"
                       f"Quốc gia: {country}<br>"
                       f"Tỉnh thành: {province}<br>"
                       f"Khoảng cách: {distance}km<br>"
                       f"Sở thích: {habit}<br>"
                       f"Đang tìm kiếm: {search}<br>"
                       f"Nền tảng: {obj.platform}<br>")
        html_return += html_target
        return format_html(html_return)

    targets.short_description = ""
    image_preview.short_description = 'Ảnh'
    video_preview.short_description = 'Video'


@admin.register(RateCoinPerView)
class RateCoinPerViewAdmin(admin.ModelAdmin):
    list_display = ('description', 'coin', 'updated_at')
    readonly_fields = ('description',)
    fields = ('description', 'coin')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
