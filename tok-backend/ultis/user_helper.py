from math import radians, sin, cos, atan2, sqrt

from django.db.models import Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from apps.user.models import BaseInformation


def haversine(lat1, lon1, lat2, lon2):
    # Chuyển đổi độ sang radian
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Tính toán chênh lệch giữa các vị trí địa lý
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Đường kính của Trái Đất (đơn vị: km)
    R = 6371.0

    # Tính khoảng cách
    distance = R * c

    return round(distance,2)


def get_list_interest(base_info):
    # Khởi tạo danh sách để lưu trữ các tiêu đề
    title_list = []

    # Lấy tiêu đề từ mỗi mô hình thông tin và thêm vào danh sách
    work_titles = list(base_info.work.all().values_list('title', flat=True))
    title_list.extend(work_titles)

    character_titles = list(base_info.character.all().values_list('title', flat=True))
    title_list.extend(character_titles)

    search_titles = list(base_info.search.all().values_list('title', flat=True))
    title_list.extend(search_titles)

    hobby_titles = list(base_info.hobby.all().values_list('title', flat=True))
    title_list.extend(hobby_titles)

    communicate_titles = list(base_info.communicate.all().values_list('title', flat=True))
    title_list.extend(communicate_titles)

    return title_list


# def get_similar_profiles(users, user):
#     # Lấy tất cả các hồ sơ người dùng
#     all_profiles = BaseInformation.objects.filter(Q(user__in=users) | Q(user=user))
#
#     # Lấy danh sách tất cả các sở thích
#     all_interests = []
#     for profile in all_profiles:
#         interests = get_list_interest(profile)
#         all_interests.append(' '.join(interests))
#
#     tfidf_vectorizer = TfidfVectorizer()
#     tfidf_matrix = tfidf_vectorizer.fit_transform(all_interests)
#
#     # Tính toán sự tương tự giữa các hồ sơ dựa trên ma trận TF-IDF
#     cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
#
#     # Lấy chỉ số của người dùng hiện tại trong ma trận tương tự
#     user_index = all_profiles.filter(user=user).first()
#
#     # Lấy chỉ số của người dùng hiện tại trong danh sách all_profiles
#     user_index = list(all_profiles).index(user_index)
#
#     # Lấy các chỉ số của các hồ sơ tương tự
#     similar_profile_indices = cosine_similarities[user_index].argsort()[:-5:-1]
#     similar_profile_indices = list(similar_profile_indices.astype(int))
#     # Lấy danh sách các CustomUser tương tự
#     similar_users = [all_profiles[int(i)].user for i in similar_profile_indices if all_profiles[int(i)].user != user]
#     return similar_users



