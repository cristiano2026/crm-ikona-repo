# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import uuid
from datetime import datetime

# Inizializza l'applicazione Flask
app = Flask(__name__)
# Imposta una chiave segreta per il funzionamento dei messaggi flash e delle sessioni
app.secret_key = 'chiave_segreta_molto_sicura'

# --- In-Memory Database (simulazione di un database) ---
# Usiamo una lista di dizionari per memorizzare i dati dei clienti
clients = [
    {
        'id': str(uuid.uuid4()),
        'name': 'Azienda Alpha',
        'contact': 'Mario Rossi',
        'email': 'mario.rossi@alpha.it',
        'phone': '011-1234567',
        'vat_id': 'IT12345678901',
        'address': 'Via Roma 10',
        'city': 'Torino',
        'zip': '10121',
        'sdi_code': 'ABCDEFG',
        'agent': 'Giuseppe Verdi',
        'call_center': 'Call Center Nord',
        'created_at': datetime(2023, 1, 1) # Aggiunto il campo created_at
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Beta S.r.l.',
        'contact': 'Giulia Bianchi',
        'email': 'giulia.bianchi@beta.it',
        'phone': '022-9876543',
        'vat_id': 'IT98765432109',
        'address': 'Corso Sempione 5',
        'city': 'Milano',
        'zip': '20145',
        'sdi_code': 'HIJKLMN',
        'agent': 'Anna Neri',
        'call_center': 'Call Center Sud',
        'created_at': datetime(2023, 2, 1) # Aggiunto il campo created_at
    },
]

# Lista per memorizzare i dati dei servizi
services = [
    {'id': str(uuid.uuid4()), 'name': 'Sviluppo Sito Web', 'price': 1500, 'description': 'Creazione di un sito web responsivo.'},
    {'id': str(uuid.uuid4()), 'name': 'Campagna Social Media', 'price': 800, 'description': 'Gestione di profili social e campagne pubblicitarie.'},
]

# --- STRUTTURA DATI PER COLLEGARE CLIENTI E SERVIZI ---
# Questo "database" tiene traccia di quali servizi sono associati a quali clienti
client_services = [
    {
        'id': str(uuid.uuid4()),
        'client_id': clients[0]['id'],
        'service_id': services[0]['id'],
        'subscribed_price': 1400.00,
        'start_date': datetime(2023, 1, 15),
        'end_date': datetime(2023, 12, 31),
        'notes': 'Sconto applicato per l\'anno intero.'
    },
    {
        'id': str(uuid.uuid4()),
        'client_id': clients[0]['id'],
        'service_id': services[1]['id'],
        'subscribed_price': 750.00,
        'start_date': datetime(2023, 3, 1),
        'end_date': None,
        'notes': 'Contratto a tempo indeterminato.'
    }
]


# --- Route per la Homepage ---
@app.route('/')
def index():
    """Renderizza la pagina principale del sito."""
    return render_template('index.html')

# --- Route per l'elenco dei clienti ---
@app.route('/clients')
def show_clients():
    """Renderizza la pagina con la lista dei clienti."""
    return render_template('clients.html', clients=clients)

# --- Route per aggiungere un nuovo cliente ---
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    """
    Gestisce l'aggiunta di un nuovo cliente.
    GET: Mostra il form per l'inserimento.
    POST: Elabora i dati del form e aggiunge il cliente alla lista.
    """
    form_data = {}
    
    if request.method == 'POST':
        form_data = request.form
        
        # Estrae i dati specifici che ci interessano per la validazione
        client_name = form_data.get('nome')
        
        if client_name:
            # Crea un nuovo dizionario per il cliente con un ID univoco e tutti i campi
            new_client = {
                'id': str(uuid.uuid4()),
                'name': client_name,
                'email': form_data.get('email', ''),
                'phone': form_data.get('telefono', ''),
                'vat_id': form_data.get('partita_iva', ''),
                'address': form_data.get('indirizzo', ''),
                'city': form_data.get('citta', ''),
                'zip': form_data.get('cap', ''),
                'sdi_code': form_data.get('codice_sdi', ''),
                'agent': form_data.get('agente', ''),
                'call_center': form_data.get('call_center', ''),
                'contact': form_data.get('referente_aziendale', ''),
                'created_at': datetime.now() # Aggiunge la data e l'ora attuali
            }
            clients.append(new_client)
            flash(f'Cliente "{client_name}" aggiunto con successo!', 'success')
            return redirect(url_for('show_clients'))
        else:
            flash('Errore: Il campo "Nome / Ragione Sociale" è obbligatorio.', 'error')
            
    return render_template('add_client.html', form_data=form_data)


# --- Route per visualizzare i dettagli di un cliente e i suoi servizi ---
@app.route('/clients/<string:client_id>')
def show_client(client_id):
    """
    Renderizza la pagina con i dettagli di un singolo cliente.
    (La funzione è stata rinominata da 'view_client' a 'show_client' per coerenza)
    """
    # Cerca il cliente con l'ID specificato
    client = next((item for item in clients if item['id'] == client_id), None)
    if not client:
        flash('Cliente non trovato.', 'error')
        return redirect(url_for('show_clients'))

    # Recupera tutti i servizi sottoscritti da questo cliente
    client_specific_services = []
    for cs in client_services:
        if cs['client_id'] == client_id:
            service = next((s for s in services if s['id'] == cs['service_id']), None)
            if service:
                client_specific_services.append((cs, service))

    # Passa i dati al template
    return render_template('client_detail.html', client=client, services=client_specific_services)


# --- Route per modificare un cliente esistente ---
@app.route('/edit_client/<string:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    """
    Gestisce la modifica di un cliente.
    GET: Mostra il form precompilato con i dati del cliente.
    POST: Aggiorna i dati del cliente nella lista.
    """
    client = next((item for item in clients if item['id'] == client_id), None)

    if not client:
        flash('Cliente non trovato.', 'error')
        return redirect(url_for('show_clients'))

    if request.method == 'POST':
        # Aggiorna i dati del cliente con tutti i campi del modulo
        client['name'] = request.form.get('name')
        client['email'] = request.form.get('email')
        client['phone'] = request.form.get('phone')
        client['vat_id'] = request.form.get('vat_id')
        client['address'] = request.form.get('address')
        client['city'] = request.form.get('citta')
        client['zip'] = request.form.get('cap')
        client['sdi_code'] = request.form.get('sdi_code')
        client['agent'] = request.form.get('agente')
        client['call_center'] = request.form.get('call_center')
        client['contact'] = request.form.get('referente_aziendale')
        flash('Cliente modificato con successo!', 'success')
        return redirect(url_for('show_client', client_id=client_id))

    # Se il metodo è GET, renderizza la pagina del form
    return render_template('edit_client.html', client=client)

# --- Route per eliminare un cliente ---
@app.route('/delete_client/<string:client_id>')
def delete_client(client_id):
    """Elimina un cliente dalla lista."""
    global clients, client_services
    clients = [client for client in clients if client['id'] != client_id]
    # Rimuovi anche tutti i servizi associati a questo cliente
    client_services = [cs for cs in client_services if cs['client_id'] != client_id]
    flash('Cliente eliminato con successo!', 'success')
    return redirect(url_for('show_clients'))

# --- NUOVE ROTTE PER LA GESTIONE DEI SERVIZI ---

# --- Route per l'elenco dei servizi ---
@app.route('/services')
def show_services():
    """Renderizza la pagina con la lista dei servizi."""
    return render_template('services.html', services=services)

# --- Route per aggiungere un nuovo servizio ---
@app.route('/add_service', methods=['GET', 'POST'])
def add_service_route():
    """
    Gestisce l'aggiunta di un nuovo servizio.
    GET: Mostra il form.
    POST: Elabora i dati del form e aggiunge il servizio.
    """
    if request.method == 'POST':
        service_name = request.form.get('name')
        service_price = request.form.get('price')
        service_description = request.form.get('description')

        if service_name and service_price and service_description:
            new_service = {
                'id': str(uuid.uuid4()),
                'name': service_name,
                'price': float(service_price),
                'description': service_description
            }
            services.append(new_service)
            flash('Servizio aggiunto con successo!', 'success')
            return redirect(url_for('show_services'))
        else:
            flash('Errore: tutti i campi sono obbligatori.', 'error')
            
    return render_template('add_service.html')

# --- Route per visualizzare un servizio ---
@app.route('/services/<string:service_id>')
def view_service_detail(service_id):
    """Renderizza la pagina con i dettagli di un singolo servizio."""
    service = next((item for item in services if item['id'] == service_id), None)
    if service:
        return render_template('view_service.html', service=service)
    else:
        flash('Servizio non trovato.', 'error')
        return redirect(url_for('show_services'))

# --- Route per modificare un servizio ---
@app.route('/edit_service/<string:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    """
    Gestisce la modifica di un servizio esistente.
    GET: Mostra il form precompilato.
    POST: Aggiorna i dati del servizio.
    """
    service = next((item for item in services if item['id'] == service_id), None)

    if not service:
        flash('Servizio non trovato.', 'error')
        return redirect(url_for('show_services'))

    if request.method == 'POST':
        service['name'] = request.form.get('name')
        service['price'] = float(request.form.get('price'))
        service['description'] = request.form.get('description')
        flash('Servizio modificato con successo!', 'success')
        return redirect(url_for('show_services'))

    return render_template('edit_service.html', service=service)

# --- Route per eliminare un servizio ---
@app.route('/delete_service/<string:service_id>')
def delete_service(service_id):
    """Elimina un servizio dalla lista."""
    global services, client_services
    services = [service for service in services if service['id'] != service_id]
    # Rimuovi anche le associazioni con i clienti
    client_services = [cs for cs in client_services if cs['service_id'] != service_id]
    flash('Servizio eliminato con successo!', 'success')
    return redirect(url_for('show_services'))


# --- ROTTE PER LA GESTIONE DEI SERVIZI PER CLIENTE ---
@app.route('/clients/<string:client_id>/add_service', methods=['GET', 'POST'])
def add_client_service(client_id):
    """
    Gestisce l'associazione di un servizio a un cliente.
    GET: Mostra il form.
    POST: Elabora i dati del form e crea l'associazione.
    """
    # Trova il cliente per ID, o reindirizza se non esiste
    client = next((c for c in clients if c['id'] == client_id), None)
    if not client:
        flash('Cliente non trovato.', 'error')
        return redirect(url_for('show_clients'))

    if request.method == 'POST':
        service_id = request.form.get('service_id')
        subscribed_price = request.form.get('subscribed_price')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        notes = request.form.get('notes')

        if not service_id or not subscribed_price or not start_date_str:
            flash('Compila tutti i campi obbligatori.', 'error')
            return redirect(url_for('add_client_service', client_id=client['id']))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
            subscribed_price = float(subscribed_price)
            
            # Controlla se il servizio è già stato aggiunto
            existing_service = next((cs for cs in client_services if cs['client_id'] == client_id and cs['service_id'] == service_id), None)

            if existing_service:
                flash('Questo servizio è già stato aggiunto a questo cliente.', 'error')
                return redirect(url_for('add_client_service', client_id=client['id']))

            new_client_service = {
                'id': str(uuid.uuid4()),
                'client_id': client_id,
                'service_id': service_id,
                'subscribed_price': subscribed_price,
                'start_date': start_date,
                'end_date': end_date,
                'notes': notes
            }
            client_services.append(new_client_service)
            flash('Servizio aggiunto con successo!', 'success')
            return redirect(url_for('show_client', client_id=client_id))

        except (ValueError, TypeError) as e:
            flash(f'Errore nel formato dei dati: {e}', 'error')
            return redirect(url_for('add_client_service', client_id=client['id']))

    # Renderizza il template passando i dati del cliente e dei servizi
    return render_template('add_client_service.html', client=client, services=services)


@app.route('/clients/<string:client_id>/edit_service/<string:client_service_id>', methods=['GET', 'POST'])
def edit_client_service(client_id, client_service_id):
    """
    Gestisce la modifica di un servizio già associato a un cliente.
    """
    client = next((c for c in clients if c['id'] == client_id), None)
    client_service = next((cs for cs in client_services if cs['id'] == client_service_id), None)

    if not client or not client_service:
        flash('Cliente o servizio non trovato.', 'error')
        return redirect(url_for('show_clients'))

    if request.method == 'POST':
        # Aggiorna i dati dell'associazione servizio-cliente
        client_service['service_id'] = request.form.get('service_id')
        client_service['subscribed_price'] = float(request.form.get('subscribed_price'))
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        client_service['notes'] = request.form.get('notes')
        
        client_service['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d')
        client_service['end_date'] = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        flash('Servizio cliente modificato con successo!', 'success')
        return redirect(url_for('show_client', client_id=client_id))

    return render_template('edit_client_service.html', client=client, client_service=client_service, available_services=services)

@app.route('/clients/<string:client_id>/delete_service/<string:client_service_id>', methods=['POST'])
def delete_client_service(client_id, client_service_id):
    """
    Elimina un servizio associato a un cliente.
    """
    global client_services
    # Filtra la lista per rimuovere l'associazione specifica
    client_services = [cs for cs in client_services if cs['id'] != client_service_id]
    flash('Servizio rimosso dal cliente con successo!', 'success')
    return redirect(url_for('show_client', client_id=client_id))


# --- Avvia l'applicazione ---
if __name__ == '__main__':
    # Esegue l'applicazione in modalità debug, utile per lo sviluppo
    app.run(debug=True)
