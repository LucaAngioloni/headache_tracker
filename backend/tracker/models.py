from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Medicine(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="medicines"
    )
    name = models.CharField(max_length=120)
    active_ingredient = models.CharField(max_length=120, blank=True)
    unit = models.CharField(max_length=32, default="cpr")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="uniq_medicine_user_name"),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Trigger(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="triggers"
    )
    name = models.CharField(max_length=120)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="uniq_trigger_user_name"),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Episode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="episodes"
    )
    occurred_on = models.DateField()
    pain_level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    notes = models.TextField(blank=True)
    triggers = models.ManyToManyField(Trigger, blank=True, related_name="episodes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "occurred_on"]),
        ]
        ordering = ["-occurred_on", "-id"]

    def __str__(self) -> str:
        return f"{self.occurred_on} ({self.user})"


class Dose(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="doses")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name="doses")
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    note = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.medicine} x{self.quantity}"
