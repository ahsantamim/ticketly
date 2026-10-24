from django.db import models
from django.db.models import F, Q

from venues.models import Venue


# Module level, not nested in Event, so Meta.constraints can reference it.
class EventStatus(models.TextChoices):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Event(models.Model):
    # PROTECT: a venue with events can't be deleted; events carry sales history.
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(ends_at__gt=F("starts_at")), name="event_ends_after_starts"
            ),
            # choices are only checked by forms/serializers, so enforce them in the DB too.
            models.CheckConstraint(
                condition=Q(status__in=EventStatus.values), name="event_status_valid"
            ),
        ]
        indexes = [
            models.Index(fields=["status", "starts_at"], name="event_status_starts_idx"),
            models.Index(fields=["venue", "starts_at"], name="event_venue_starts_idx"),
        ]

    def __str__(self):
        return self.title


class TicketTier(models.Model):
    # No capacity column: for reserved seating it's the count of EventSeat rows on this tier.
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tiers")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(price__gte=0), name="tier_price_non_negative"),
            models.UniqueConstraint(fields=["event", "name"], name="tier_unique_name_per_event"),
        ]

    def __str__(self):
        return f"{self.event} / {self.name}"
