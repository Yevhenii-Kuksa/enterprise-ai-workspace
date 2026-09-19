from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.demo.ids import (
    ANNA_KOWALSKA_ID,
    EWA_LEWANDOWSKA_ID,
    KAROLINA_WOJCIK_ID,
    KRZYSZTOF_MAZUR_ID,
    PIOTR_NOWAK_ID,
    TOMASZ_WISNIEWSKI_ID,
)


@dataclass(frozen=True, slots=True)
class DemoCalendarEvent:
    event_id: str
    title: str
    starts_at: datetime
    ends_at: datetime
    organizer_user_id: UUID
    attendee_user_ids: tuple[UUID, ...]
    location: str
    description: str


NEXALVORA_CALENDAR_EVENTS = (
    DemoCalendarEvent(
        event_id="CAL-2026-0919-001",
        title="Przegląd ryzyka ORD-1048",
        starts_at=datetime(
            2026,
            9,
            19,
            11,
            0,
            tzinfo=UTC,
        ),
        ends_at=datetime(
            2026,
            9,
            19,
            11,
            30,
            tzinfo=UTC,
        ),
        organizer_user_id=ANNA_KOWALSKA_ID,
        attendee_user_ids=(
            PIOTR_NOWAK_ID,
            KRZYSZTOF_MAZUR_ID,
            EWA_LEWANDOWSKA_ID,
        ),
        location="Sala operacyjna / Teams",
        description=(
            "Przegląd ryzyka dla ORD-1048: dostępność MAT-204, "
            "harmonogram produkcji, kontrola jakości i termin wysyłki."
        ),
    ),
    DemoCalendarEvent(
        event_id="CAL-2026-0921-001",
        title="Odbiór pierwszej partii MAT-204",
        starts_at=datetime(
            2026,
            9,
            21,
            8,
            0,
            tzinfo=UTC,
        ),
        ends_at=datetime(
            2026,
            9,
            21,
            9,
            0,
            tzinfo=UTC,
        ),
        organizer_user_id=PIOTR_NOWAK_ID,
        attendee_user_ids=(
            KRZYSZTOF_MAZUR_ID,
        ),
        location="Magazyn główny",
        description=(
            "Planowany odbiór pierwszej partii 200 m² materiału MAT-204 "
            "dla PO-2026-0914."
        ),
    ),
    DemoCalendarEvent(
        event_id="CAL-2026-0922-001",
        title="Kontrola gotowości produkcyjnej ORD-1048",
        starts_at=datetime(
            2026,
            9,
            22,
            13,
            0,
            tzinfo=UTC,
        ),
        ends_at=datetime(
            2026,
            9,
            22,
            13,
            30,
            tzinfo=UTC,
        ),
        organizer_user_id=KRZYSZTOF_MAZUR_ID,
        attendee_user_ids=(
            ANNA_KOWALSKA_ID,
            EWA_LEWANDOWSKA_ID,
        ),
        location="Production Floor A",
        description=(
            "Potwierdzenie gotowości modułów NX-Mod Technical "
            "przed planowaną wysyłką ORD-1048."
        ),
    ),
    DemoCalendarEvent(
        event_id="CAL-2026-0923-001",
        title="Potwierdzenie dostawy ORD-1048 z klientem",
        starts_at=datetime(
            2026,
            9,
            23,
            7,
            30,
            tzinfo=UTC,
        ),
        ends_at=datetime(
            2026,
            9,
            23,
            8,
            0,
            tzinfo=UTC,
        ),
        organizer_user_id=KAROLINA_WOJCIK_ID,
        attendee_user_ids=(
            TOMASZ_WISNIEWSKI_ID,
            EWA_LEWANDOWSKA_ID,
        ),
        location="Teams",
        description=(
            "Potwierdzenie statusu dostawy 24 modułów NX-Mod Technical "
            "dla Baltic Construction Group."
        ),
    ),
)