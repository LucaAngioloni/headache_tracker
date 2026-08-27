from django.conf import settings
from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import EpisodeFilter
from .models import Episode, Medicine, Trigger
from .serializers import EpisodeSerializer, MedicineSerializer, MeSerializer, TriggerSerializer
from .stats import compute_stats


class UserScopedMixin:
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MeView(APIView):
    def get(self, request):
        return Response(MeSerializer(request.user).data)


class VersionView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response({"version": settings.VERSION})


class MedicineViewSet(UserScopedMixin, viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    search_fields = ("name", "active_ingredient")
    ordering_fields = ("name", "id")

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "medicine in use"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TriggerViewSet(UserScopedMixin, viewsets.ModelViewSet):
    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "id")


class EpisodeViewSet(UserScopedMixin, viewsets.ModelViewSet):
    queryset = Episode.objects.prefetch_related("doses__medicine", "triggers").all()
    serializer_class = EpisodeSerializer
    filterset_class = EpisodeFilter
    search_fields = ("notes",)
    ordering_fields = ("occurred_on", "pain_level", "id")


class StatsView(APIView):
    def get(self, request):
        return Response(compute_stats(request.user, request.query_params))
