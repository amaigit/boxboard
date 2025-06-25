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

// --- GESTIONE CONFLITTI AVANZATA (SYNC AUTOMATICA) ---

// Esempio: ogni record deve avere un campo 'updated_at' (timestamp ISO) sia locale che remoto
// La funzione di sync ora confronta i record e, in caso di conflitto, mostra un popup per la scelta

// Log locale dei conflitti risolti
const storicoConflitti = [];

async function syncEntityWithConflicts(entity, apiUrl, token) {
    // Scarica dati remoti
    const res = await fetch(`${apiUrl}/export-bulk/${entity}`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const remoteItems = await res.json();
    const localItems = await db[entity].toArray();
    const localMap = Object.fromEntries(localItems.map(x => [x.id, x]));
    const remoteMap = Object.fromEntries(remoteItems.map(x => [x.id, x]));
    // Unione e confronto
    for (const id of new Set([...Object.keys(localMap), ...Object.keys(remoteMap)])) {
        const local = localMap[id];
        const remote = remoteMap[id];
        if (local && remote) {
            if (local.updated_at !== remote.updated_at) {
                // Conflitto: mostra popup per risoluzione
                await showConflictPopup(entity, local, remote);
            } else {
                // Nessun conflitto, aggiorna locale
                await db[entity].put(remote);
            }
        } else if (remote && !local) {
            await db[entity].add(remote);
        } else if (local && !remote) {
            // Record solo locale: opzionale, puoi chiedere se inviare al server
            // Per ora, mantieni locale
        }
    }
    // Upload dei dati locali risolti
    await syncUpload(entity, apiUrl, token);
}

// Popup HTML per risoluzione conflitti
async function showConflictPopup(entity, local, remote) {
    return new Promise(resolve => {
        const modal = document.createElement('div');
        modal.style = 'position:fixed;top:10%;left:20%;width:60vw;background:#fff;padding:2em;z-index:99999;border:2px solid #888;box-shadow:0 4px 24px #0003;';
        modal.innerHTML = `
        <h3>Conflitto su ${entity} (ID: ${local.id})</h3>
        <div style='display:flex;gap:2em;'>
          <div style='flex:1;'>
            <b>Locale</b><pre style='background:#f9f9f9'>${JSON.stringify(local, null, 2)}</pre>
            <button id='keepLocal'>Mantieni locale</button>
          </div>
          <div style='flex:1;'>
            <b>Server</b><pre style='background:#f9f9f9'>${JSON.stringify(remote, null, 2)}</pre>
            <button id='keepRemote'>Mantieni server</button>
          </div>
        </div>
        <button id='mergeManual' style='margin-top:1em;'>Unisci manualmente</button>
        <button id='closePopup' style='float:right;'>Annulla</button>
        `;
        document.body.appendChild(modal);
        document.getElementById('keepLocal').onclick = () => {
            db[entity].put(local);
            storicoConflitti.unshift({id: local.id, entity, scelta: 'locale', ts: new Date().toISOString()});
            modal.remove();
            resolve('locale');
        };
        document.getElementById('keepRemote').onclick = () => {
            db[entity].put(remote);
            storicoConflitti.unshift({id: local.id, entity, scelta: 'server', ts: new Date().toISOString()});
            modal.remove();
            resolve('server');
        };
        document.getElementById('mergeManual').onclick = () => {
            // Per semplicità, scegli locale e logga come merge manuale (puoi estendere con UI di merge campi)
            db[entity].put(local);
            storicoConflitti.unshift({id: local.id, entity, scelta: 'merge', ts: new Date().toISOString()});
            modal.remove();
            resolve('merge');
        };
        document.getElementById('closePopup').onclick = () => {
            modal.remove();
            resolve('annulla');
        };
    });
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
            await syncEntityWithConflicts(entity, apiUrl, token);
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

// --- NOTIFICHE AVANZATE E STORICO OPERAZIONI ---

// Toast non bloccante
function showToast(msg, type='info') {
    const color = type==='success' ? '#4caf50' : type==='error' ? '#f44336' : '#333';
    const toast = document.createElement('div');
    toast.textContent = msg;
    toast.style = `position:fixed;bottom:30px;right:30px;background:${color};color:#fff;padding:12px 24px;border-radius:6px;z-index:9999;font-size:1.1em;opacity:0.95;box-shadow:0 2px 8px #0003;`;
    document.body.appendChild(toast);
    setTimeout(()=>toast.remove(), 3500);
}

// Badge stato online/offline
function renderOnlineBadge(containerId) {
    const online = navigator.onLine;
    const html = `<span style='padding:4px 12px;border-radius:12px;background:${online?'#4caf50':'#f44336'};color:#fff;'>${online?'ONLINE':'OFFLINE'}</span>`;
    document.getElementById(containerId).innerHTML = html;
}
window.addEventListener('online', ()=>renderOnlineBadge('badgeOnline'));
window.addEventListener('offline', ()=>renderOnlineBadge('badgeOnline'));

// Storico operazioni (in memoria, max 50)
const storicoOperazioni = [];
function logOperazione(msg, type='info') {
    storicoOperazioni.unshift({msg, type, ts: new Date().toLocaleString()});
    if (storicoOperazioni.length>50) storicoOperazioni.pop();
    renderStorico('storicoContainer');
}
function renderStorico(containerId) {
    if (!document.getElementById(containerId)) return;
    let html = '<b>Storico operazioni</b><ul style="max-height:200px;overflow:auto;font-size:0.95em">';
    for (const op of storicoOperazioni) {
        html += `<li style='color:${op.type==='error'?'#f44336':op.type==='success'?'#4caf50':'#333'}'>[${op.ts}] ${op.msg}</li>`;
    }
    html += '</ul>';
    document.getElementById(containerId).innerHTML = html;
}

// Esempio: usa showToast/logOperazione nelle funzioni CRUD/sync
// Sostituisci alert(...) con showToast(...) e logOperazione(...)
// ... existing code ... 