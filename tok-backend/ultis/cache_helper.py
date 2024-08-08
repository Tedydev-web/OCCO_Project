from django.db.models import Q

from apps.user.models import CustomUser, FriendShip
from apps.user.serializers import FriendShipSerializer
from ultis.user_helper import haversine


def check_update_user_cache_different(current_cache, request_user, user2):
    # Chk block
    current_block = CustomUser.custom_objects.is_block(request_user, user2)

    if current_block != current_cache['block_status']:
        current_cache['block_status'] = current_block

    # Chk distance
    try:
        current_distance = haversine(request_user.lat,
                                     request_user.lng,
                                     user2.lat,
                                     user2.lng)
    except Exception as e:
        current_distance = None

    if current_distance != current_cache['distance']:
        current_cache['distance'] = current_distance

    try:
        current_cache['distance'] = haversine(lat1=request_user.lat,
                                              lat2=user2.lat,
                                              lon1=request_user.lng,
                                              lon2=user2.lng)
    except Exception as e:
        current_cache['distance'] = None

    try:
        current_cache['friend'] = True if str(user2.id) in request_user.social['friends'] else False
    except:
        current_cache['friend'] = False
    try:
        current_cache['friend_request'] = True if str(user2.id) in request_user.social['friend_request'] else False
    except:
        current_cache['friend_request'] = False
    try:
        current_cache['friend_accept'] = True if str(request_user.id) in user2.social['friend_request'] else False
    except:
        current_cache['friend_accept'] = False

    try:
        current_cache['follow'] = True if str(user2.id) in request_user.social['following'] else False
    except:
        current_cache['follow'] = False

    return current_cache
