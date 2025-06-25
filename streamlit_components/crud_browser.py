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
        Qui verrà integrata l'interfaccia CRUD con Dexie.js.<br>
        <i>Questa è una preview tecnica. La logica JS sarà integrata in seguito.</i>
    </div>
    """, height=120, key=key) 