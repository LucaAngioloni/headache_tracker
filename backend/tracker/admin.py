from django.contrib import admin

from .models import Dose, Episode, Medicine, Trigger


class DoseInline(admin.TabularInline):
    model = Dose
    extra = 0


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "active_ingredient", "unit", "user")
    list_filter = ("user",)
    search_fields = ("name", "active_ingredient")


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    list_filter = ("user",)
    search_fields = ("name",)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("occurred_on", "pain_level", "user")
    list_filter = ("user", "occurred_on")
    search_fields = ("notes",)
    inlines = [DoseInline]


@admin.register(Dose)
class DoseAdmin(admin.ModelAdmin):
    list_display = ("episode", "medicine", "quantity")
    list_filter = ("medicine",)
