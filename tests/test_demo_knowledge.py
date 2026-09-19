from app.demo.ids import PROD_W38_DOCUMENT_ID, TECH_12_DOCUMENT_ID
from app.demo.knowledge import NEXALVORA_KNOWLEDGE_DOCUMENTS
from app.demo.knowledge_content import NEXALVORA_KNOWLEDGE_CONTENT


def test_knowledge_document_codes_are_unique() -> None:
    codes = [
        document.document_code
        for document in NEXALVORA_KNOWLEDGE_DOCUMENTS
    ]

    assert len(codes) == len(set(codes))


def test_knowledge_document_ids_are_unique() -> None:
    document_ids = [
        document.id
        for document in NEXALVORA_KNOWLEDGE_DOCUMENTS
    ]

    assert len(document_ids) == len(set(document_ids))


def test_expected_number_of_knowledge_documents() -> None:
    assert len(NEXALVORA_KNOWLEDGE_DOCUMENTS) == 10


def test_all_knowledge_documents_have_rag_content() -> None:
    document_ids = {
        document.id
        for document in NEXALVORA_KNOWLEDGE_DOCUMENTS
    }

    assert document_ids == set(NEXALVORA_KNOWLEDGE_CONTENT)


def test_all_rag_content_is_non_empty() -> None:
    assert all(
        content.strip()
        for content in NEXALVORA_KNOWLEDGE_CONTENT.values()
    )


def test_production_plan_contains_main_order_story() -> None:
    content = NEXALVORA_KNOWLEDGE_CONTENT[PROD_W38_DOCUMENT_ID]

    assert "ORD-1048" in content
    assert "23.09.2026" in content
    assert "MAT-204" in content


def test_technical_document_contains_product_and_material() -> None:
    content = NEXALVORA_KNOWLEDGE_CONTENT[TECH_12_DOCUMENT_ID]

    assert "NX-Mod Technical" in content
    assert "MAT-204" in content