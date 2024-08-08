
from api.services.agora.RtcTokenBuilder2 import RtcTokenBuilder, Role_Subscriber, Role_Publisher
from core.settings import AGORA_APP_CERTIFICATE, AGORA_APP_ID


def get_token_publisher(live_id, user_id):
    app_id = AGORA_APP_ID
    app_certificate = AGORA_APP_CERTIFICATE
    # Replace channelName with the name of the channel you want to join
    channel_name = live_id
    # Fill in your actual user ID
    uid = ''
    # Token validity time in seconds
    token_expiration_in_seconds = 3600
    # The validity time of all permissions in seconds
    privilege_expiration_in_seconds = 3600

    print("App Id: %s" % app_id)
    print("App Certificate: %s" % app_certificate)
    if not app_id or not app_certificate:
        print("Need to set environment variable AGORA_APP_ID and AGORA_APP_CERTIFICATE")
        return

    # Generate Token
    token = RtcTokenBuilder.build_token_with_uid(app_id, app_certificate, channel_name, uid, Role_Publisher,
                                                 token_expiration_in_seconds, privilege_expiration_in_seconds)
    print("Token with int uid: {}".format(token))
    return token


def get_token_subscriber(live_id, user_id):
    app_id = AGORA_APP_ID
    app_certificate = AGORA_APP_CERTIFICATE
    # Replace channelName with the name of the channel you want to join
    channel_name = live_id
    # Fill in your actual user ID
    uid = ''
    # Token validity time in seconds
    token_expiration_in_seconds = 3600
    # The validity time of all permissions in seconds
    privilege_expiration_in_seconds = 3600

    print("App Id: %s" % app_id)
    print("App Certificate: %s" % app_certificate)
    if not app_id or not app_certificate:
        print("Need to set environment variable AGORA_APP_ID and AGORA_APP_CERTIFICATE")
        return

    # Generate Token
    token = RtcTokenBuilder.build_token_with_uid(app_id, app_certificate, channel_name, uid, Role_Subscriber,
                                                 token_expiration_in_seconds, privilege_expiration_in_seconds)
    print("Token with int uid: {}".format(token))
    return token

