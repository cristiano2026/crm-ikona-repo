from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Funzione per caricare i dati dei clienti da un file JSON
def load_clients():
    try:
        with open('clients.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Funzione per salvare i dati dei clienti in un file JSON
def save_clients(clients):
    with open('clients.json', 'w') as f:
        json.dump(clients, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clienti')
def clients_list():
    clients = load_clients()
    return render_template('clients.html', clients=clients)

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        clients = load_clients()
        new_client = {
            'id': len(clients) + 1,
            'nome': request.form['nome'],
            'email': request.form['email'],
            'telefono': request.form['telefono'],
            'partita_iva': request.form['partita_iva'],
            'indirizzo': request.form['indirizzo'],
            'citta': request.form['citta'],
            'cap': request.form['cap'],
            'codice_sdi': request.form['codice_sdi'],
            'agente': request.form['agente'],
            'call_center': request.form['call_center'],
            'referente_aziendale': request.form['referente_aziendale']
        }
        clients.append(new_client)
        save_clients(clients)
        return redirect(url_for('clients_list'))
    return render_template('add_client.html')

@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    clients = load_clients()
    client = next((c for c in clients if c['id'] == client_id), None)

    if client:
        if request.method == 'POST':
            client['nome'] = request.form['nome']
            client['email'] = request.form['email']
            client['telefono'] = request.form['telefono']
            client['partita_iva'] = request.form['partita_iva']
            client['indirizzo'] = request.form['indirizzo']
            client['citta'] = request.form['citta']
            client['cap'] = request.form['cap']
            client['codice_sdi'] = request.form['codice_sdi']
            client['agente'] = request.form['agente']
            client['call_center'] = request.form['call_center']
            client['referente_aziendale'] = request.form['referente_aziendale']
            save_clients(clients)
            return redirect(url_for('clients_list'))
        return render_template('edit_client.html', client=client, client_id=client_id)
    return redirect(url_for('clients_list'))

@app.route('/delete/<int:client_id>')
def delete_client(client_id):
    clients = load_clients()
    clients = [c for c in clients if c['id'] != client_id]
    save_clients(clients)
    return redirect(url_for('clients_list'))

if __name__ == '__main__':
    app.run(debug=True)
