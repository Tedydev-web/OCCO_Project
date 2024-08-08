from django.urls import path
from .views import *

urlpatterns = [
    path('all/<uuid:pk>/', GetBlogAPIView.as_view()),
    path('friend/', GetBlogInterestAPIView.as_view()),
    path('proposal/', GetBlogProposalAPIView.as_view()),

    path('detail/<uuid:pk>/', BlogDetailAPIView.as_view()),
    path('create/', CreateBlogAPIView.as_view()),
    path('update/<uuid:pk>/', UpdateBlogAPIView.as_view()),
    path('delete/<uuid:pk>/', DeleteBlogAPIView.as_view()),

    path('like/', LikeBlogAPIView.as_view()),
    path('unlike/', UnLikeBlogAPIView.as_view()),

    # comment
    path('<uuid:pk>/comment/', GetCommentAPIView.as_view()),
    path('comment/create/', CreateCommentAPIView.as_view()),
    path('comment/update/<uuid:pk>/', UpdateCommentAPIView.as_view()),
    path('comment/delete/<uuid:pk>/', DeleteCommentAPIView.as_view()),

    path('comment/like/', LikeCommentAPIView.as_view()),
    path('comment/unlike/', UnLikeCommentAPIView.as_view()),


    # reply commemt
    path('comment/<uuid:pk>/reply/', GetReplyCommentAPIView.as_view()),
    path('comment/reply/add/', AddReplyCommentAPIView.as_view()),
    path('comment/reply/update/<uuid:pk>/', UpdateReplyCommentAPIView.as_view()),
    path('comment/reply/delete/<uuid:pk>/', DeleteReplyCommentAPIView.as_view()),

    path('comment/reply/like/', LikeReplyCommentAPIView.as_view()),
    path('comment/reply/unlike/', UnLikeReplyCommentAPIView.as_view()),

    # list audio file
    path('audio/list/', GetListAudioAPIView.as_view()),

    #
    path('search/', SearchBlogAPIView.as_view()),

    #
    path('hide/<uuid:pk>/', HideBlogAPIView.as_view()),
]