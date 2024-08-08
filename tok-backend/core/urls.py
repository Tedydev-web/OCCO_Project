"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include, reverse_lazy

from core import settings
from django.conf.urls.static import static


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy('admin:dashboard')


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/v1/auth/user/', include('apps.user.urls')),
    path('api/v1/general/', include('apps.general.urls')),
    path('api/v1/conversation/', include('apps.conversation.urls')),
    path('api/v1/discovery/', include('apps.discovery.urls')),
    path('api/v1/blog/', include('apps.blog.urls')),
    path('api/v1/notification/', include('apps.notification.urls')),
    path('api/v1/friend/', include('apps.friend.urls')),
    path('api/v1/payment/', include('apps.payment.urls')),
    path('api/v1/ads/', include('apps.ads.urls')),
    path('admin/', admin.site.urls),
    path('webhook/', include('apps.webhook.urls')),
    path('dashboard/', include('apps.dashboard.urls'), name='dashboard'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_header = "OCCO Admin"
admin.site.site_title = "OCCO"
admin.site.index_title = "Chào mừng đến với OCCO"
