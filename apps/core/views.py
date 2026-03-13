from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.academics.models import School
from .serializers import SchoolSerializer

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def schools(request):
    schools = School.objects.prefetch_related("departments").all()
    serializer = SchoolSerializer(schools, many=True)
    return Response(serializer.data)