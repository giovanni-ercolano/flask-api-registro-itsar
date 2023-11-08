import requests

# Configura i dati di input (username e password)
input_data = {
    "username": "g.ercolano@itsrizzoli.it",
    "password": "131054"
}

# Invia una richiesta POST all'API
response = requests.post('http://127.0.0.1:5000/', json=input_data)  # Assicurati di utilizzare l'URL corretto

# Stampa la risposta
print(response.status_code)  # Codice di stato della risposta

data = response.json()
presenze_assenze = data['presenze_assenze']

# Utilizza un insieme per tenere traccia dei codici materia unici
codici_materia_set = set()

# Scansiona i dati di presenze_assenze e stampa i codici materia senza duplicati
for presenza in presenze_assenze:
    codice_materia = presenza["codice_materia"]
    if codice_materia not in codici_materia_set:
        print(codice_materia)
        codici_materia_set.add(codice_materia)
