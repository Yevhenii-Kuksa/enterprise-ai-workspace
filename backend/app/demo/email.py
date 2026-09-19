from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.demo.ids import (
    ANNA_KOWALSKA_ID,
    BUILDCORE_MATERIALS_ID,
    KAROLINA_WOJCIK_ID,
    PIOTR_NOWAK_ID,
)


@dataclass(frozen=True, slots=True)
class DemoEmailMessage:
    message_id: str
    sent_at: datetime
    sender_name: str
    sender_address: str
    recipient_user_id: UUID
    subject: str
    body: str
    thread_key: str


NEXALVORA_EMAIL_MESSAGES = (
    DemoEmailMessage(
        message_id="MSG-2026-0919-001",
        sent_at=datetime(
            2026,
            9,
            19,
            8,
            12,
            tzinfo=UTC,
        ),
        sender_name="BuildCore Materials Sp. z o.o.",
        sender_address="logistics@buildcore.example",
        recipient_user_id=PIOTR_NOWAK_ID,
        subject="Aktualizacja dostawy MAT-204 / PO-2026-0914",
        body=(
            "Informujemy o zmianie harmonogramu dostawy dla zamówienia "
            "PO-2026-0914. Pierwsza partia 200 m² MAT-204 zostanie "
            "dostarczona 21.09.2026. Pozostałe 200 m² planujemy dostarczyć "
            "25.09.2026. Przepraszamy za opóźnienie i prosimy o potwierdzenie "
            "otrzymania informacji."
        ),
        thread_key="PO-2026-0914",
    ),
    DemoEmailMessage(
        message_id="MSG-2026-0919-002",
        sent_at=datetime(
            2026,
            9,
            19,
            9,
            5,
            tzinfo=UTC,
        ),
        sender_name="Krzysztof Mazur",
        sender_address="krzysztof.mazur@nexalvora.example",
        recipient_user_id=ANNA_KOWALSKA_ID,
        subject="ORD-1048 — ryzyko terminu produkcji",
        body=(
            "Dla ORD-1048 mamy obecnie 180 m² MAT-204 przy zapotrzebowaniu "
            "260 m². Pierwsza opóźniona dostawa ma dotrzeć 21.09.2026. "
            "Przy planowanej wysyłce 23.09.2026 pozostaje bardzo mały bufor "
            "na przyjęcie materiału, produkcję i kontrolę jakości."
        ),
        thread_key="ORD-1048",
    ),
    DemoEmailMessage(
        message_id="MSG-2026-0919-003",
        sent_at=datetime(
            2026,
            9,
            19,
            10,
            18,
            tzinfo=UTC,
        ),
        sender_name="Baltic Construction Group Sp. z o.o.",
        sender_address="project@balticconstruction.example",
        recipient_user_id=KAROLINA_WOJCIK_ID,
        subject="Potwierdzenie terminu dostawy ORD-1048",
        body=(
            "Prosimy o potwierdzenie, że dostawa 24 modułów NX-Mod Technical "
            "dla Warsaw Logistics Center — Building B pozostaje aktualna "
            "na 23.09.2026. Termin jest istotny dla dalszego harmonogramu prac "
            "na budowie."
        ),
        thread_key="ORD-1048",
    ),
)


BUILDCORE_EMAIL_SENDER_ID = BUILDCORE_MATERIALS_ID