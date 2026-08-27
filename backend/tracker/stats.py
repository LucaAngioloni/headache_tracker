from __future__ import annotations

from collections import defaultdict
from datetime import date
from math import ceil
from statistics import median

from django.db.models import Prefetch
from django.utils import timezone

from .models import Dose, Episode


def _today() -> date:
    return timezone.localdate()


def default_range(qs) -> tuple[date, date]:
    """From the first episode in the queryset to today. Today only if no episodes."""
    end = _today()
    first = qs.order_by("occurred_on").values_list("occurred_on", flat=True).first()
    start = first if first is not None else end
    return start, end


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def apply_episode_filters(qs, params):
    date_after = parse_date(params.get("date_after"))
    date_before = parse_date(params.get("date_before"))
    if date_after is None and date_before is None:
        date_after, date_before = default_range(qs)
    if date_after:
        qs = qs.filter(occurred_on__gte=date_after)
    if date_before:
        qs = qs.filter(occurred_on__lte=date_before)

    medicine = params.get("medicine")
    if medicine:
        qs = qs.filter(doses__medicine_id=medicine)
    trigger = params.get("trigger")
    if trigger:
        qs = qs.filter(triggers__id=trigger)
    pain_min = params.get("pain_min")
    if pain_min not in (None, ""):
        qs = qs.filter(pain_level__gte=int(pain_min))
    pain_max = params.get("pain_max")
    if pain_max not in (None, ""):
        qs = qs.filter(pain_level__lte=int(pain_max))
    search = params.get("search")
    if search:
        qs = qs.filter(notes__icontains=search)
    return qs.distinct(), date_after, date_before


def current_streak_days(user) -> int:
    """Days from the first unfiltered episode to today (Europe/Rome). 0 if no episodes."""
    today = _today()
    first = (
        Episode.objects.filter(user=user, occurred_on__lte=today)
        .order_by("occurred_on")
        .values_list("occurred_on", flat=True)
        .first()
    )
    if first is None:
        return 0
    return (today - first).days


def longest_streak_days(dates: list[date], range_start: date | None, range_end: date | None) -> int:
    """Longest gap between consecutive episode dates inside the filtered range."""
    if range_start is None or range_end is None or not dates:
        return 0
    unique = sorted(set(dates))
    gaps = []
    gaps.append((unique[0] - range_start).days)
    for prev, nxt in zip(unique, unique[1:], strict=False):
        gaps.append((nxt - prev).days - 1)
    gaps.append((range_end - unique[-1]).days)
    return max(0, max(gaps))


def iso_week(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def months_between(start: date, end: date) -> int:
    """Number of calendar months covered by [start, end], inclusive."""
    return (end.year - start.year) * 12 + (end.month - start.month) + 1


def weeks_in_range(start: date, end: date) -> int:
    """Number of weeks covered by [start, end], rounded up, at least 1."""
    return max(1, ceil((end - start).days / 7))


def compute_stats(user, params) -> dict:
    """
    KPI + series for the authenticated user.

    Default date range is from the first episode to today when date_after/date_before
    are omitted. current_headache_free_streak_days uses the unfiltered user calendar
    (days from the first episode to today, Europe/Rome).
    longest_headache_free_streak_days is computed inside the filtered range.
    avg_episodes_per_month / avg_episodes_per_week are computed over the effective range.
    """
    base = Episode.objects.filter(user=user)
    filtered, date_after, date_before = apply_episode_filters(
        base.prefetch_related(
            Prefetch("doses", queryset=Dose.objects.select_related("medicine")),
            "triggers",
        ),
        params,
    )
    episodes = list(filtered.order_by("occurred_on"))
    count = len(episodes)
    pains = [e.pain_level for e in episodes if e.pain_level is not None]
    dates = [e.occurred_on for e in episodes]

    avg_pain = round(sum(pains) / len(pains), 2) if pains else None
    median_pain = float(median(pains)) if pains else None

    avg_days_between = None
    unique_dates = sorted(set(dates))
    if len(unique_dates) >= 2:
        spans = [(b - a).days for a, b in zip(unique_dates, unique_dates[1:], strict=False)]
        avg_days_between = round(sum(spans) / len(spans), 2)

    multi_dose = sum(1 for e in episodes if e.doses.count() >= 2)
    second_dose_rate = round(multi_dose / count, 4) if count else 0

    avg_episodes_per_month = (
        round(count / months_between(date_after, date_before), 2) if count else 0
    )
    avg_episodes_per_week = (
        round(count / weeks_in_range(date_after, date_before), 2) if count else 0
    )

    by_month: dict[str, int] = defaultdict(int)
    by_week: dict[str, int] = defaultdict(int)
    for e in episodes:
        by_month[e.occurred_on.strftime("%Y-%m")] += 1
        by_week[iso_week(e.occurred_on)] += 1

    med_stats: dict[int, dict] = {}
    for e in episodes:
        seen = set()
        for dose in e.doses.all():
            entry = med_stats.setdefault(
                dose.medicine_id,
                {
                    "id": dose.medicine_id,
                    "name": dose.medicine.name,
                    "dose_count": 0,
                    "episode_count": 0,
                },
            )
            entry["dose_count"] += 1
            if dose.medicine_id not in seen:
                entry["episode_count"] += 1
                seen.add(dose.medicine_id)

    trig_stats: dict[int, dict] = {}
    for e in episodes:
        for trigger in e.triggers.all():
            entry = trig_stats.setdefault(
                trigger.id,
                {"id": trigger.id, "name": trigger.name, "episode_count": 0},
            )
            entry["episode_count"] += 1

    medicines = []
    for row in med_stats.values():
        row["pct"] = round(row["episode_count"] / count, 4) if count else 0
        medicines.append(row)
    medicines.sort(key=lambda r: (-r["episode_count"], r["name"]))

    triggers = []
    for row in trig_stats.values():
        row["pct"] = round(row["episode_count"] / count, 4) if count else 0
        triggers.append(row)
    triggers.sort(key=lambda r: (-r["episode_count"], r["name"]))

    echo = {
        "date_after": date_after.isoformat() if date_after else None,
        "date_before": date_before.isoformat() if date_before else None,
        "medicine": params.get("medicine") or None,
        "trigger": params.get("trigger") or None,
        "pain_min": params.get("pain_min") or None,
        "pain_max": params.get("pain_max") or None,
        "search": params.get("search") or None,
    }

    return {
        "filters": echo,
        "episode_count": count,
        "avg_pain": avg_pain,
        "median_pain": median_pain,
        "avg_days_between": avg_days_between,
        "avg_episodes_per_month": avg_episodes_per_month,
        "avg_episodes_per_week": avg_episodes_per_week,
        "current_headache_free_streak_days": current_streak_days(user),
        "longest_headache_free_streak_days": longest_streak_days(dates, date_after, date_before),
        "second_dose_rate": second_dose_rate,
        "episodes_by_month": [
            {"month": month, "count": by_month[month]} for month in sorted(by_month)
        ],
        "episodes_by_week": [{"week": week, "count": by_week[week]} for week in sorted(by_week)],
        "medicines": medicines,
        "triggers": triggers,
    }
