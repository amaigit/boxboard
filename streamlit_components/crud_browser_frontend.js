// crud_browser_frontend.js
// Logica Dexie.js per CRUD locale e sincronizzazione manuale
// Da integrare in un componente Streamlit custom

// Includi Dexie.js nel tuo HTML:
// <script src="https://unpkg.com/dexie@3.2.4/dist/dexie.min.js"></script>

const db = new Dexie('boxboard_browser');
db.version(1).stores({
    utenti: '++id, nome, email, ruolo',
    locations: '++id, nome, indirizzo, note, data_creazione',
    oggetti: '++id, nome, descrizione, stato, tipo, location_id, contenitore_id, data_rilevamento',
    attivita: '++id, nome, descrizione',
    note: '++id, testo, oggetto_id, attivita_id, location_id, autore_id, data'
});

// CRUD di esempio per utenti
async function addUtente(utente) {
    return await db.utenti.add(utente);
}
async function getUtenti() {
    return await db.utenti.toArray();
}
async function updateUtente(id, changes) {
    return await db.utenti.update(id, changes);
}
async function deleteUtente(id) {
    return await db.utenti.delete(id);
}
// ... analoghi per locations, oggetti, attivita, note ...

// Esportazione dati (JSON)
async function exportAll() {
    const data = {};
    for (const table of ['utenti','locations','oggetti','attivita','note']) {
        data[table] = await db[table].toArray();
    }
    return JSON.stringify(data, null, 2);
}

// Importazione dati (JSON)
async function importAll(jsonStr) {
    const data = JSON.parse(jsonStr);
    for (const table of ['utenti','locations','oggetti','attivita','note']) {
        if (data[table]) {
            await db[table].clear();
            await db[table].bulkAdd(data[table]);
        }
    }
}

// Sincronizzazione manuale con API REST (upload dati locali)
async function syncUpload(entity, apiUrl, token) {
    const items = await db[entity].toArray();
    const res = await fetch(`${apiUrl}/import-bulk/${entity}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: new Blob([JSON.stringify(items)], {type: 'application/json'})
    });
    return await res.json();
}

// Sincronizzazione manuale con API REST (scarica dati dal server)
async function syncDownload(entity, apiUrl, token) {
    const res = await fetch(`${apiUrl}/export-bulk/${entity}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    const items = await res.json();
    await db[entity].clear();
    await db[entity].bulkAdd(items);
    return items.length;
}

// --- SINCRONIZZAZIONE AUTOMATICA ---

// Lista delle entità da sincronizzare
const ENTITIES = ['utenti','locations','oggetti','attivita','note'];

// Funzione di sincronizzazione automatica
async function autoSync(apiUrl, token) {
    if (!navigator.onLine) {
        alert('Sei offline: sincronizzazione rimandata.');
        return;
    }
    let success = 0, fail = 0;
    for (const entity of ENTITIES) {
        try {
            await syncUpload(entity, apiUrl, token);
            await syncDownload(entity, apiUrl, token);
            success++;
        } catch (e) {
            console.error('Sync fallita per', entity, e);
            fail++;
        }
    }
    alert(`Sincronizzazione completata. Successi: ${success}, falliti: ${fail}`);
}

// Listener per eventi online/offline
window.addEventListener('online', () => {
    alert('Connessione ripristinata: avvio sincronizzazione automatica.');
    // Sostituisci con i tuoi parametri reali
    autoSync(window.BOXBOARD_API_URL, window.BOXBOARD_TOKEN);
});
window.addEventListener('offline', () => {
    alert('Sei offline! Le modifiche verranno sincronizzate appena torni online.');
});

// Sincronizzazione periodica (ogni 2 minuti)
setInterval(() => {
    if (navigator.onLine) {
        autoSync(window.BOXBOARD_API_URL, window.BOXBOARD_TOKEN);
    }
}, 120000);

// Per usare la sync automatica:
// 1. Definisci window.BOXBOARD_API_URL e window.BOXBOARD_TOKEN nel tuo HTML prima di includere questo script.
// 2. Le sync avverranno automaticamente quando torni online o ogni 2 minuti.

// Utility per collegare questi metodi ai pulsanti HTML del componente custom.
// Vedi README e doc per istruzioni di integrazione.

// --- UI CRUD INTERATTIVA (ESEMPIO PER OGGETTI) ---

// Renderizza una tabella HTML degli oggetti
async function renderOggettiTable(containerId) {
    const oggetti = await db.oggetti.toArray();
    let html = `<input type='text' id='searchObj' placeholder='Cerca...' oninput='filterOggettiTable()'>`;
    html += `<table border='1' id='oggettiTable'><thead><tr><th>ID</th><th>Nome</th><th>Descrizione</th><th>Stato</th><th>Azioni</th></tr></thead><tbody>`;
    for (const o of oggetti) {
        html += `<tr data-nome='${o.nome.toLowerCase()}'><td>${o.id}</td><td>${o.nome}</td><td>${o.descrizione||''}</td><td>${o.stato||''}</td>` +
            `<td><button onclick='editOggetto(${o.id})'>Modifica</button> <button onclick='deleteOggettoUI(${o.id})'>Elimina</button></td></tr>`;
    }
    html += `</tbody></table>`;
    html += `<button onclick='showAddOggettoModal()'>Aggiungi oggetto</button>`;
    document.getElementById(containerId).innerHTML = html;
}

// Filtro ricerca oggetti
function filterOggettiTable() {
    const val = document.getElementById('searchObj').value.toLowerCase();
    const rows = document.querySelectorAll('#oggettiTable tbody tr');
    for (const r of rows) {
        r.style.display = r.dataset.nome.includes(val) ? '' : 'none';
    }
}

// Modale per aggiunta/modifica oggetto
function showAddOggettoModal(oggetto) {
    const isEdit = !!oggetto;
    const id = oggetto ? oggetto.id : '';
    const nome = oggetto ? oggetto.nome : '';
    const descrizione = oggetto ? oggetto.descrizione : '';
    const stato = oggetto ? oggetto.stato : '';
    const html = `
    <div id='modalOggetto' style='position:fixed;top:20%;left:30%;background:#fff;padding:20px;border:2px solid #888;z-index:1000;'>
        <h3>${isEdit ? 'Modifica' : 'Aggiungi'} oggetto</h3>
        <input id='objNome' placeholder='Nome' value='${nome}'><br>
        <input id='objDescrizione' placeholder='Descrizione' value='${descrizione}'><br>
        <input id='objStato' placeholder='Stato' value='${stato}'><br>
        <button onclick='${isEdit ? `saveOggetto(${id})` : 'addOggettoUI()'}'>Salva</button>
        <button onclick='closeOggettoModal()'>Annulla</button>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', html);
}
function closeOggettoModal() {
    const m = document.getElementById('modalOggetto');
    if (m) m.remove();
}

// Aggiungi oggetto dalla UI
async function addOggettoUI() {
    const nome = document.getElementById('objNome').value;
    const descrizione = document.getElementById('objDescrizione').value;
    const stato = document.getElementById('objStato').value;
    await db.oggetti.add({nome, descrizione, stato});
    closeOggettoModal();
    renderOggettiTable('oggettiCrudContainer');
}
// Modifica oggetto dalla UI
async function saveOggetto(id) {
    const nome = document.getElementById('objNome').value;
    const descrizione = document.getElementById('objDescrizione').value;
    const stato = document.getElementById('objStato').value;
    await db.oggetti.update(id, {nome, descrizione, stato});
    closeOggettoModal();
    renderOggettiTable('oggettiCrudContainer');
}
// Elimina oggetto dalla UI
async function deleteOggettoUI(id) {
    if (confirm('Sei sicuro di voler eliminare questo oggetto?')) {
        await db.oggetti.delete(id);
        renderOggettiTable('oggettiCrudContainer');
    }
}
// Modifica oggetto (apre modale)
async function editOggetto(id) {
    const o = await db.oggetti.get(id);
    showAddOggettoModal(o);
}

// Per integrare:
// 1. Aggiungi <div id='oggettiCrudContainer'></div> nel tuo HTML
// 2. Chiama renderOggettiTable('oggettiCrudContainer') dopo il caricamento pagina
// 3. Adatta per altre entità copiando la logica
// ... existing code ... 