import django_filters

from .models import Episode


class EpisodeFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(field_name="occurred_on", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="occurred_on", lookup_expr="lte")
    medicine = django_filters.NumberFilter(field_name="doses__medicine_id", distinct=True)
    trigger = django_filters.NumberFilter(field_name="triggers__id", distinct=True)
    pain_min = django_filters.NumberFilter(field_name="pain_level", lookup_expr="gte")
    pain_max = django_filters.NumberFilter(field_name="pain_level", lookup_expr="lte")

    class Meta:
        model = Episode
        fields = (
            "date_after",
            "date_before",
            "medicine",
            "trigger",
            "pain_min",
            "pain_max",
        )
