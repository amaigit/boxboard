import streamlit as st
import streamlit.components.v1 as components

def st_crud_browser(key=None):
    """
    Componente custom per CRUD locale in modalità browser (IndexedDB + Dexie.js).
    Placeholder: la parte JS sarà integrata in seguito.
    """
    st.info("Modalità browser attiva: i dati saranno salvati solo localmente nel browser tramite IndexedDB/Dexie.js.")
    components.html("""
    <div style='padding:1em; border:1px dashed #888; background:#f9f9f9;'>
        <b>CRUD locale (browser):</b><br>
        <ul>
            <li><b>Utenti</b>: aggiungi, modifica, elimina utenti locali</li>
            <li><b>Locations</b>: gestione sedi/località</li>
            <li><b>Oggetti</b>: gestione oggetti e contenitori</li>
            <li><b>Attività</b>: gestione attività e assegnazioni</li>
            <li><b>Note</b>: aggiungi note agli oggetti/attività/locations</li>
        </ul>
        <button disabled style='margin:0.5em;'>Esporta dati (JSON)</button>
        <button disabled style='margin:0.5em;'>Importa dati (JSON)</button>
        <br><i>Qui saranno attivi i pulsanti per esportare/importare tutti i dati in formato JSON.<br>
        Questa è una preview tecnica: la logica JS sarà integrata in seguito.</i>
    </div>
    """, height=320, key=key) 