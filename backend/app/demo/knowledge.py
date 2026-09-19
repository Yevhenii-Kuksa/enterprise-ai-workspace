from dataclasses import dataclass
from uuid import UUID

from app.demo.ids import (
    BHP_02_DOCUMENT_ID,
    FIRE_03_DOCUMENT_ID,
    LOG_05_DOCUMENT_ID,
    PROC_07_DOCUMENT_ID,
    PROD_W38_DOCUMENT_ID,
    PUR_02_DOCUMENT_ID,
    QMS_04_DOCUMENT_ID,
    SALES_03_DOCUMENT_ID,
    SUP_01_DOCUMENT_ID,
    TECH_12_DOCUMENT_ID,
)


@dataclass(frozen=True, slots=True)
class DemoKnowledgeDocument:
    id: UUID
    document_code: str
    title: str
    category: str
    language: str
    version: str


NEXALVORA_KNOWLEDGE_DOCUMENTS = (
    DemoKnowledgeDocument(
        id=QMS_04_DOCUMENT_ID,
        document_code="QMS-04",
        title="Procedura kontroli jakości prefabrykatów",
        category="Quality",
        language="pl",
        version="4.2",
    ),
    DemoKnowledgeDocument(
        id=BHP_02_DOCUMENT_ID,
        document_code="BHP-02",
        title="Zasady bezpieczeństwa produkcji i montażu",
        category="Safety",
        language="pl",
        version="2.1",
    ),
    DemoKnowledgeDocument(
        id=PROC_07_DOCUMENT_ID,
        document_code="PROC-07",
        title="Procedura odbioru materiałów",
        category="Procurement",
        language="pl",
        version="3.0",
    ),
    DemoKnowledgeDocument(
        id=TECH_12_DOCUMENT_ID,
        document_code="TECH-12",
        title="Specyfikacja techniczna NX-Mod Technical",
        category="Technical",
        language="pl",
        version="12.3",
    ),
    DemoKnowledgeDocument(
        id=FIRE_03_DOCUMENT_ID,
        document_code="FIRE-03",
        title="Wymagania odporności ogniowej",
        category="Compliance",
        language="pl",
        version="3.4",
    ),
    DemoKnowledgeDocument(
        id=PUR_02_DOCUMENT_ID,
        document_code="PUR-02",
        title="Polityka zakupowa i zatwierdzanie dostawców",
        category="Procurement",
        language="pl",
        version="2.5",
    ),
    DemoKnowledgeDocument(
        id=SUP_01_DOCUMENT_ID,
        document_code="SUP-01",
        title="Lista zatwierdzonych dostawców",
        category="Procurement",
        language="pl",
        version="1.8",
    ),
    DemoKnowledgeDocument(
        id=PROD_W38_DOCUMENT_ID,
        document_code="PROD-W38",
        title="Plan produkcji — tydzień 38",
        category="Production",
        language="pl",
        version="2026-W38",
    ),
    DemoKnowledgeDocument(
        id=LOG_05_DOCUMENT_ID,
        document_code="LOG-05",
        title="Procedura transportu modułów prefabrykowanych",
        category="Logistics",
        language="pl",
        version="5.1",
    ),
    DemoKnowledgeDocument(
        id=SALES_03_DOCUMENT_ID,
        document_code="SALES-03",
        title="Standard przygotowania ofert i follow-up",
        category="Sales",
        language="pl",
        version="3.2",
    ),
)