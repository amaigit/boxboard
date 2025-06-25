from crud import add_utente, add_location, add_oggetto, add_attivita, add_oggetto_attivita, add_nota

# Rimuovo 'from app import (' se non usato


def popola_mock():
    print("Popolamento dati di esempio...")
    # Utenti
    u1 = add_utente("Mario Rossi", "Operatore", "mario@example.com")
    u2 = add_utente("Luigi Bianchi", "Coordinatore", "luigi@example.com")
    u3 = add_utente("Anna Verdi", "Altro", "anna@example.com")

    # Location
    l1 = add_location("Magazzino Centrale", "Via Roma 1", "Sede principale")
    l2 = add_location("Deposito Nord", "Via Milano 10", "")
    l3 = add_location("Cantina Sud", "Via Napoli 5", "")
    l4 = add_location("Box Garage", "Via Torino 22", "")

    # Attività
    a1 = add_attivita("Valutazione", "Valutare il valore dell'oggetto")
    a2 = add_attivita("Trasporto", "Trasportare l'oggetto al deposito")
    a3 = add_attivita("Pulizia", "Pulire e igienizzare l'oggetto")
    a4 = add_attivita("Catalogazione", "Catalogare e fotografare l'oggetto")

    # Contenitori
    c1 = add_oggetto(
        "Scatola Grande Cartone",
        "Scatola di cartone 60x40x40cm",
        "da_rimuovere",
        "contenitore",
        l1,
    )
    c2 = add_oggetto(
        "Baule Antico", "Baule in legno d'epoca", "in_attesa", "contenitore", l2
    )
    c3 = add_oggetto(
        "Cassetta Plastica",
        "Cassetta in plastica trasparente",
        "da_rimuovere",
        "contenitore",
        l1,
    )
    c4 = add_oggetto(
        "Valigia Vintage", "Valigia anni '70 in pelle", "venduto", "contenitore", l3
    )

    # Oggetti semplici
    o1 = add_oggetto(
        "Lampada da Tavolo",
        "Lampada vintage in ottone",
        "da_rimuovere",
        "oggetto",
        l1,
        c1,
    )
    o3 = add_oggetto(
        "Orologio da Parete", "Orologio a pendolo", "in_attesa", "oggetto", l2, c2
    )
    o6 = add_oggetto(
        "Poltrona", "Poltrona in pelle marrone", "da_rimuovere", "oggetto", l4
    )
    o8 = add_oggetto(
        "Specchio", "Specchio con cornice dorata", "in_attesa", "oggetto", l1, c3
    )

    # Assegnazioni attività
    add_oggetto_attivita(o1, a1, "2024-07-01", u1)
    add_oggetto_attivita(o1, a3, "2024-06-15", u2)
    add_oggetto_attivita(o3, a2, "2024-07-10", u1)
    add_oggetto_attivita(o6, a1, "2024-07-05", u3)
    add_oggetto_attivita(o8, a4, "2024-06-20", u2)

    # Note
    add_nota(
        "Oggetto in buone condizioni, da valutare per vendita", o1, None, None, u1
    )
    add_nota("Trasporto programmato per venerdì mattina", None, a2, None, u2)
    add_nota("Location molto umida, attenzione alla muffa", None, None, l3, u1)
    add_nota(
        "Attività completata in anticipo rispetto alla scadenza",
        None,
        a1,
        None,
        u3,
    )

    print("Dati di esempio inseriti!")


if __name__ == "__main__":
    popola_mock()
