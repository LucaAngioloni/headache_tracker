from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from tracker.models import Dose, Episode, Medicine, Trigger

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret123")


@pytest.fixture
def other(db):
    return User.objects.create_user(username="bob", password="secret123")


@pytest.fixture
def auth(api, user):
    api.force_authenticate(user=user)
    return api


def create_medicine(user, name="Oki Task"):
    return Medicine.objects.create(user=user, name=name, unit="cpr")


def create_episode(user, medicine, occurred_on=None, pain=5, extra_doses=0):
    occurred_on = occurred_on or date(2026, 1, 10)
    episode = Episode.objects.create(
        user=user, occurred_on=occurred_on, pain_level=pain, notes="test"
    )
    Dose.objects.create(episode=episode, medicine=medicine, quantity=1)
    for i in range(extra_doses):
        Dose.objects.create(
            episode=episode, medicine=medicine, quantity=1, sort_order=i + 1
        )
    return episode


def test_token_login(api, user):
    res = api.post(
        "/api/auth/token/",
        {"username": "alice", "password": "secret123"},
        format="json",
    )
    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data


def test_me(auth, user):
    res = auth.get("/api/me/")
    assert res.status_code == 200
    assert res.data["username"] == "alice"
    assert res.data["id"] == user.id


def test_user_isolation(auth, user, other):
    mine = create_medicine(user, "Oki Task")
    theirs = create_medicine(other, "Synflex")
    create_episode(user, mine)
    create_episode(other, theirs)

    res = auth.get("/api/medicines/")
    names = [row["name"] for row in res.data["results"]]
    assert names == ["Oki Task"]

    res = auth.get("/api/episodes/")
    assert res.data["count"] == 1
    assert auth.get(f"/api/episodes/{Episode.objects.get(user=other).id}/").status_code == 404


def test_nested_episode_write(auth, user):
    med = create_medicine(user)
    trig = Trigger.objects.create(user=user, name="sonno")
    res = auth.post(
        "/api/episodes/",
        {
            "occurred_on": "2026-02-01",
            "pain_level": 7,
            "notes": "pomeriggio",
            "trigger_ids": [trig.id],
            "doses": [{"medicine": med.id, "quantity": "1.00", "note": "prima"}],
        },
        format="json",
    )
    assert res.status_code == 201
    assert res.data["pain_level"] == 7
    assert len(res.data["doses"]) == 1
    assert res.data["doses"][0]["medicine"] == med.id
    assert res.data["triggers"][0]["name"] == "sonno"


def test_episode_requires_dose(auth, user):
    res = auth.post(
        "/api/episodes/",
        {"occurred_on": "2026-02-01", "doses": []},
        format="json",
    )
    assert res.status_code == 400


def test_cannot_use_foreign_medicine(auth, other):
    foreign = create_medicine(other, "Tachicaf")
    res = auth.post(
        "/api/episodes/",
        {
            "occurred_on": "2026-02-01",
            "doses": [{"medicine": foreign.id, "quantity": 1}],
        },
        format="json",
    )
    assert res.status_code == 400


def test_medicine_delete_protected(auth, user):
    med = create_medicine(user)
    create_episode(user, med)
    res = auth.delete(f"/api/medicines/{med.id}/")
    assert res.status_code == 400
    assert med.id and Medicine.objects.filter(id=med.id).exists()


def test_stats_empty(auth):
    res = auth.get("/api/stats/")
    assert res.status_code == 200
    assert res.data["episode_count"] == 0
    assert res.data["avg_pain"] is None
    assert res.data["median_pain"] is None
    assert res.data["second_dose_rate"] == 0


def test_stats_math(auth, user):
    med = create_medicine(user, "Oki Task")
    med2 = create_medicine(user, "Synflex")
    trig = Trigger.objects.create(user=user, name="vino")
    today = timezone.localdate()
    e1 = create_episode(user, med, occurred_on=today - timedelta(days=10), pain=4)
    e1.triggers.add(trig)
    e2 = create_episode(
        user, med, occurred_on=today - timedelta(days=4), pain=8, extra_doses=1
    )
    Dose.objects.create(episode=e2, medicine=med2, quantity=1, sort_order=2)

    res = auth.get(
        "/api/stats/",
        {"date_after": (today - timedelta(days=30)).isoformat(), "date_before": today.isoformat()},
    )
    data = res.data
    assert data["episode_count"] == 2
    assert data["avg_pain"] == 6.0
    assert data["median_pain"] == 6.0
    assert data["avg_days_between"] == 6.0
    assert data["current_headache_free_streak_days"] == 4
    assert data["second_dose_rate"] == 0.5
    names = {row["name"]: row for row in data["medicines"]}
    assert names["Oki Task"]["episode_count"] == 2
    assert names["Synflex"]["episode_count"] == 1
    assert data["triggers"][0]["name"] == "vino"
    assert data["longest_headache_free_streak_days"] >= 0
