from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EpisodeViewSet, MedicineViewSet, StatsView, TriggerViewSet

router = DefaultRouter()
router.register("medicines", MedicineViewSet, basename="medicine")
router.register("triggers", TriggerViewSet, basename="trigger")
router.register("episodes", EpisodeViewSet, basename="episode")

urlpatterns = [
    path("stats/", StatsView.as_view(), name="stats"),
    path("", include(router.urls)),
]
