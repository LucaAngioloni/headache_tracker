from rest_framework import serializers

from .models import Dose, Episode, Medicine, Trigger


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ("id", "name", "active_ingredient", "unit")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = ("id", "name")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class DoseSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    medicine_unit = serializers.CharField(source="medicine.unit", read_only=True)

    class Meta:
        model = Dose
        fields = (
            "id",
            "medicine",
            "medicine_name",
            "medicine_unit",
            "quantity",
            "note",
            "sort_order",
        )


class EpisodeSerializer(serializers.ModelSerializer):
    doses = DoseSerializer(many=True)
    trigger_ids = serializers.PrimaryKeyRelatedField(
        source="triggers",
        many=True,
        queryset=Trigger.objects.all(),
        required=False,
    )
    triggers = TriggerSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = (
            "id",
            "occurred_on",
            "pain_level",
            "notes",
            "trigger_ids",
            "triggers",
            "doses",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate_pain_level(self, value):
        if value is not None and not 1 <= value <= 10:
            raise serializers.ValidationError("Pain level must be between 1 and 10.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        triggers = attrs.get("triggers")
        if triggers is not None:
            foreign = [t.id for t in triggers if t.user_id != user.id]
            if foreign:
                raise serializers.ValidationError(
                    {"trigger_ids": "Triggers must belong to the current user."}
                )
        return attrs

    def validate_doses(self, doses):
        if self.instance is None and not doses:
            raise serializers.ValidationError("At least one dose is required.")
        request = self.context["request"]
        user = request.user
        for dose in doses:
            medicine = dose.get("medicine")
            if medicine and medicine.user_id != user.id:
                raise serializers.ValidationError("Medicines must belong to the current user.")
        return doses

    def create(self, validated_data):
        doses_data = validated_data.pop("doses")
        triggers = validated_data.pop("triggers", [])
        validated_data["user"] = self.context["request"].user
        episode = Episode.objects.create(**validated_data)
        if triggers:
            episode.triggers.set(triggers)
        self._replace_doses(episode, doses_data)
        return episode

    def update(self, instance, validated_data):
        doses_data = validated_data.pop("doses", None)
        triggers = validated_data.pop("triggers", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if triggers is not None:
            instance.triggers.set(triggers)
        if doses_data is not None:
            if not doses_data:
                raise serializers.ValidationError({"doses": "At least one dose is required."})
            instance.doses.all().delete()
            self._replace_doses(instance, doses_data)
        return instance

    def _replace_doses(self, episode, doses_data):
        for index, dose in enumerate(doses_data):
            Dose.objects.create(
                episode=episode,
                medicine=dose["medicine"],
                quantity=dose.get("quantity", 1),
                note=dose.get("note", ""),
                sort_order=dose.get("sort_order", index),
            )


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
