# Rimuovo 'from app import (' se non usato

def test_crud():
    print("--- TEST CRUD ---")
    # UTENTE
    u = add_utente("Test User", "Operatore", "test@example.com")
    assert u.id is not None
    utenti = get_utenti()
    assert any(x.email == "test@example.com" for x in utenti)
    u2 = update_utente(u.id, nome="User Modificato")
    assert u2.nome == "User Modificato"
    assert delete_utente(u.id)
    assert not any(x.id == u.id for x in get_utenti())

    # LOCATION
    loc = add_location("Test Location", "Via Test", "Note di test")
    assert loc.id is not None
    locations = get_locations()
    assert any(x.nome == "Test Location" for x in locations)
    loc2 = update_location(loc.id, note="Note modificate")
    assert loc2.note == "Note modificate"
    assert delete_location(loc.id)
    assert not any(x.id == loc.id for x in get_locations())

    # OGGETTO
    loc = add_location("Loc Oggetto", "Via O", "")
    o = add_oggetto("Test Oggetto", "Desc", "da_rimuovere", "oggetto", loc.id)
    assert o.id is not None
    oggetti = get_oggetti()
    assert any(x.nome == "Test Oggetto" for x in oggetti)
    o2 = update_oggetto(o.id, stato="venduto")
    assert o2.stato == "venduto"
    assert delete_oggetto(o.id)
    assert not any(x.id == o.id for x in get_oggetti())
    delete_location(loc.id)

    # ATTIVITA
    a = add_attivita("Test Attivita", "Descrizione")
    assert a.id is not None
    attivita = get_attivita()
    assert any(x.nome == "Test Attivita" for x in attivita)
    a2 = update_attivita(a.id, descrizione="Modificata")
    assert a2.descrizione == "Modificata"
    assert delete_attivita(a.id)
    assert not any(x.id == a.id for x in get_attivita())

    # OGGETTO_ATTIVITA
    loc = add_location("Loc OA", "Via OA", "")
    o = add_oggetto("Oggetto OA", "Desc", "da_rimuovere", "oggetto", loc.id)
    a = add_attivita("Att OA", "Desc")
    u = add_utente("Utente OA", "Operatore", "oa@example.com")
    oa = add_oggetto_attivita(o.id, a.id, "2024-07-01", u.id)
    assert oa.id is not None
    oas = get_oggetto_attivita()
    assert any(x.id == oa.id for x in oas)
    oa2 = update_oggetto_attivita(oa.id, completata=True)
    assert oa2.completata is True
    assert delete_oggetto_attivita(oa.id)
    assert not any(x.id == oa.id for x in get_oggetto_attivita())
    delete_oggetto(o.id)
    delete_attivita(a.id)
    delete_utente(u.id)
    delete_location(loc.id)

    # NOTA
    loc = add_location("Loc Nota", "Via Nota", "")
    o = add_oggetto("Oggetto Nota", "Desc", "da_rimuovere", "oggetto", loc.id)
    u = add_utente("Utente Nota", "Operatore", "nota@example.com")
    n = add_nota("Test Nota", oggetto_id=o.id, autore_id=u.id, location_id=loc.id)
    assert n.id is not None
    note = get_note(oggetto_id=o.id)
    assert any(x.id == n.id for x in note)
    n2 = update_nota(n.id, testo="Nota Modificata")
    assert n2.testo == "Nota Modificata"
    assert delete_nota(n.id)
    assert not any(x.id == n.id for x in get_note(oggetto_id=o.id))
    delete_oggetto(o.id)
    delete_utente(u.id)
    delete_location(loc.id)

    print("TUTTI I TEST CRUD SUPERATI!")


if __name__ == "__main__":
    test_crud()
