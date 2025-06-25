import streamlit as st
import streamlit.components.v1 as components


def st_crud_browser(key=None):
    """
    Componente custom per CRUD locale in modalità browser (IndexedDB + Dexie.js).
    Placeholder: la parte JS sarà integrata in seguito.
    """
    st.info(
        "Modalità browser attiva: i dati saranno salvati solo localmente nel browser tramite IndexedDB/Dexie.js."
    )
    components.html(
        """
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
        <button disabled style='margin:0.5em;background:#d0f;'>Sincronizza con server (upload)</button>
        <button disabled style='margin:0.5em;background:#0df;'>Sincronizza con server (download)</button>
        <br><i>I pulsanti di sincronizzazione permetteranno di inviare/ricevere dati dal server tramite API REST.<br>
        Sarà possibile gestire conflitti e merge manualmente.<br>
        Questa è una preview tecnica: la logica JS sarà integrata in seguito.</i>
    </div>
    """,
        height=400,
        key=key,
    )

    st.markdown(
        """
    **Come integrare la logica JS:**
    - Includi Dexie.js: `<script src='https://unpkg.com/dexie@3.2.4/dist/dexie.min.js'></script>`
    - Includi il file `crud_browser_frontend.js` fornito nel repo.
    - Collega i pulsanti HTML alle funzioni JS (es: `onclick='exportAll()'`, `onclick='syncUpload(...)'`).
    - Consulta il README e i commenti nel file JS per dettagli.
    """
    )
