from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class Alive(APIView):
    """Alive
    """
    def get(self, request):
        response = Response({"message":"hello world"}, status=status.HTTP_200_OK)
        return response

class Resultados(APIView):
    """Api resultado
    """

