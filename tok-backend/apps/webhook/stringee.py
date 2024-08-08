from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.services.telegram import logging
from apps.user.models import CustomUser


class StringeeAPIView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request):
        from_user = request.query_params.get('from')
        to_user = request.query_params.get('to')
        user_id = request.query_params.get('userId')
        project_id = request.query_params.get('projectId')
        call_id = request.query_params.get('callId')
        custom_data = request.query_params.get('custom')
        try:
            display_user1 = CustomUser.objects.get(id=from_user).full_name
            display_user2 = CustomUser.objects.get(id=to_user).full_name
        except Exception as e:
            logging(f'Error when get user', e)
            display_user1 = None
            display_user2 = None
        stringee_data = [{
            "action": "connect",
            "from": {
                "type": "internal",
                "number": from_user,
                "alias": display_user1
            },
            "to": {
                "type": "internal",
                "number": to_user,
                "alias": display_user2,
            },
            "customData": custom_data
        }]
        # logging(f'Return response to Stringee: {stringee_data}')

        return Response(stringee_data, status=status.HTTP_200_OK)

