# Rimuovo 'from app import (' se non usato

from crud import add_utente, update_utente, delete_utente, add_location, update_location, delete_location, add_oggetto, update_oggetto, delete_oggetto, add_attivita, update_attivita, delete_attivita, add_oggetto_attivita, update_oggetto_attivita, delete_oggetto_attivita, add_nota, update_nota, delete_nota

def test_crud():
    print("--- TEST CRUD ---")
    # UTENTE
    u_id = add_utente("Test User", "Operatore", "test@user.com")
    assert u_id is not None
    assert update_utente(u_id, nome="User Aggiornato") == u_id
    assert delete_utente(u_id) is True

    # LOCATION
    l_id = add_location("Test Location", "Via Test", "Note di test")
    assert l_id is not None
    assert update_location(l_id, note="Note modificate") == l_id
    assert delete_location(l_id) is True

    # OGGETTO
    l_id = add_location("Loc Oggetto", "Via O", "")
    o_id = add_oggetto("Test Oggetto", "Desc", "da_rimuovere", "oggetto", l_id)
    assert o_id is not None
    assert update_oggetto(o_id, nome="Oggetto Aggiornato") == o_id
    assert delete_oggetto(o_id) is True
    delete_location(l_id)

    # ATTIVITA
    a_id = add_attivita("Test Attivita", "Desc")
    assert a_id is not None
    assert update_attivita(a_id, nome="Attivita Aggiornata") == a_id
    assert delete_attivita(a_id) is True

    # OGGETTO_ATTIVITA
    l_id = add_location("Loc OA", "Via OA", "")
    o_id = add_oggetto("Oggetto OA", "Desc", "da_rimuovere", "oggetto", l_id)
    a_id = add_attivita("Att OA", "Desc")
    u_id = add_utente("Utente OA", "Operatore", "oa@example.com")
    oa_id = add_oggetto_attivita(o_id, a_id, "2024-07-01", u_id)
    assert oa_id is not None
    assert update_oggetto_attivita(oa_id, completata=True) == oa_id
    assert delete_oggetto_attivita(oa_id) is True
    delete_attivita(a_id)
    delete_utente(u_id)
    delete_location(l_id)

    # NOTA
    l_id = add_location("Loc Nota", "Via Nota", "")
    o_id = add_oggetto("Oggetto Nota", "Desc", "da_rimuovere", "oggetto", l_id)
    u_id = add_utente("Utente Nota", "Operatore", "nota@example.com")
    n_id = add_nota("Test Nota", oggetto_id=o_id, autore_id=u_id, location_id=l_id)
    assert n_id is not None
    assert update_nota(n_id, testo="Nota aggiornata") == n_id
    assert delete_nota(n_id) is True
    delete_oggetto(o_id)
    delete_utente(u_id)
    delete_location(l_id)

    print("TUTTI I TEST CRUD (add, update, delete) SUPERATI!")


if __name__ == "__main__":
    test_crud()
