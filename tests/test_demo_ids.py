import uuid

from app.demo.ids import (
    ANNA_KOWALSKA_ID,
    NEXALVORA_ORGANIZATION_ID,
    ORD_1048_ID,
    demo_uuid,
)


def test_demo_uuid_is_deterministic() -> None:
    first = demo_uuid("order:ORD-1048")
    second = demo_uuid("order:ORD-1048")

    assert first == second
    assert first == ORD_1048_ID


def test_demo_uuid_returns_uuid_instance() -> None:
    assert isinstance(NEXALVORA_ORGANIZATION_ID, uuid.UUID)
    assert isinstance(ANNA_KOWALSKA_ID, uuid.UUID)
    assert isinstance(ORD_1048_ID, uuid.UUID)


def test_different_demo_keys_produce_different_ids() -> None:
    assert NEXALVORA_ORGANIZATION_ID != ANNA_KOWALSKA_ID
    assert ANNA_KOWALSKA_ID != ORD_1048_ID
    assert NEXALVORA_ORGANIZATION_ID != ORD_1048_ID