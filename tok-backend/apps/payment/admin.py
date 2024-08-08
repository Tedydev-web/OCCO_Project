from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, path
from django.utils.html import format_html

from api.services.firebase import send_and_save_notification
from apps.discovery.models import GiftLog
from apps.payment.models import Transaction, Wallet
from ultis.helper import format_currency


@admin.register(Transaction)
class TransactionCoinAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'transaction_type', 'return_code', 'from_user', 'display_add_info', 'created_at',)
    ordering = ('-created_at',)
    list_per_page = 15
    exclude = ('to_user',)
    search_fields = ('id', 'from_user__phone_number', 'from_user__id')
    list_filter = ('transaction_type', 'return_code')
    fields = ('display_add_info', 'transaction_type', 'return_code', 'from_user', 'created_at')
    readonly_fields = ('display_add_info', 'short_id', 'created_at', 'from_user', 'transaction_type',)

    def has_change_permission(self, request, obj=None):
        if obj and obj.return_code == '02':
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    # @admin.action(description='Hoàn tiền')
    # def refund_transaction(self, request, queryset):
    #     for transaction in queryset:
    #         if transaction.return_code == '01':  # Failed transactions
    #             self.process_refund(transaction, request)
    #             self.message_user(request,
    #                               'Đã tạo thành công đơn hoàn tiền cho giao dịch ID %(id)s.' % {
    #                                   'id': transaction.id})

    def process_refund(self, transaction, request):
        new_transaction = Transaction.objects.create(
            amount=transaction.amount,
            return_code='00',  # Assuming success for refund
            funds=transaction.funds,
            transaction_type='refund',
            from_user=request.user,
            to_user=transaction.from_user,
            information_detail={
                "original_transaction_id": str(transaction.id),
                "original_transaction_type": transaction.transaction_type,
                "original_return_code": transaction.return_code,
                "original_information_detail": transaction.information_detail,
            }
        )
        new_transaction.save()
        send_and_save_notification(user=new_transaction.to_user,
                                   title='Thông báo',
                                   body=f'Đã hoàn tiền cho đơn mua thóc thất bại giá trị {transaction.amount}',
                                   direct_user=request.user,
                                   )

    def refund_action(self, obj):
        if (obj.return_code == '01' and
                obj.transaction_type == 'deposit' and
                not Transaction.objects.filter(transaction_type='refund',
                                               information_detail__original_transaction_id=str(
                                                   obj.id)).exists()):  # Failed transactions
            return format_html(
                '<a class="button" href="{}" style="border: 1px solid #000; padding: 5px 10px; text-decoration: none; background-color: #f0f0f0; color: #000; border-radius: 5px;">Hoàn tiền</a>',
                reverse('admin:refund_single_transaction', args=[obj.pk])
            )
        return '-'

    refund_action.short_description = 'Hoàn tiền'
    refund_action.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('refund/<uuid:transaction_id>/', self.admin_site.admin_view(self.refund_single_transaction),
                 name='refund_single_transaction'),
        ]
        return custom_urls + urls

    def refund_single_transaction(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, pk=transaction_id)
        if transaction.return_code == '01':  # Failed transactions
            self.process_refund(transaction, request)
            self.message_user(request, 'Đã tạo thành công đơn hoàn tiền cho giao dịch ID %(id)s.' % {
                'id': transaction.id})
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def display_add_info(self, obj):
        global html_return
        if obj.transaction_type == 'deposit':
            html_return = (f"<p>Số tiền VNĐ: {format_currency(obj.information_detail['item_data']['vnd_price'])}</p>"
                           f"Số thóc: {obj.information_detail['item_data']['coin_price']}")
        elif obj.transaction_type == 'withdraw':
            try:
                html_return = (
                    f"<p>Số tiền VNĐ: {format_currency(obj.information_detail['item_data']['vnd_price'])}</p>"
                    f"<p>Số thóc: {obj.information_detail['item_data']['coin_price']}</p>"
                    f"<p>Ngân hàng: {obj.information_detail['banking']['fullname']}</p>"
                    f"<p>Bank code: {obj.information_detail['banking']['bank_code']}</p>"
                    f"<p>Chủ thẻ: {obj.information_detail['user_info']['account_name']}</p>"
                    f"<p>Số thẻ: {obj.information_detail['user_info']['bank_account']}</p>"
                )
            except Exception as e:
                print(e)
        elif obj.transaction_type == 'avatar':
            html_return = (f"<p>Số thóc: {obj.information_detail['avt']['coin_price']}</p> "
                           f"Khung avatar: <img src='{obj.information_detail['avt']['frame']}' width='50' height='50' />")
        elif obj.transaction_type == 'gift':
            html_return = (f"<p>Số thóc: {obj.information_detail['gift']['price']}</p> "
                           f"Khung avatar: <img src='{obj.information_detail['gift']['image']}' width='50' height='50' />")
        elif obj.transaction_type == 'uid':
            html_return = (f"<p>Số thóc: {obj.information_detail['uid']['coin_price']}</p> "
                           f"UID: {obj.information_detail['uid']['coin_price']}")
        elif obj.transaction_type == 'coinToAds':
            html_return = (f"<p>Số thóc: {obj.information_detail['coinToAds']['coin_price']}"
                           )
        elif obj.transaction_type == 'vip':
            html_return = (f"<p>Số thóc: {obj.information_detail['vip']['coin_price']}"
                           f"<p>Số tháng: {obj.information_detail['vip']['total_month']}"
                           )
        else:
            html_return = ''
        return format_html(html_return)

    def save_model(self, request, obj, form, change):
        if obj.return_code == '00' and obj.transaction_type == 'withdraw':
            send_and_save_notification(user=obj.from_user,
                                       title='Thông báo',
                                       body=f'Giao dịch rút {obj.amount} thóc xử lý thành công',
                                       custom_data={
                                           'direct_type': 'WITHDRAW_SUCCESS'
                                       })
        elif obj.return_code == '01' and obj.transaction_type == 'withdraw':
            wallet = Wallet.objects.get_or_create(user=obj.from_user)[0]
            wallet.add_balance(obj.amount)
            send_and_save_notification(user=obj.from_user,
                                       title='Thông báo',
                                       body=f'Giao dịch rút {obj.amount} thóc xử lý thất bại\n'
                                            f'Đã hoàn trả {obj.amount} thóc',
                                       custom_data={
                                           'direct_type': 'WITHDRAW_FAIL'
                                       }
                                       )
        obj.save()

    display_add_info.short_description = 'Thông tin chi tiết'


@admin.register(GiftLog)
class GiftLogAdmin(admin.ModelAdmin):
    list_display = ('sender', 'amount', 'total_price', 'gift', 'created_at',)
    list_filter = ('gift',)
    ordering = ('-created_at',)
    fields = ('sender', 'receiver', 'gift', 'amount', 'total_price')
    list_per_page = 15
    search_fields = ('sender', 'receiver', 'gift__title')
    readonly_fields = ('sender', 'receiver', 'gift', 'amount', 'total_price')
