from typing import Dict, Any

JAZZMIN_SETTINGS_: Dict[str, Any] = {
    "site_title": "OCCO Admin",
    "site_header": "OCCO Admin",
    "site_footer": "OCCO Admin",
    "site_logo_classes": None,
    "site_icon": "/jazzmin/img/tok.png",  # Đường dẫn đến logo của bạn
    "site_logo": "/jazzmin/img/tok.png",

    "login_logo_background": "/jazzmin/img/tok.png",
    "welcome_sign": "Trang web quản trị OCCO",
    "dashboard_title": "Trang chủ",
    # Copyright on the footer
    "copyright": "Cydeva Technology Solutions",
    "development_version": False,
    "version": "",
    "icons": {
        "user": "fas fa-users",
        "user.CustomUser": "fas fa-users",
        "user.ReportMessage": "fas fa-ban",
        "user.IDCard": "fas fa-id-card",

        "general.Report": "far fa-flag",
        "general.DefaultSetting": "fas fa-wrench",
        "general.AppConfig": "fas fa-wrench",
        "general.FeedBack": "fas fa-inbox",
        "general.BackGroundColor": "fas fa-palette",
        "general.CoinTrading": "fas fa-coins",
        "general.MoneyTrading": "fas fa-money-bill-wave-alt",
        "general.UIDTrading": "fas fa-sort-numeric-up",
        "general.StickerCategory": "fas fa-sticky-note",
        "general.FileUploadAudio": "fas fa-microphone",
        "general.AdminProxy": "fas fa-users-cog",
        "general.AppInformation": "fas fa-info",
        "general.AvatarFrame": "fas fa-crop-alt",
        "conversation.Room": "fas fa-comments",

        "discovery.LiveChatProxy": "fas fa-comment-dots",
        "discovery.LiveStreamProxy": "fas fa-tv",
        "discovery.LiveAudioProxy": "fas fa-headset",
        "discovery.LiveVideoProxy": "fas fa-video",
        "discovery.Gift": "fas fa-gifts",
        "discovery.GiftLog": "fas fa-donate",

        "blog.Blog": "fas fa-blog",
        "blog.AudioUpload": "far fa-file-audio",
        "notification.Notification": "fas fa-bell",

        "payment.Transaction": "fas fa-file-invoice-dollar",

        "ads.Advertisement": "fab fa-adversal",
        "ads.RateCoinPerView": "fas fa-percentage"

    },
    # "search_model": ["user.WorkInformation"],
    "topmenu_links": [
        # {"name": "Trang chủ", "url": "/dashboard", "permissions": ["auth.view_user"]},
        {"name": "Chăm sóc khách hàng", "url": "/dashboard/cskh/", "permissions": ["auth.view_user"]},
        {"name": "Báo cáo và thống kê", "url": "/dashboard/statistics/", "permissions": ["auth.view_user"]},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        # { "name": "Cài đặt giá trị", "app": "user",},
    ],
    # "order_with_respect_to": ["apps.user.workinformation"],

    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "use_google_fonts_cdn": True,
    # "language_chooser": True,
    "hide_apps": ["admin.LogEntry", "notification"],
    "hide_models": [
        "django_celery_beat.clockedschedule",
        "django_celery_beat.crontabschedule",
        "django_celery_beat.intervalschedule",
        "django_celery_beat.solarschedule",
        "django_celery_beat.periodictask",
        "auth.group",
        "user.WorkInformation",
        "user.CharacterInformation",
        "user.SearchInformation",
        "user.HobbyInformation",
        "user.CommunicateInformation",
        "user.OTP",
        "user.UserLog",
        # "conversation.Room",
        "general.DefaultAvatar",
        "general.DevSetting",
        "general.FileUpload",
        # "general.Feedback",
        # "discovery.Gift",
        "notification.UserDevice",
        "admin.LogEntry",
        # "general.AdminProxy",
        'notification.Notification',
        # "discovery.LiveChatProxy",
        # "discovery.LiveAudioProxy",
        # "discovery.LiveVideoProxy",
        "blog.Comment",
        "blog.ReplyComment",
        "blog.LikeBlog",
        "blog.LikeReplyComment",
        "blog.LikeComment",
    ],
    "custom_links": {
        "books": [{
            "name": "Admin Setting",
            "url": "admin_setting",
            "icon": "fas fa-comments",
            "permissions": ["user", "general"]
        }]
    },
    "custom_js": "js/dashboard.js",
    # "order_with_respect_to": ["general", "user.WorkInformation", "user"],
    # "ui_builder": {"extras": ["imagekit", "filer"]},
    # "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS_ = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-purple navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-indigo",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
