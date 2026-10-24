# ADR-001: Cancel published events instead of deleting them

- Status: Accepted
- Date: 2026-10-24
- Issue: TIC-7

## Context

`Event` owns its `TicketTier` and `EventSeat` rows through `on_delete=CASCADE`, so `event.delete()` removes the event's prices and its whole seat inventory. In Phase 2, orders, tickets and payments will point at that inventory. Deleting a published event would then wipe, or be blocked by, the sales history that refunds, accounting and support depend on.

## Decision

- A `draft` event may be hard-deleted. Nothing has been sold, so there is no history to keep.
- Once an event is `published`, it is never hard-deleted. To call it off, set `status` to `cancelled`.
- A `Venue` that has events can't be deleted (`Event.venue` is `on_delete=PROTECT`).

## Consequences

- For now this rule is a convention. No API or admin action exists yet that could break it. The first code that exposes event deletion (the Event API or admin) must enforce it, for example by allowing `DELETE` only on drafts.
- Listings and reports must filter on `status` instead of assuming that every row is live.
