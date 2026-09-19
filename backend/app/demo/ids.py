import uuid

NEXALVORA_DEMO_NAMESPACE = uuid.UUID(
    "5c2c19c4-f69f-4dd2-b4cf-8bf397e714a1"
)


def demo_uuid(key: str) -> uuid.UUID:
    return uuid.uuid5(NEXALVORA_DEMO_NAMESPACE, key)


# Organization

NEXALVORA_ORGANIZATION_ID = demo_uuid(
    "organization:nexalvora-industries"
)

# Departments

SALES_DEPARTMENT_ID = demo_uuid("department:sales")
PROCUREMENT_DEPARTMENT_ID = demo_uuid("department:procurement")
PRODUCTION_DEPARTMENT_ID = demo_uuid("department:production")
QUALITY_DEPARTMENT_ID = demo_uuid("department:quality")
LOGISTICS_DEPARTMENT_ID = demo_uuid("department:logistics")
OPERATIONS_DEPARTMENT_ID = demo_uuid("department:operations")


# Users

ANNA_KOWALSKA_ID = demo_uuid("user:anna-kowalska")
PIOTR_NOWAK_ID = demo_uuid("user:piotr-nowak")
MARTA_ZIELINSKA_ID = demo_uuid("user:marta-zielinska")
KRZYSZTOF_MAZUR_ID = demo_uuid("user:krzysztof-mazur")
TOMASZ_WISNIEWSKI_ID = demo_uuid("user:tomasz-wisniewski")
KAROLINA_WOJCIK_ID = demo_uuid("user:karolina-wojcik")
MICHAL_KAMINSKI_ID = demo_uuid("user:michal-kaminski")
EWA_LEWANDOWSKA_ID = demo_uuid("user:ewa-lewandowska")


# Customers

BALTIC_CONSTRUCTION_GROUP_ID = demo_uuid(
    "customer:baltic-construction-group"
)
NORDBUILD_DEVELOPMENT_ID = demo_uuid(
    "customer:nordbuild-development"
)
MAZOVIA_LOGISTICS_PARKS_ID = demo_uuid(
    "customer:mazovia-logistics-parks"
)
VISTULA_PROPERTY_GROUP_ID = demo_uuid(
    "customer:vistula-property-group"
)
POLARIS_INDUSTRIAL_DEVELOPMENT_ID = demo_uuid(
    "customer:polaris-industrial-development"
)


# Sales opportunities

OPP_2026_041_ID = demo_uuid("opportunity:OPP-2026-041")
OPP_2026_042_ID = demo_uuid("opportunity:OPP-2026-042")
OPP_2026_043_ID = demo_uuid("opportunity:OPP-2026-043")
OPP_2026_044_ID = demo_uuid("opportunity:OPP-2026-044")


# Products

NX_MOD_TECHNICAL_ID = demo_uuid("product:NX-MOD-TECHNICAL")
NX_MOD_OFFICE_ID = demo_uuid("product:NX-MOD-OFFICE")
NX_WALL_PRO_ID = demo_uuid("product:NX-WALL-PRO")
NX_FACADE_ID = demo_uuid("product:NX-FACADE")


# Materials

MAT_204_ID = demo_uuid("material:MAT-204")
MAT_118_ID = demo_uuid("material:MAT-118")
MAT_331_ID = demo_uuid("material:MAT-331")
MAT_086_ID = demo_uuid("material:MAT-086")
MAT_412_ID = demo_uuid("material:MAT-412")
MAT_509_ID = demo_uuid("material:MAT-509")

# ERP locations

MAIN_WAREHOUSE_ID = demo_uuid("location:main-warehouse")


# ERP inventory items

MAT_204_INVENTORY_ID = demo_uuid("inventory:MAT-204:main-warehouse")
MAT_118_INVENTORY_ID = demo_uuid("inventory:MAT-118:main-warehouse")
MAT_331_INVENTORY_ID = demo_uuid("inventory:MAT-331:main-warehouse")
MAT_086_INVENTORY_ID = demo_uuid("inventory:MAT-086:main-warehouse")
MAT_412_INVENTORY_ID = demo_uuid("inventory:MAT-412:main-warehouse")
MAT_509_INVENTORY_ID = demo_uuid("inventory:MAT-509:main-warehouse")


# Suppliers

BUILDCORE_MATERIALS_ID = demo_uuid(
    "supplier:buildcore-materials"
)


# Customer orders

ORD_1048_ID = demo_uuid("order:ORD-1048")
ORD_1047_ID = demo_uuid("order:ORD-1047")
ORD_1046_ID = demo_uuid("order:ORD-1046")
ORD_1045_ID = demo_uuid("order:ORD-1045")
ORD_1044_ID = demo_uuid("order:ORD-1044")


# Purchase orders

PO_2026_0914_ID = demo_uuid(
    "purchase-order:PO-2026-0914"
)


# Knowledge documents

QMS_04_DOCUMENT_ID = demo_uuid("document:QMS-04")
BHP_02_DOCUMENT_ID = demo_uuid("document:BHP-02")
PROC_07_DOCUMENT_ID = demo_uuid("document:PROC-07")
TECH_12_DOCUMENT_ID = demo_uuid("document:TECH-12")
FIRE_03_DOCUMENT_ID = demo_uuid("document:FIRE-03")
PUR_02_DOCUMENT_ID = demo_uuid("document:PUR-02")
SUP_01_DOCUMENT_ID = demo_uuid("document:SUP-01")
PROD_W38_DOCUMENT_ID = demo_uuid("document:PROD-W38")
LOG_05_DOCUMENT_ID = demo_uuid("document:LOG-05")
SALES_03_DOCUMENT_ID = demo_uuid("document:SALES-03")


# Governance scenario

ACT_PROP_001_ID = demo_uuid("action-proposal:ACT-PROP-001")
ACT_PROP_002_ID = demo_uuid("action-proposal:ACT-PROP-002")
ACT_PROP_003_ID = demo_uuid("action-proposal:ACT-PROP-003")

# Approvals

APPROVAL_001_ID = demo_uuid("approval:APPROVAL-001")
APPROVAL_002_ID = demo_uuid("approval:APPROVAL-002")
APPROVAL_003_ID = demo_uuid("approval:APPROVAL-003")


# Executions

EXECUTION_001_ID = demo_uuid("execution:EXECUTION-001")
EXECUTION_002_ID = demo_uuid("execution:EXECUTION-002")


# Audit events

AUDIT_001_ID = demo_uuid("audit:AUDIT-001")
AUDIT_002_ID = demo_uuid("audit:AUDIT-002")
AUDIT_003_ID = demo_uuid("audit:AUDIT-003")
AUDIT_004_ID = demo_uuid("audit:AUDIT-004")
AUDIT_005_ID = demo_uuid("audit:AUDIT-005")
AUDIT_006_ID = demo_uuid("audit:AUDIT-006")
AUDIT_007_ID = demo_uuid("audit:AUDIT-007")