from flask import Flask, render_template, request, redirect, url_for, flash
import uuid
# Importa le classi datetime e timedelta dal modulo datetime
from datetime import datetime, timedelta
# Importa il modulo calendar per i nomi dei mesi
import calendar

# Inizializza l'applicazione Flask
app = Flask(__name__)
# Imposta una chiave segreta per il funzionamento dei messaggi flash e delle sessioni
app.secret_key = 'chiave_segreta_molto_sicura'

# Registra il filtro 'date' per Jinja
@app.template_filter('date')
def date_format(value, format="%d/%m/%Y"):
    """Formatta un oggetto data in un formato stringa."""
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

# Funzione helper per generare i dettagli mensili
def generate_monthly_details(start_date, end_date):
    """
    Genera una lista di dizionari, uno per ogni mese tra le due date.
    Ogni dizionario include il mese, l'anno, il nome del mese, le note, le ore lavorate, l'importo pagato e le ore preventivate.
    """
    monthly_details = []
    current_date = start_date
    while current_date <= end_date:
        monthly_details.append({
            'month': current_date.month,
            'year': current_date.year,
            'month_name': calendar.month_name[current_date.month],
            'notes': '',  # Inizializza le note come stringa vuota
            'hours_worked': 0, # Campo per le ore lavorate
            'amount_paid': 0.0, # Campo per l'importo pagato
            'estimated_hours': 0 # Nuovo campo per le ore preventivate
        })
        # Sposta al primo giorno del mese successivo
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
    return monthly_details

# --- In-Memory Database (simulazione di un database) ---
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
        'created_at': datetime(2023, 1, 1)
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
        'created_at': datetime(2023, 2, 1)
    },
]

# --- NUOVO: Elenco di dati di esempio per i potenziali clienti ---
prospects = [
    {
        'id': str(uuid.uuid4()),
        'name': 'Gamma S.p.A.',
        'contact': 'Luca Verdi',
        'email': 'luca.verdi@gamma.it',
        'phone': '06-11223344',
        'notes': 'Interessato a sviluppo app mobile.',
        'preventivo': 'Preventivo iniziale per app iOS/Android inviato il 01/07/2024.',
        'graphic_quote_link': 'https://drive.google.com/file/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/view?usp=sharing' # Esempio di link
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Delta Tech',
        'contact': 'Sara Neri',
        'email': 'sara.neri@delta.com',
        'phone': '081-55667788',
        'notes': 'Richiesta di preventivo per campagna SEO.',
        'preventivo': 'Preventivo per campagna SEO base inviato il 15/06/2024.',
        'graphic_quote_link': '' # Nessun link per questo esempio
    }
]

services = [
    {'id': str(uuid.uuid4()), 'name': 'Sviluppo Sito Web', 'price': 1500, 'description': 'Creazione di un sito web responsivo.'},
    {'id': str(uuid.uuid4()), 'name': 'Campagna Social Media', 'price': 800, 'description': 'Gestione di profili social e campagne pubblicitarie.'},
]

# --- NUOVO: Elenco di dati di esempio per i collaboratori ---
collaborators = [
    {'id': str(uuid.uuid4()), 'name': 'Mario Rossi', 'role': 'Sviluppatore', 'email': 'mario.rossi@example.com', 'phone': '333-1234567'},
    {'id': str(uuid.uuid4()), 'name': 'Giulia Bianchi', 'role': 'Designer', 'email': 'giulia.bianchi@example.com', 'phone': '339-9876543'},
]

# --- STRUTTURA DATI PER COLLEGARE CLIENTI E SERVIZI ---
client_services = [
    {
        'id': str(uuid.uuid4()),
        'client_id': clients[0]['id'],
        'service_id': services[0]['id'],
        'subscribed_price': 1400.00,
        'start_date': datetime(2023, 1, 15),
        'end_date': datetime(2023, 12, 31),
        'notes': 'Sconto applicato per l\'anno intero.',
        # Aggiunta del campo monthly_details
        'monthly_details': generate_monthly_details(datetime(2023, 1, 15), datetime(2023, 12, 31))
    },
    {
        'id': str(uuid.uuid4()),
        'client_id': clients[0]['id'],
        'service_id': services[1]['id'],
        'subscribed_price': 750.00,
        'start_date': datetime(2023, 3, 1),
        'end_date': None,
        'notes': 'Contratto a tempo indeterminato.',
        # Per i contratti a tempo indeterminato, calcoliamo i mesi fino ad oggi
        'monthly_details': generate_monthly_details(datetime(2023, 3, 1), datetime.now())
    }
]


# --- Route per la Homepage ---
@app.route('/')
def index():
    """Renderizza la pagina principale del sito."""
    return render_template('index.html')
    
# --- Route per la Rubrica Clienti (vecchia, da rimuovere o reindirizzare se non più usata) ---
@app.route('/rubrica')
def show_address_book():
    """Renderizza la pagina con la rubrica dei clienti."""
    # Passa la lista completa dei clienti al template
    return render_template('address_book.html', clients=clients)

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
        
        client_name = form_data.get('nome')
        
        if client_name:
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
                'created_at': datetime.now()
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
    Renderizza la pagina con i dettagli di un singolo cliente e la lista dei suoi servizi.
    """
    client = next((item for item in clients if item['id'] == client_id), None)
    if not client:
        flash('Cliente non trovato.', 'error')
        return redirect(url_for('show_clients'))

    client_services_with_details = []
    for cs in client_services:
        if cs['client_id'] == client_id:
            service = next((s for s in services if s['id'] == cs['service_id']), None)
            if service:
                combined_service = {
                    'id': cs['id'],
                    'service': service,
                    'subscribed_price': cs['subscribed_price'],
                    'start_date': cs['start_date'],
                    'end_date': cs['end_date'],
                    'notes': cs['notes']
                }
                client_services_with_details.append(combined_service)

    return render_template('client_detail.html', client=client, services=client_services_with_details)


# --- Route per modificare un cliente esistente ---
@app.route('/edit_client/<string:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    """
    Gestisce la modifica di un cliente.
    """
    client = next((item for item in clients if item['id'] == client_id), None)

    if not client:
        flash('Cliente non trovato.', 'error')
        return redirect(url_for('show_clients'))

    if request.method == 'POST':
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

    return render_template('edit_client.html', client=client)

# --- Route per eliminare un cliente ---
@app.route('/delete_client/<string:client_id>')
def delete_client(client_id):
    """Elimina un cliente dalla lista."""
    global clients, client_services
    clients = [client for client in clients if client['id'] != client_id]
    client_services = [cs for cs in client_services if cs['client_id'] != client_id]
    flash('Cliente eliminato con successo!', 'success')
    return redirect(url_for('show_clients'))

# --- ROTTE PER LA GESTIONE DEI SERVIZI ---
@app.route('/services')
def show_services():
    """Renderizza la pagina con la lista dei servizi."""
    return render_template('services.html', services=services)

@app.route('/add_service', methods=['GET', 'POST'])
def add_service_route():
    """
    Gestisce l'aggiunta di un nuovo servizio.
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

@app.route('/services/<string:service_id>')
def view_service_detail(service_id):
    """Renderizza la pagina con i dettagli di un singolo servizio."""
    service = next((item for item in services if item['id'] == service_id), None)
    if service:
        return render_template('view_service.html', service=service)
    else:
        flash('Servizio non trovato.', 'error')
        return redirect(url_for('show_services'))

@app.route('/edit_service/<string:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    """
    Gestisce la modifica di un servizio esistente.
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

@app.route('/delete_service/<string:service_id>')
def delete_service(service_id):
    """Elimina un servizio dalla lista."""
    global services, client_services
    services = [service for service in services if service['id'] != service_id]
    client_services = [cs for cs in client_services if cs['service_id'] != service_id]
    flash('Servizio eliminato con successo!', 'success')
    return redirect(url_for('show_services'))


# --- ROTTE PER LA GESTIONE DEI SERVIZI PER CLIENTE ---
@app.route('/clients/<string:client_id>/add_service', methods=['GET', 'POST'])
def add_client_service(client_id):
    """
    Gestisce l'associazione di un servizio a un cliente.
    """
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
                'notes': notes,
                # Chiamiamo la funzione per inizializzare il campo monthly_details
                'monthly_details': generate_monthly_details(start_date, end_date if end_date else datetime.now())
            }
            client_services.append(new_client_service)
            flash('Servizio aggiunto con successo!', 'success')
            return redirect(url_for('show_client', client_id=client_id))

        except (ValueError, TypeError) as e:
            flash(f'Errore nel formato dei dati: {e}', 'error')
            return redirect(url_for('add_client_service', client_id=client['id']))

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
        client_service['service_id'] = request.form.get('service_id')
        client_service['subscribed_price'] = float(request.form.get('subscribed_price'))
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        client_service['notes'] = request.form.get('notes')
        
        client_service['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d')
        client_service['end_date'] = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # Rigenera i dettagli mensili se le date sono cambiate
        client_service['monthly_details'] = generate_monthly_details(
            client_service['start_date'], 
            client_service['end_date'] if client_service['end_date'] else datetime.now()
        )

        flash('Servizio cliente modificato con successo!', 'success')
        return redirect(url_for('show_client', client_id=client_id))

    return render_template('edit_client_service.html', client=client, client_service=client_service, available_services=services)

@app.route('/clients/<string:client_id>/delete_service/<string:client_service_id>', methods=['POST'])
def delete_client_service(client_id, client_service_id):
    """
    Elimina un servizio associato a un cliente.
    """
    global client_services
    client_services = [cs for cs in client_services if cs['id'] != client_service_id]
    flash('Servizio rimosso dal cliente con successo!', 'success')
    return redirect(url_for('show_client', client_id=client_id))


# --- NUOVA ROTTA PER VISUALIZZARE UN SERVIZIO CLIENTE ---
@app.route('/clients/<string:client_id>/view_service/<string:client_service_id>')
def view_client_service(client_id, client_service_id):
    """
    Renderizza la pagina con i dettagli di un servizio associato a un cliente.
    """
    client = next((c for c in clients if c['id'] == client_id), None)
    client_service = next((cs for cs in client_services if cs['id'] == client_service_id), None)

    if not client or not client_service:
        flash('Cliente o servizio associato non trovato.', 'error')
        return redirect(url_for('show_clients'))

    service = next((s for s in services if s['id'] == client_service['service_id']), None)
    
    if not service:
        flash('Dettagli del servizio non trovati.', 'error')
        return redirect(url_for('show_client', client_id=client_id))

    return render_template('view_client_service.html', client=client, client_service=client_service, service=service)

# --- NUOVA ROTTA: Gestisce il salvataggio delle note mensili e delle ore lavorate ---
@app.route('/clients/<string:client_id>/save_monthly_notes/<string:client_service_id>', methods=['POST'])
def save_monthly_notes(client_id, client_service_id):
    """
    Salva le note mensili, le ore lavorate e l'importo pagato inviate tramite il form.
    """
    client_service = next((cs for cs in client_services if cs['id'] == client_service_id), None)
    if not client_service:
        flash('Servizio cliente non trovato.', 'error')
        return redirect(url_for('show_client', client_id=client_id))
    
    for i, month_data in enumerate(client_service['monthly_details']):
        notes_field_name = f"note_{month_data['year']}_{month_data['month']}"
        hours_field_name = f"hours_{month_data['year']}_{month_data['month']}"
        amount_paid_field_name = f"amount_paid_{month_data['year']}_{month_data['month']}"
        estimated_hours_field_name = f"estimated_hours_{month_data['year']}_{month_data['month']}"
        
        new_notes = request.form.get(notes_field_name)
        new_hours_worked = request.form.get(hours_field_name)
        new_amount_paid = request.form.get(amount_paid_field_name)
        new_estimated_hours = request.form.get(estimated_hours_field_name)

        if new_notes is not None:
            client_service['monthly_details'][i]['notes'] = new_notes
        
        if new_hours_worked is not None:
            try:
                client_service['monthly_details'][i]['hours_worked'] = float(new_hours_worked)
            except ValueError:
                flash(f"Errore: Il valore inserito per le ore di {month_data['month_name']} non è un numero valido.", 'error')

        if new_amount_paid is not None:
            try:
                client_service['monthly_details'][i]['amount_paid'] = float(new_amount_paid)
            except ValueError:
                flash(f"Errore: Il valore inserito per l'importo di {month_data['month_name']} non è un numero valido.", 'error')
                
        if new_estimated_hours is not None:
            try:
                client_service['monthly_details'][i]['estimated_hours'] = float(new_estimated_hours)
            except ValueError:
                flash(f"Errore: Il valore inserito per le ore preventivate di {month_data['month_name']} non è un numero valido.", 'error')


    flash('Dettagli mensili salvati con successo!', 'success')
    return redirect(url_for('view_client_service', client_id=client_id, client_service_id=client_service_id))

# --- NUOVE ROTTE PER LA GESTIONE DEI COLLABORATORI ---
@app.route('/collaboratori')
def show_collaborators():
    """Renderizza la pagina con la rubrica dei collaboratori."""
    return render_template('collaborators.html', collaborators=collaborators)

@app.route('/add_collaborator', methods=['GET', 'POST'])
def add_collaborator():
    """Gestisce l'aggiunta di un nuovo collaboratore."""
    if request.method == 'POST':
        form_data = request.form
        name = form_data.get('name')
        
        if name:
            new_collaborator = {
                'id': str(uuid.uuid4()),
                'name': name,
                'role': form_data.get('role', ''),
                'email': form_data.get('email', ''),
                'phone': form_data.get('phone', '')
            }
            collaborators.append(new_collaborator)
            flash(f'Collaboratore "{name}" aggiunto con successo!', 'success')
            return redirect(url_for('show_collaborators'))
        else:
            flash('Errore: Il campo "Nome" è obbligatorio.', 'error')
            
    return render_template('add_collaborator.html')

# --- NUOVE ROTTE PER LA GESTIONE DEI POTENZIALI CLIENTI ---
@app.route('/prospects')
def show_prospects():
    """Renderizza la pagina con la lista dei potenziali clienti."""
    return render_template('prospects.html', prospects=prospects)

@app.route('/add_prospect', methods=['GET', 'POST'])
def add_prospect():
    """
    Gestisce l'aggiunta di un nuovo potenziale cliente.
    GET: Mostra il form per l'inserimento.
    POST: Elabora i dati del form e aggiunge il potenziale cliente alla lista.
    """
    form_data = {}
    if request.method == 'POST':
        form_data = request.form
        prospect_name = form_data.get('name')
        
        if prospect_name:
            new_prospect = {
                'id': str(uuid.uuid4()),
                'name': prospect_name,
                'contact': form_data.get('contact', ''), # Nuovo campo referente aziendale
                'email': form_data.get('email', ''),
                'phone': form_data.get('phone', ''),
                'notes': form_data.get('notes', ''), # Nuovo campo note
                'preventivo': form_data.get('preventivo', ''), # Nuovo campo preventivo
                'graphic_quote_link': form_data.get('graphic_quote_link', ''), # NUOVO CAMPO: link preventivo grafico
                'created_at': datetime.now() # Data di creazione
            }
            prospects.append(new_prospect)
            flash(f'Potenziale Cliente "{prospect_name}" aggiunto con successo!', 'success')
            return redirect(url_for('show_prospects'))
        else:
            flash('Errore: Il campo "Nome" è obbligatorio.', 'error')
    return render_template('add_prospect.html', form_data=form_data)

@app.route('/edit_prospect/<string:prospect_id>', methods=['GET', 'POST'])
def edit_prospect(prospect_id):
    """
    Gestisce la modifica di un potenziale cliente esistente.
    """
    prospect = next((item for item in prospects if item['id'] == prospect_id), None)

    if not prospect:
        flash('Potenziale Cliente non trovato.', 'error')
        return redirect(url_for('show_prospects'))

    if request.method == 'POST':
        prospect['name'] = request.form.get('name')
        prospect['contact'] = request.form.get('contact')
        prospect['email'] = request.form.get('email')
        prospect['phone'] = request.form.get('phone')
        prospect['notes'] = request.form.get('notes')
        prospect['preventivo'] = request.form.get('preventivo')
        prospect['graphic_quote_link'] = request.form.get('graphic_quote_link') # Salva il campo preventivo grafico
        flash('Potenziale Cliente modificato con successo!', 'success')
        return redirect(url_for('show_prospects'))

    return render_template('edit_prospect.html', prospect=prospect)

@app.route('/delete_prospect/<string:prospect_id>')
def delete_prospect(prospect_id):
    """Elimina un potenziale cliente dalla lista."""
    global prospects
    prospects = [p for p in prospects if p['id'] != prospect_id]
    flash('Potenziale Cliente eliminato con successo!', 'success')
    return redirect(url_for('show_prospects'))


# --- Avvia l'applicazione ---
if __name__ == '__main__':
    app.run(debug=True)
