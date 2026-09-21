export const demoCompany = {
  name: 'Nexalvora Industries Sp. z o.o.',
  shortName: 'Nexalvora Industries',
  environment: 'Środowisko demonstracyjne',
  dateLabel: '19 września 2026',
}

export const currentUser = {
  employeeCode: 'USR-001',
  fullName: 'Anna Kowalska',
  email: 'anna.kowalska@nexalvora.example',
  jobTitle: 'Operations Manager',
  systemRole: 'Administrator',
}

export const demoSales = {
  openPipelinePln: 920_000,
  wonValuePln: 686_400,
  opportunities: [
    {
      code: 'OPP-2026-041',
      customer: 'Baltic Construction Group Sp. z o.o.',
      project: 'Warsaw Logistics Center — Building B',
      stage: 'WON',
      valuePln: 686_400,
      owner: 'Karolina Wójcik',
    },
    {
      code: 'OPP-2026-042',
      customer: 'NordBuild Development Sp. z o.o.',
      project: 'NordBuild Business Park — Office Modules',
      stage: 'NEGOTIATION',
      valuePln: 420_000,
      owner: 'Tomasz Wiśniewski',
    },
    {
      code: 'OPP-2026-043',
      customer: 'Mazovia Logistics Parks S.A.',
      project: 'Mazovia Logistics Park — Wall Systems',
      stage: 'PROPOSAL_SENT',
      valuePln: 315_000,
      owner: 'Karolina Wójcik',
    },
    {
      code: 'OPP-2026-044',
      customer: 'Vistula Property Group Sp. z o.o.',
      project: 'Vistula Retail Hub — Facade Modules',
      stage: 'QUALIFIED',
      valuePln: 185_000,
      owner: 'Michał Kamiński',
    },
  ],
}

export const demoOrders = [
  {
    number: 'ORD-1048',
    customer: 'Baltic Construction Group Sp. z o.o.',
    project: 'Warsaw Logistics Center — Building B',
    product: 'NX-Mod Technical',
    quantity: 24,
    valuePln: 686_400,
    lifecycle: 'IN_PROGRESS',
    delayState: 'AT_RISK',
    deliveryDate: '23.09.2026',
  },
  {
    number: 'ORD-1047',
    customer: 'NordBuild Development Sp. z o.o.',
    product: 'NX-Mod Office',
    lifecycle: 'IN_PROGRESS',
    delayState: 'ON_TIME',
    deliveryDate: '28.09.2026',
  },
  {
    number: 'ORD-1046',
    customer: 'Mazovia Logistics Parks S.A.',
    product: 'NX-Wall Pro',
    lifecycle: 'READY',
    delayState: 'ON_TIME',
    deliveryDate: '20.09.2026',
  },
  {
    number: 'ORD-1045',
    customer: 'Vistula Property Group Sp. z o.o.',
    product: 'NX-Facade',
    lifecycle: 'IN_PROGRESS',
    delayState: 'DELAYED',
    deliveryDate: '18.09.2026',
  },
  {
    number: 'ORD-1044',
    customer: 'Polaris Industrial Development Sp. z o.o.',
    product: 'NX-Mod Technical',
    lifecycle: 'DRAFT',
    delayState: 'ON_TIME',
    deliveryDate: null,
  },
]

export const mainRisk = {
  orderNumber: 'ORD-1048',
  materialCode: 'MAT-204',
  materialName: 'Structural Insulated Panel 120 mm',
  required: 260,
  onHand: 180,
  shortage: 80,
  safetyStock: 300,
  safetyStockGap: 120,
  riskLevel: 'HIGH',
  supplier: 'BuildCore Materials Sp. z o.o.',
  purchaseOrder: 'PO-2026-0914',
  firstDelivery: '21.09.2026',
  firstDeliveryQuantity: 200,
  secondDelivery: '25.09.2026',
  secondDeliveryQuantity: 200,
  shipmentDate: '23.09.2026',
}

export const demoKnowledgeDocuments = [
  {
    code: 'QMS-04',
    title: 'Procedura kontroli jakości prefabrykatów',
    category: 'Quality',
    version: '4.2',
  },
  {
    code: 'BHP-02',
    title: 'Zasady bezpieczeństwa produkcji i montażu',
    category: 'Safety',
    version: '2.1',
  },
  {
    code: 'PROC-07',
    title: 'Procedura odbioru materiałów',
    category: 'Procurement',
    version: '3.0',
  },
  {
    code: 'TECH-12',
    title: 'Specyfikacja techniczna NX-Mod Technical',
    category: 'Technical',
    version: '12.3',
  },
  {
    code: 'FIRE-03',
    title: 'Wymagania odporności ogniowej',
    category: 'Compliance',
    version: '3.4',
  },
  {
    code: 'PUR-02',
    title: 'Polityka zakupowa i zatwierdzanie dostawców',
    category: 'Procurement',
    version: '2.5',
  },
  {
    code: 'SUP-01',
    title: 'Lista zatwierdzonych dostawców',
    category: 'Procurement',
    version: '1.8',
  },
  {
    code: 'PROD-W38',
    title: 'Plan produkcji — tydzień 38',
    category: 'Produkcja',
    version: '2026-W38',
  },
  {
    code: 'LOG-05',
    title: 'Procedura transportu modułów prefabrykowanych',
    category: 'Logistics',
    version: '5.1',
  },
  {
    code: 'SALES-03',
    title: 'Standard przygotowania ofert i follow-up',
    category: 'Sales',
    version: '3.2',
  },
]

export const demoEmails = [
  {
    sender: 'BuildCore Materials Sp. z o.o.',
    recipient: 'Piotr Nowak',
    subject: 'Aktualizacja dostawy MAT-204 / PO-2026-0914',
    time: '08:12',
  },
  {
    sender: 'Krzysztof Mazur',
    recipient: 'Anna Kowalska',
    subject: 'ORD-1048 — ryzyko terminu produkcji',
    time: '09:05',
  },
  {
    sender: 'Baltic Construction Group Sp. z o.o.',
    recipient: 'Karolina Wójcik',
    subject: 'Potwierdzenie terminu dostawy ORD-1048',
    time: '10:18',
  },
]

export const demoCalendarEvents = [
  {
    title: 'Przegląd ryzyka ORD-1048',
    date: '19.09.2026',
    time: '11:00',
  },
  {
    title: 'Odbiór pierwszej partii MAT-204',
    date: '21.09.2026',
    time: '08:00',
  },
  {
    title: 'Kontrola gotowości produkcyjnej ORD-1048',
    date: '22.09.2026',
    time: '13:00',
  },
  {
    title: 'Potwierdzenie dostawy ORD-1048 z klientem',
    date: '23.09.2026',
    time: '07:30',
  },
]

export const demoIntegrations = [
  {
    key: 'gmail',
    name: 'Gmail',
    provider: 'Google Workspace',
    status: 'READY',
    capability: 'READ_MESSAGES',
  },
  {
    key: 'google-drive',
    name: 'Google Drive',
    provider: 'Google Workspace',
    status: 'READY',
    capability: 'READ_FILES',
  },
  {
    key: 'sharepoint',
    name: 'SharePoint',
    provider: 'Microsoft 365',
    status: 'READY',
    capability: 'READ_FILES',
  },
  {
    key: 'google-calendar',
    name: 'Google Calendar',
    provider: 'Google Workspace',
    status: 'READY',
    capability: 'READ_CALENDAR_EVENTS',
  },
  {
    key: 'erp',
    name: 'ERP',
    provider: 'Nexalvora ERP',
    status: 'READY',
    capability: 'READ_ERP_DATA',
  },
]

export const demoApprovals = [
  {
    code: 'ACT-PROP-001',
    title: 'Utworzyć pilne zamówienie materiału MAT-204',
    status: 'APPROVED',
    approver: 'Piotr Nowak',
  },
  {
    code: 'ACT-PROP-002',
    title: 'Zaktualizować harmonogram produkcji ORD-1048',
    status: 'APPROVED',
    approver: 'Anna Kowalska',
  },
  {
    code: 'ACT-PROP-003',
    title: 'Przygotować komunikat do klienta o ryzyku terminu',
    status: 'PENDING',
    approver: null,
  },
]

export const demoExecutions = [
  {
    code: 'EXECUTION-001',
    proposalCode: 'ACT-PROP-001',
    status: 'SUCCEEDED',
    summary: 'Pilne zamówienie MAT-204 przekazano do obsługi zakupowej.',
    time: '10:52',
  },
  {
    code: 'EXECUTION-002',
    proposalCode: 'ACT-PROP-002',
    status: 'SUCCEEDED',
    summary: 'Harmonogram ORD-1048 oznaczono do aktualizacji.',
    time: '10:57',
  },
]

export const demoAuditEvents = [
  {
    time: '10:30',
    event: 'AI_INSIGHT_CREATED',
    description: 'AI wykrył ryzyko terminu dla ORD-1048.',
    actionId: null,
  },
  {
    time: '10:35',
    event: 'ACTION_PROPOSAL_CREATED',
    description: 'Utworzono propozycję pilnego zamówienia MAT-204.',
    actionId: 'ACT-PROP-001',
  },
  {
    time: '10:40',
    event: 'ACTION_PROPOSAL_CREATED',
    description: 'Utworzono propozycję aktualizacji harmonogramu ORD-1048.',
    actionId: 'ACT-PROP-002',
  },
  {
    time: '10:50',
    event: 'APPROVAL_GRANTED',
    description: 'Piotr Nowak zatwierdził działanie zakupowe.',
    actionId: 'APPROVAL-001',
  },
  {
    time: '10:52',
    event: 'ACTION_EXECUTED',
    description: 'Wykonano zatwierdzone działanie dotyczące MAT-204.',
    actionId: 'EXECUTION-001',
  },
  {
    time: '10:55',
    event: 'APPROVAL_GRANTED',
    description: 'Anna Kowalska zatwierdziła aktualizację harmonogramu.',
    actionId: 'APPROVAL-002',
  },
  {
    time: '10:57',
    event: 'ACTION_EXECUTED',
    description: 'Wykonano aktualizację harmonogramu ORD-1048.',
    actionId: 'EXECUTION-002',
  },
]