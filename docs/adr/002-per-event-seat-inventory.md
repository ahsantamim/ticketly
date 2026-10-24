# ADR-002: Per-event seat inventory as one row per (event, seat)

- Status: Accepted
- Date: 2026-10-24
- Issue: TIC-7 (ERD and lead review are in the issue's comments)

## Context

Phase 2 adds holds and orders and must never oversell a seat. The schema has to make that guarantee cheap and concurrent.

## Decision

`events.EventSeat` has one row per (event, seat), pointing at the `TicketTier` that prices it. Its `status` is `available`, `held` or `sold`, and `hold_expires_at` is set exactly when the status is `held`.

- **No oversell, enforced by the database.** `UNIQUE (event_id, seat_id)` makes a double listing impossible. Claiming seats is a single conditional `UPDATE ... SET status = 'held' WHERE id IN (...) AND status = 'available'`. If fewer rows are updated than were requested, someone else got there first, and the transaction rolls back.
- **Concurrency.** Buyers lock different rows (`SELECT ... FOR UPDATE SKIP LOCKED`) instead of all contending for one counter on the tier.
- **Cost.** Rows = seats × events. 20k seats × 100 events = 2M narrow rows, which is fine for Postgres.

Rejected alternatives:

- **A sold/held counter on `TicketTier`.** It can't say which seat was bought, and the counter row becomes a lock hotspot.
- **Deriving availability from order/ticket rows.** Holds would still need their own table, and "what's free?" becomes an anti-join.

### Tier capacity is derived, not stored

`TicketTier` has no `capacity` column. For reserved seating, a tier's capacity is the number of `EventSeat` rows that point at it. Storing it as well would create a second source of truth that can disagree with the rows, for example by showing "20 left" when no row is available. If general admission is added later, give the tier a `kind` and a nullable `capacity`, with `CHECK ((kind = 'ga') = (capacity IS NOT NULL))`.

### Cross-table consistency is enforced in the service, for now

Two invariants aren't covered by plain foreign keys:

- `event_seat.seat.venue` must equal `event_seat.event.venue`.
- `event_seat.tier.event` must equal `event_seat.event`.

The inventory-generation service, which will be the only code that writes `EventSeat` rows, enforces both, and tests cover them. If a second write path appears, upgrade to composite foreign keys, for example `(tier_id, event_id) REFERENCES ticket_tier (id, event_id)` backed by `UNIQUE (id, event_id)`, added with a Postgres-only `RunSQL` migration.

### Deletes

- Event → TicketTier and Event → EventSeat: `CASCADE`. Drafts can be cleaned up in one call (see ADR-001 for published events).
- Seat → EventSeat and TicketTier → EventSeat: `RESTRICT`, not `PROTECT`. Both block deleting a seat or tier that has inventory. Only `RESTRICT` lets `event.delete()` go through, because those `EventSeat` rows are also being deleted through the cascade from `Event`. `RESTRICT` is a Django-side rule. The database foreign keys are `NO ACTION`, so raw SQL still can't leave orphan rows.
