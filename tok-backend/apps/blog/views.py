import json
from datetime import datetime

from django.db.models import Q
from django.shortcuts import render
from ipware import get_client_ip
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.firebase import send_and_save_notification
from apps.blog.models import Blog, Comment, ReplyComment, AudioUpload
from apps.blog.serializers import BlogSerializer, CommentSerializer, ReplyCommentSerializer, BlogCreateSerializer, \
    CreateCommentSerializer, CreateReplyCommentSerializer, AudioSerializer
from apps.dashboard.models import NotificationAdmin
from apps.user.models import FriendShip, CustomUser, UserLog, UserTimeline
from ultis.api_helper import api_decorator
from api.services.telegram_admin import send_telegram_message
from ultis.helper import get_paginator_limit_offset


class GetBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        blog_of_user = Blog.objects.filter(user=user, is_active=True).order_by('-created_at').select_related(
            'user', 'audio').prefetch_related('file', 'tagged_users', 'hide_by').exclude(hide_by=request.user)
        qs, paginator = get_paginator_limit_offset(blog_of_user, request)
        serializer = BlogSerializer(qs, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data
        return data, 'Toàn bộ bài đăng!', status.HTTP_200_OK


class GetBlogProposalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        list_block = CustomUser.custom_objects.list_blocking(request.user)
        queryset = Blog.objects.filter(is_active=True).order_by('-created_at', '-count_like',
                                                                '-count_comment').select_related(
            'user', 'audio').prefetch_related('file', 'tagged_users', 'hide_by').exclude(hide_by=request.user).exclude(user__id__in=list_block)
        qs, paginator = get_paginator_limit_offset(queryset, request)

        serializer = BlogSerializer(qs, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data

        return data, 'Bài đăng đề xuất!', status.HTTP_200_OK


class GetBlogInterestAPIView(APIView):  # lấy bài viết của bạn bè mục "quan tâm" theo TOK FeatureList
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        list_friend = CustomUser.custom_objects.list_friend(request.user)

        queryset = Blog.objects.select_related('user', 'audio').prefetch_related('file', 'tagged_users').filter(
            user__in=list_friend, is_active=True).order_by('-created_at', 'hide_by').exclude(hide_by=request.user)

        qs, paginator = get_paginator_limit_offset(queryset, request)

        serializer = BlogSerializer(qs, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data
        return data, 'Bài viết của bạn bè!', status.HTTP_200_OK


class BlogDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        try:
            serializer = BlogSerializer(Blog.objects.get(id=pk, is_active=True), context={'request': request})
            return serializer.data, 'Chi tiết bài đăng', status.HTTP_200_OK
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST


class CreateBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        number_of_files = len(request.data.get("file", []))
        if int(number_of_files) > 9:
            return {}, 'Vượt quá số hình cho phép!', status.HTTP_400_BAD_REQUEST
        else:
            request.data['user'] = str(request.user.id)
            serializer = BlogCreateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                blog = Blog.objects.get(id=serializer.data['id'])
                data = BlogSerializer(blog, context={'request': request}).data
                url_admin = f"https://occo.tokvn.live/admin/blog/blog/{data['id']}/change/"
                user_log = \
                    UserLog.objects.get_or_create(user=str(request.user.id),
                                                  phone_number=str(request.user.phone_number))[0]
                ipaddr = get_client_ip(request)[0]
                user_log.blog.append({
                    'ipaddr': ipaddr,
                    'date': str(datetime.now()),
                    'data': data
                })
                user_log.save()
                notification_admin = NotificationAdmin.objects.create(
                    from_user=request.user,
                    title=f"{request.user.full_name} đã tạo bài đăng",
                    body=f"",
                    type='NEW',
                    link=url_admin
                )
                send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
                return data, 'Tạo bài đăng thành công!', status.HTTP_200_OK


class UpdateBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        try:
            blog = Blog.objects.get(id=pk, is_active=True)
        except:
            return {}, 'Bài đăng không tồn tại!', status.HTTP_400_BAD_REQUEST
        serializer = BlogSerializer(blog, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Cập nhật bài đăng thành công!', status.HTTP_200_OK


class DeleteBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        try:
            blog = Blog.objects.get(id=pk)
            blog.delete()
            return {}, 'Xóa bài đăng thành công!', status.HTTP_204_NO_CONTENT
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST


class LikeBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        blog_id = request.data.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST

        check_exists = blog.user_like.filter(id=request.user.id).exists()
        if check_exists:
            return {}, 'Đã yêu thích rồi!', status.HTTP_400_BAD_REQUEST
        else:
            blog.count_like += 1
            blog.user_like.add(request.user)
            blog.save()
            if blog.user != request.user:
                send_and_save_notification(user=blog.user,
                                           title='Thông báo',
                                           body=f"{request.user.full_name} đã yêu thích bài viết của bạn",
                                           direct_type='USER_LIKE_BLOG',
                                           direct_value=str(blog.id))
            url_admin = f"https://occo.tokvn.live/admin/blog/blog/{str(blog.id)}/change/"

            notification_admin = NotificationAdmin.objects.create(
                from_user=request.user,
                title=f"{request.user.full_name} đã thích bài viết của {blog.user.full_name}",
                body=f"",
                type='LIKE',
                link=url_admin
            )
            user_timeline = UserTimeline.objects.create(
                user=request.user,
                title=f"{request.user.full_name} đã thích bài viết",
                body=f"",
                type='LIKE',
                fk_id=str(blog.id),
                link=url_admin,
                direct_user=blog.user
            )
            send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
            return {}, 'Đã yêu thích bài đăng!', status.HTTP_200_OK


class UnLikeBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        blog_id = request.data.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST

        check_exists = blog.user_like.filter(id=request.user.id).exists()
        if check_exists:
            blog.count_like -= 1
            blog.user_like.remove(request.user)
            blog.save()
            return {}, 'Đã hủy yêu thích bài đăng!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Chưa yêu thích bài đăng!', status.HTTP_400_BAD_REQUEST


class GetCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        queryset = Comment.objects.filter(blog__id=pk, is_active=True).select_related('blog', 'user').prefetch_related(
            'replycomment_set').order_by('-created_at')
        queryset, paginator = get_paginator_limit_offset(queryset, request)
        serializer = CommentSerializer(queryset, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data
        return data, 'Bình luận của 1 bài đăng!', status.HTTP_200_OK


class CreateCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        request.data['user'] = str(request.user.id)
        serializer = CreateCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            blog_id = request.data.get('blog')
            blog = Blog.objects.get(id=blog_id)
            blog.count_comment += 1
            blog.save()

        comment = Comment.objects.get(id=serializer.data['id'])
        serializer = CommentSerializer(comment, context={'request': request})
        data = serializer.data
        user_log = \
            UserLog.objects.get_or_create(user=str(request.user.id), phone_number=str(request.user.phone_number))[0]
        ipaddr = get_client_ip(request)[0]
        user_log.comment.append({
            'ipaddr': ipaddr,
            'date': str(datetime.now()),
            'data': data
        })
        user_log.save()

        if comment.blog.user != request.user:
            send_and_save_notification(user=comment.blog.user,
                                       title='Thông báo',
                                       body=f"{request.user.full_name} đã bình luận về bài viết của bạn",
                                       direct_type='USER_CMT_BLOG',
                                       direct_value=str(comment.blog.id))

        url_admin = f"https://occo.tokvn.live/admin/blog/blog/{str(comment.blog.id)}/change/"
        notification_admin = NotificationAdmin.objects.create(
            from_user=request.user,
            title=f"{request.user.full_name} đã bình luận bài viết của {comment.blog.user.full_name}",
            body=f"với nội dung: {comment.content}",
            type='COMMENT',
            link=url_admin
        )
        send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
        user_timeline = UserTimeline.objects.create(
            user=request.user,
            title=f"{request.user.full_name} đã bình luận bài viết",
            body=f"{comment.content}",
            type='COMMENT',
            fk_id=str(comment.blog.id),
            link=url_admin,
            direct_user=comment.blog.user
        )
        return data, 'Thêm bình luận thành công!', status.HTTP_200_OK


class UpdateCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        request.data['user'] = str(request.user.id)
        # blog_id = request.data.get('blog')
        # blog = Blog.objects.get(id=blog_id)
        comment = Comment.objects.get(id=pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Cập nhật bình luận thành công!', status.HTTP_200_OK


class DeleteCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk, is_active=True)
        except:
            return {}, 'Comment không tồn tại!', status.HTTP_400_BAD_REQUEST

        comment.blog.count_comment -= 1
        comment.blog.save()

        comment.is_active = False
        comment.save()

        return {}, 'Xóa thành công!', status.HTTP_204_NO_CONTENT


class LikeCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        comment_id = request.data.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id)
            if not comment.user_like.filter(id=request.user.id).exists():
                comment.count_like += 1
                comment.user_like.add(request.user)
                comment.save()
                if comment.user != request.user:
                    send_and_save_notification(user=comment.user,
                                               title='Thông báo',
                                               body=f"{request.user.full_name} đã thích 1 bình luận của bạn",
                                               direct_type='USER_LIKE_CMT',
                                               direct_value=str(comment.blog.id))
                return {}, 'Đã yêu thích bình luận này!', status.HTTP_200_OK
            else:
                return {}, 'Bạn đã yêu thích bình luận này rồi!', status.HTTP_400_BAD_REQUEST

        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST


class UnLikeCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        comment_id = request.data.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id)
            if comment.user_like.filter(id=request.user.id).exists():
                comment.count_like -= 1
                comment.user_like.remove(request.user)
                comment.save()
                return {}, 'Hủy yêu thích!', status.HTTP_200_OK
            else:
                return {}, 'Chưa yêu thích!', status.HTTP_400_BAD_REQUEST

        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST


class GetReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        queryset = ReplyComment.objects.filter(comment_id=pk)
        serializer = ReplyCommentSerializer(queryset, many=True, context={'request': request})
        return serializer.data, 'Các phản hồi của bình luận!', status.HTTP_200_OK


class AddReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        request.data['user'] = str(request.user.id)
        serializer = CreateReplyCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        reply_comment = ReplyComment.objects.get(id=serializer.data['id'])
        reply_comment.comment.blog.count_comment += 1
        reply_comment.comment.blog.save()
        serializer = ReplyCommentSerializer(reply_comment, context={'request': request})
        data = serializer.data
        user_log = \
            UserLog.objects.get_or_create(user=str(request.user.id), phone_number=str(request.user.phone_number))[0]
        ipaddr = get_client_ip(request)[0]
        user_log.comment.append({
            'ipaddr': ipaddr,
            'date': str(datetime.now()),
            'data': data
        })
        user_log.save()
        if reply_comment.user != request.user:
            send_and_save_notification(user=reply_comment.user,
                                       title='Thông báo',
                                       body=f"{request.user.full_name} đã phản hồi về bình luận của bạn",
                                       direct_type='USER_CMT_BLOG',
                                       direct_value=str(reply_comment.comment.blog.id))
        url_admin = f"https://occo.tokvn.live/admin/blog/blog/{str(reply_comment.comment.blog.id)}/change/"
        notification_admin = NotificationAdmin.objects.create(
            from_user=request.user,
            title=f"{request.user.full_name} đã phản hồi bình luận của {reply_comment.user.full_name}",
            body=f"với nội dung: {reply_comment.content}",
            type='COMMENT',
            link=url_admin
        )
        send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
        user_timeline = UserTimeline.objects.create(
            user=request.user,
            title=f"{request.user.full_name} đã phản hồi bình luận",
            body=f"{reply_comment.content}",
            type='COMMENT',
            fk_id=str(reply_comment.comment.blog.id),
            link=url_admin,
            direct_user=reply_comment.user
        )
        return data, 'Phản hồi bình luận thành công!', status.HTTP_200_OK


class UpdateReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        try:
            reply_comment = ReplyComment.objects.get(id=pk)
        except:
            return {}, 'Phản hồi này không tồn tại!', status.HTTP_400_BAD_REQUEST
        serializer = ReplyCommentSerializer(reply_comment, data=request.data, partial=True,
                                            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Cập nhật phản hồi bình luận thành công!', status.HTTP_200_OK


class DeleteReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        try:
            reply_comment = ReplyComment.objects.get(id=pk)
            reply_comment.is_active = False
            reply_comment.save()
            return {}, 'Xóa bình luận thành công!', status.HTTP_204_NO_CONTENT
        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST


class LikeReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        comment_id = request.data.get('reply_id')
        try:
            comment = ReplyComment.objects.get(id=comment_id)
            if not comment.user_like.filter(id=request.user.id).exists():
                comment.count_like += 1
                comment.user_like.add(request.user)
                comment.save()
                if comment.user != request.user:
                    send_and_save_notification(user=comment.user,
                                               title='Thông báo',
                                               body=f"{request.user.full_name} đã thích 1 phản hồi bình luận của bạn",
                                               direct_type='USER_LIKE_CMT',
                                               direct_value=str(comment.blog.id))

                return {}, 'Đã yêu thích bình luận này!', status.HTTP_200_OK
            else:
                return {}, 'Bạn đã yêu thích bình luận này rồi!', status.HTTP_400_BAD_REQUEST

        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST


class UnLikeReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        comment_id = request.data.get('reply_id')
        try:
            comment = ReplyComment.objects.get(id=comment_id)
            if comment.user_like.filter(id=request.user.id).exists():
                comment.count_like -= 1
                comment.user_like.remove(request.user)
                comment.save()
                return {}, 'Hủy yêu thích!', status.HTTP_200_OK
            else:
                return {}, 'Chưa yêu thích!', status.HTTP_400_BAD_REQUEST

        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST


class GetListAudioAPIView(APIView):
    @api_decorator
    def get(self, request):
        qs = AudioUpload.objects.all().order_by('index', '-created_at')
        qs, paginator = get_paginator_limit_offset(qs, request)
        serializer = AudioSerializer(qs, many=True)
        data = paginator.get_paginated_response(serializer.data).data
        return data, "Danh sách file audio", status.HTTP_200_OK


class SearchBlogAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword', '')
        qs = Blog.objects.filter(Q(title__unaccent__icontains=keyword) |
                                 Q(user__full_name__unaccent__icontains=keyword) |
                                 Q(content__unaccent__icontains=keyword)).select_related('user',
                                                                                         'audio').prefetch_related(
            'tagged_users', 'file', 'hide_by').exclude(hide_by=request.user)
        serializer = BlogSerializer(qs, many=True, context={'request': request})
        return serializer.data, "Danh sách bài viết", status.HTTP_200_OK


class HideBlogAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        blog = Blog.objects.get(id=pk)
        blog.add_hide_by(request.user)
        return f"{blog.hide_by.values_list('full_name', flat=True)}", "Ẩn bài viết thành công", status.HTTP_200_OK
