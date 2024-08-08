from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class AppotaPayAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        data_return = request.query_params.dict()
        data = request.query_params.get('data', None)
        signature = request.query_params.get('signature', None)
        time = request.query_params.get('time', None)
        return Response(data_return, status=status.HTTP_200_OK)

    def post(self,request):
        data = request.query_params.get('data', None)
        signature = request.query_params.get('signature', None)
        time = request.query_params.get('time', None)
        pass