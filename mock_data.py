from app import add_utente, add_location, add_oggetto, add_attivita, add_oggetto_attivita, add_nota

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
        l1.id,
    )
    c2 = add_oggetto(
        "Baule Antico", "Baule in legno d'epoca", "in_attesa", "contenitore", l2.id
    )
    c3 = add_oggetto(
        "Cassetta Plastica",
        "Cassetta in plastica trasparente",
        "da_rimuovere",
        "contenitore",
        l1.id,
    )
    c4 = add_oggetto(
        "Valigia Vintage", "Valigia anni '70 in pelle", "venduto", "contenitore", l3.id
    )

    # Oggetti semplici
    o1 = add_oggetto(
        "Lampada da Tavolo",
        "Lampada vintage in ottone",
        "da_rimuovere",
        "oggetto",
        l1.id,
        c1.id,
    )
    o3 = add_oggetto(
        "Orologio da Parete", "Orologio a pendolo", "in_attesa", "oggetto", l2.id, c2.id
    )
    o6 = add_oggetto(
        "Poltrona", "Poltrona in pelle marrone", "da_rimuovere", "oggetto", l4.id
    )
    o8 = add_oggetto(
        "Specchio", "Specchio con cornice dorata", "in_attesa", "oggetto", l1.id, c3.id
    )

    # Assegnazioni attività
    add_oggetto_attivita(o1.id, a1.id, "2024-07-01", u1.id)
    add_oggetto_attivita(o1.id, a3.id, "2024-06-15", u2.id)
    add_oggetto_attivita(o3.id, a2.id, "2024-07-10", u1.id)
    add_oggetto_attivita(o6.id, a1.id, "2024-07-05", u3.id)
    add_oggetto_attivita(o8.id, a4.id, "2024-06-20", u2.id)

    # Note
    add_nota(
        "Oggetto in buone condizioni, da valutare per vendita", o1.id, None, None, u1.id
    )
    add_nota("Trasporto programmato per venerdì mattina", None, a2.id, None, u2.id)
    add_nota("Location molto umida, attenzione alla muffa", None, None, l3.id, u1.id)
    add_nota(
        "Attività completata in anticipo rispetto alla scadenza",
        None,
        a1.id,
        None,
        u3.id,
    )

    print("Dati di esempio inseriti!")


if __name__ == "__main__":
    popola_mock()
