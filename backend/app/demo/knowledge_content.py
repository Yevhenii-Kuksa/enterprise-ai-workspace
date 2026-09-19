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

NEXALVORA_KNOWLEDGE_CONTENT = {
    QMS_04_DOCUMENT_ID: """
Procedura kontroli jakości prefabrykatów.

Każdy gotowy moduł prefabrykowany przed zwolnieniem do wysyłki
musi przejść kontrolę jakości.

Kontrola obejmuje zgodność z dokumentacją techniczną,
stan konstrukcji, elementy wykończeniowe oraz wymagane oznaczenia.

Moduł niespełniający kryteriów jakości nie może zostać oznaczony
jako gotowy do wysyłki do klienta.
""".strip(),
    BHP_02_DOCUMENT_ID: """
Zasady bezpieczeństwa produkcji i montażu.

Pracownicy wykonujący prace produkcyjne i montażowe są zobowiązani
do stosowania wymaganych środków ochrony indywidualnej.

Przed rozpoczęciem pracy należy sprawdzić stan stanowiska,
narzędzi oraz urządzeń wykorzystywanych podczas produkcji.

Nieprawidłowości wpływające na bezpieczeństwo należy niezwłocznie
zgłosić przełożonemu i wstrzymać pracę, jeżeli dalsze działanie
mogłoby stworzyć zagrożenie.
""".strip(),
    PROC_07_DOCUMENT_ID: """
Procedura odbioru materiałów.

Każda dostawa materiałów produkcyjnych musi zostać zweryfikowana
przed przekazaniem materiału do wykorzystania na produkcji.

Kontrola obejmuje zgodność ilościową, identyfikację materiału,
stan opakowania oraz widoczne uszkodzenia.

Materiały wymagające kontroli jakości nie mogą zostać automatycznie
uznane za dostępne do produkcji wyłącznie na podstawie daty dostawy.
""".strip(),
    TECH_12_DOCUMENT_ID: """
NX-Mod Technical — specyfikacja techniczna.

System NX-Mod Technical jest prefabrykowanym modułem technicznym
przeznaczonym do zastosowań w obiektach komercyjnych i przemysłowych.

Dla zamówienia ORD-1048 zaplanowano produkcję 24 modułów
NX-Mod Technical dla projektu Warsaw Logistics Center — Building B.

Produkcja modułów wymaga zastosowania paneli Structural Insulated Panel
120 mm, oznaczonych w systemie materiałowym jako MAT-204.

Brak wymaganej ilości MAT-204 może wpłynąć na harmonogram produkcji
i termin przygotowania modułów do wysyłki.
""".strip(),
    FIRE_03_DOCUMENT_ID: """
Wymagania odporności ogniowej.

Elementy prefabrykowane przeznaczone do projektów wymagających
określonej klasy odporności ogniowej muszą być zgodne
z dokumentacją techniczną danego projektu.

Materiały ogniowe i płyty Fire-rated Gypsum Board powinny być
identyfikowalne w dokumentacji materiałowej oraz podczas kontroli jakości.

Zmiana materiału posiadającego wpływ na parametry pożarowe wymaga
weryfikacji technicznej przed zastosowaniem w produkcji.
""".strip(),
    PUR_02_DOCUMENT_ID: """
Polityka zakupowa i zatwierdzanie dostawców.

Pilne zamówienia materiałowe wymagają uzasadnienia biznesowego,
wskazania ryzyka operacyjnego oraz zatwierdzenia przez uprawnioną osobę.

W przypadku ryzyka dla aktywnego zamówienia klienta dział zakupów
powinien określić dostępne opcje dostawy, potwierdzić terminy
z dostawcą oraz przekazać informację do Operations i Production.

Krytyczne działania zakupowe nie powinny być wykonywane automatycznie
bez zatwierdzenia człowieka.
""".strip(),
    SUP_01_DOCUMENT_ID: """
Lista zatwierdzonych dostawców.

BuildCore Materials Sp. z o.o., kod dostawcy SUP-014,
jest zatwierdzonym dostawcą materiałów konstrukcyjnych
wykorzystywanych w produkcji Nexalvora Industries.

Dla materiałów krytycznych należy monitorować potwierdzony termin dostawy
oraz każdą zmianę harmonogramu zgłoszoną przez dostawcę.

Opóźnienia mogące wpłynąć na aktywne zamówienia klientów
należy eskalować do Procurement i Operations.
""".strip(),
    PROD_W38_DOCUMENT_ID: """
Plan produkcji — tydzień 38 / 2026.

ORD-1048 pozostaje jednym z priorytetowych zleceń produkcyjnych tygodnia.

Plan zakłada kontynuację produkcji 24 modułów NX-Mod Technical
dla Baltic Construction Group.

Potwierdzony termin wysyłki zamówienia ORD-1048:
23.09.2026.

Dostępność materiału MAT-204 jest czynnikiem krytycznym dla utrzymania
harmonogramu. Opóźnione przyjęcie materiału może wymagać korekty
kolejności prac lub aktualizacji planu produkcji.
""".strip(),
    LOG_05_DOCUMENT_ID: """
Procedura transportu modułów prefabrykowanych.

Transport modułów może zostać zaplanowany dopiero po potwierdzeniu
gotowości produkcyjnej oraz pozytywnym zakończeniu kontroli jakości.

Koordynator logistyki potwierdza termin załadunku, dostępność transportu
oraz uzgodnione okno dostawy do klienta.

Ryzyko opóźnienia produkcji należy przekazać do logistyki możliwie wcześnie,
aby ograniczyć koszty zmiany rezerwacji transportu.
""".strip(),
    SALES_03_DOCUMENT_ID: """
Standard przygotowania ofert i follow-up.

Każda szansa sprzedażowa powinna posiadać właściciela, klienta,
wartość oraz aktualny etap procesu sprzedażowego.

Po wysłaniu oferty wymagany jest follow-up oraz aktualizacja etapu
w przypadku negocjacji, wygranej lub utraty szansy.

Po wygraniu szansy sprzedażowej informacje handlowe powinny zostać
przekazane do realizacji zamówienia i dalszej obsługi operacyjnej.
""".strip(),
}