from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..serializers.garbage import GarbageSerializer
from garbage.models import Garbage

@api_view(['POST'])
def save(request):
    serializer = GarbageSerializer(data=request.data)

    if serializer.is_valid():
        if Garbage.objects.count() > 0:
            Garbage.objects.all().delete()
        serializer.save()
        return Response({"message": "Datos recibidos correctamente", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get(request):
    if Garbage.objects.count() == 0:
        return Response({"message": "No hay datos disponibles"}, status=status.HTTP_404_NOT_FOUND)
    else:
        last_entry = Garbage.objects.latest('id')
        serializer = GarbageSerializer(last_entry)
        return Response(serializer.data, status=status.HTTP_200_OK)