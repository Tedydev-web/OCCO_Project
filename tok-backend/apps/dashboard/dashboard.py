from datetime import datetime, timedelta

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from django.contrib.admin import AdminSite
from django.db.models import Count, When, Case, Value, Sum, Q

import matplotlib.pyplot as plt
import io
import base64

from django.forms import CharField
from django.shortcuts import render
from django.urls import path
from django.utils.html import mark_safe

from apps.blog.models import Blog
from apps.discovery.models import LiveStreamingHistory, GiftLog
from apps.general.models import FileUpload, Report
from apps.payment.models import Transaction
from apps.user.models import CustomUser


class MyAdminSite(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        if request.user.country != 'All':
            filter_query = Q(country=request.user.country)
            filter_blog = Q(user__country=request.user.country)
            filter_live = Q(host__country=request.user.country)
            filter_gift = Q(sender__country=request.user.country)
            filter_transaction = Q(from_user__country=request.user.country)
        else:
            filter_query = Q()
            filter_blog = Q()
            filter_live = Q()
            filter_gift = Q()
            filter_transaction = Q()
        # Thống kê số lượng người dùng online và tổng số người dùng
        online_users = CustomUser.objects.filter(is_online=True, is_fake=False).filter(filter_query).count()
        offline_users = CustomUser.objects.filter(is_online=False, is_fake=False).filter(filter_query).count()
        total_users = CustomUser.objects.filter(is_fake=False).filter(filter_query).count()

        # # Thống kê độ tuổi theo các khoảng 10 năm
        # age_distribution = CustomUser.objects.filter(is_fake=False).annotate(
        #     age_range=Case(
        #         When(age__range=(15, 20), then=Value('15-20')),
        #         When(age__range=(20, 30), then=Value('20-30')),
        #         When(age__range=(30, 40), then=Value('30-40')),
        #         When(age__range=(40, 50), then=Value('40-50')),
        #         When(age__range=(50, 60), then=Value('50-60')),
        #         default=Value('Unknown'),
        #     )
        # ).values('age_range').annotate(count=Count('age_range')).order_by('age_range')
        #
        # age_ranges = [item['age_range'] for item in age_distribution]
        # counts = [item['count'] for item in age_distribution]

        # Thống kê số lượng bài đăng từ Blog model
        today = datetime.now().date()
        # all_blog = Blog.objects.all()
        total_blog_posts = Blog.objects.filter(filter_blog).count()
        # new_blogs_today = Blog.objects.filter(created_at__date=today).count()
        # new_image_today = FileUpload.objects.filter(blog__in=new_blogs_today, file_type='IMAGE').count()
        # new_video_today = FileUpload.objects.filter(blog__in=new_blogs_today, file_type='VIDEO').count()
        # blog_report_today = Report.objects.filter(created_at__date=today, type='BLOG').count()
        # total_image_blogs = FileUpload.objects.filter(blog__in=all_blog, file_type='IMAGE').count()
        # total_video_blogs = FileUpload.objects.filter(blog__in=all_blog, file_type='VIDEO').count()
        # total_report_blog = Report.objects.filter(type='BLOG').count()

        # payment
        total_transaction_deposit = Transaction.objects.filter(transaction_type='deposit').filter(
            filter_transaction).count()

        # Thống kê số lượng phiên live stream từ Live model
        total_live_streams = LiveStreamingHistory.objects.exclude(type='CHAT').filter(filter_live).count()
        new_users_today = CustomUser.objects.filter(is_fake=False,date_joined=datetime.now()).filter(filter_query).count()
        inactive_users_30_days = CustomUser.objects.filter(is_fake=False,
                                                           last_update__lte=datetime.now() - timedelta(days=30)).filter(
            filter_query).count()
        inactive_users_7_days = CustomUser.objects.filter(is_fake=False,
                                                          last_update__lte=datetime.now() - timedelta(days=7)).filter(
            filter_query).count()

        # Thống kê số lượng và giá trị quà tặng
        total_gifts = GiftLog.objects.filter(filter_gift).count()
        total_gift_value = GiftLog.objects.filter(filter_gift).aggregate(Sum('amount'))['amount__sum']
        context = super().each_context(request)
        context.update({
            'new_users_today': new_users_today,
            'inactive_users_30_days': inactive_users_30_days,
            'inactive_users_7_days': inactive_users_7_days,
            'online_users': online_users,
            'offline_users': offline_users,
            'total_users': total_users,
            'total_blog_posts': total_blog_posts,
            'total_live_streams': total_live_streams,
            'total_gifts': total_gifts,
            'total_gift_value': total_gift_value, }
        )
        return render(request, 'dashboard.html', context)


admin_site = MyAdminSite(name='myadmin')
