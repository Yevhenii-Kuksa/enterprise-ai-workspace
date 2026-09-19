from dataclasses import dataclass
from uuid import UUID

from app.demo.ids import (
    BUILDCORE_MATERIALS_ID,
    MAT_086_ID,
    MAT_118_ID,
    MAT_204_ID,
    MAT_331_ID,
    MAT_412_ID,
    MAT_509_ID,
    NX_FACADE_ID,
    NX_MOD_OFFICE_ID,
    NX_MOD_TECHNICAL_ID,
    NX_WALL_PRO_ID,
)


@dataclass(frozen=True, slots=True)
class DemoProduct:
    id: UUID
    product_code: str
    name: str
    category: str
    unit: str


@dataclass(frozen=True, slots=True)
class DemoMaterial:
    id: UUID
    material_code: str
    name: str
    unit: str


@dataclass(frozen=True, slots=True)
class DemoSupplier:
    id: UUID
    supplier_code: str
    name: str
    city: str
    country: str = "PL"


NEXALVORA_PRODUCTS = (
    DemoProduct(
        id=NX_MOD_TECHNICAL_ID,
        product_code="PRD-001",
        name="NX-Mod Technical",
        category="Moduł techniczny prefabrykowany",
        unit="szt.",
    ),
    DemoProduct(
        id=NX_MOD_OFFICE_ID,
        product_code="PRD-002",
        name="NX-Mod Office",
        category="Moduł biurowy prefabrykowany",
        unit="szt.",
    ),
    DemoProduct(
        id=NX_WALL_PRO_ID,
        product_code="PRD-003",
        name="NX-Wall Pro",
        category="System ścian prefabrykowanych",
        unit="m²",
    ),
    DemoProduct(
        id=NX_FACADE_ID,
        product_code="PRD-004",
        name="NX-Facade",
        category="System modułów elewacyjnych",
        unit="m²",
    ),
)


NEXALVORA_MATERIALS = (
    DemoMaterial(
        id=MAT_204_ID,
        material_code="MAT-204",
        name="Structural Insulated Panel 120 mm",
        unit="m²",
    ),
    DemoMaterial(
        id=MAT_118_ID,
        material_code="MAT-118",
        name="Galvanized Steel Profile 120",
        unit="mb",
    ),
    DemoMaterial(
        id=MAT_331_ID,
        material_code="MAT-331",
        name="Fire-rated Gypsum Board",
        unit="m²",
    ),
    DemoMaterial(
        id=MAT_086_ID,
        material_code="MAT-086",
        name="Mineral Wool 100 mm",
        unit="m²",
    ),
    DemoMaterial(
        id=MAT_412_ID,
        material_code="MAT-412",
        name="Aluminium Facade Profile",
        unit="mb",
    ),
    DemoMaterial(
        id=MAT_509_ID,
        material_code="MAT-509",
        name="Waterproof Membrane",
        unit="m²",
    ),
)


NEXALVORA_SUPPLIERS = (
    DemoSupplier(
        id=BUILDCORE_MATERIALS_ID,
        supplier_code="SUP-014",
        name="BuildCore Materials Sp. z o.o.",
        city="Łódź",
    ),
)