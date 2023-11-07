from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import datetime
import json


app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    try:
        username = request.json['username']
        password = request.json['password']
    except KeyError:
        return jsonify({'error': 'username or password missing'}), 400
    r = requests.Session()
    login_data = {
        'username': username,
        'password': password
    }
    try:
        r.post(
            'https://itsar.registrodiclasse.it/geopcfp2/update/login.asp?1=1&ajax_target=DIVHidden&ajax_tipotarget=login',
            data=login_data)
        req = r.get('https://itsar.registrodiclasse.it/geopcfp2/ajax/page/home.asp?1=1&ajax_target=DIVContenuto&ajax_tipotarget=home&z=1681492254027', cookies=r.cookies)
        midSoup = BeautifulSoup(req.content, 'html.parser')
        div = midSoup.find('div', class_='fullcalendar')
        id_alunno = div['data-id-oggetto']
        reqq = r.get('https://itsar.registrodiclasse.it/geopcfp2/ajax/page/voti_alunno.asp?1=1&ajax_target=DIVContenuto&ajax_tipotarget=voti_alunno&z=1681578054110', cookies=r.cookies)
        midLateSoup = BeautifulSoup(reqq.content, 'html.parser')
        input_tag = midLateSoup.find('input', {'id': 'LoadScriptDIVContenuto'})
        value_attribute = input_tag['value']
        iDCorsoAnno = value_attribute.split(',')[2].strip()
        requ = r.get(
            f'https://itsar.registrodiclasse.it/geopcfp2/ajax/page/componenti/voti_tabella.asp?idAlunno={id_alunno}&idMateria=&idCorsoAnno={iDCorsoAnno}&id=&idUtenteCreazione=&ajax_target=DIV210_&ajax_tipotarget=undefined&z=1680172204309',
            cookies=r.cookies)
    except:
        return jsonify({'error': 'could not access'}), 500
    soup = BeautifulSoup(requ.text, 'html.parser')
    grades = []
    subjects = []
    for row in soup.find_all('tr')[1:]:
        subject = row.td.span.text.strip()
        subjects.append(subject)
        grade = row.findChildren()[2].findChildren()[2].b.text.strip()
        if (grade == "30 lode"):
            grade = 32
        grade = int(grade)
        grades.append(grade)
    materia_voto = res = dict(zip(subjects, grades))
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=30*8) # subtract 8 months
    end_date = today + datetime.timedelta(days=30*8) # add 8 months
    start_date_def = start_date.strftime('%Y-%m-%d')
    end_date_def = end_date.strftime('%Y-%m-%d')

    annoAccademicoBase = 13;  #primo anno
    annoAccademico = annoAccademicoBase
    august_15 = datetime.date(datetime.date.today().year, 8, 15)
    if today > august_15:
        annoAccademico += 1

    try:
        cal = r.get(f'https://itsar.registrodiclasse.it/geopcfp2/json/fullcalendar_events_alunno.asp?Oggetto=idAlunno&idOggetto=2538&editable=false&z=1680542264288&start={start_date_def}&end={end_date_def}&_=1680542231937').text.strip()
    except:
        return jsonify({'error': 'could not access'}), 500
    calendario = json.loads(cal)
    for event in calendario:
        tooltip_info = event['tooltip'].split("<br>")
        for info in tooltip_info:
            if "Aula:" in info:
                event['aula'] = info.split(": ")[1]
        del event['id']
        del event['borderColor']
        del event['backgroundColor']
        del event['rendering']
        del event['overlap']
        del event['editable']
        del event['ClasseEvento']
        del event['tooltip']
        del event['icon']
    try:
        f_header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'referer': 'https://itsar.registrodiclasse.it/geopcfp2/registri_ricerca.asp',
        'origin': 'https://itsar.registrodiclasse.it',
        'accept': 'application / json, text / javascript, * / *; q = 0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest',
        }
        payload = {
        'draw': '1',
        'columns[0][data]': 'idRegistroAlunno',
        'columns[0][name]': 'idRegistroAlunno',
        'columns[0][searchable]': 'true',
        'columns[0][orderable]': 'true',
        'columns[0][search][value]': '',
        'columns[0][search][regex]': 'false',
        'columns[1][data]': 'Giorno',
        'columns[1][name]': 'Giorno',
        'columns[1][searchable]': 'true',
        'columns[1][orderable]': 'true',
        'columns[1][search][value]': '',
        'columns[1][search][regex]': 'false',
        'columns[2][data]': 'Data',
        'columns[2][name]': 'Data',
        'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true',
        'columns[2][search][value]': '',
        'columns[2][search][regex]': 'false',
        'columns[3][data]': 'DataOraInizio',
        'columns[3][name]': 'DataOraInizio',
        'columns[3][searchable]': 'true',
        'columns[3][orderable]': 'true',
        'columns[3][search][value]': '',
        'columns[3][search][regex]': 'false',
        'columns[4][data]': 'DataOraFine',
        'columns[4][name]': 'DataOraFine',
        'columns[4][searchable]': 'true',
        'columns[4][orderable]': 'true',
        'columns[4][search][value]': '',
        'columns[4][search][regex]': 'false',
        'columns[5][data]': 'MinutiPresenza',
        'columns[5][name]': 'MinutiPresenza',
        'columns[5][searchable]': 'true',
        'columns[5][orderable]': 'true',
        'columns[5][search][value]': '',
        'columns[5][search][regex]': 'false',
        'columns[6][data]': 'MinutiAssenza',
        'columns[6][name]': 'MinutiAssenza',
        'columns[6][searchable]': 'true',
        'columns[6][orderable]': 'true',
        'columns[6][search][value]': '',
        'columns[6][search][regex]': 'false',
        'columns[7][data]': 'CodiceMateria',
        'columns[7][name]': 'CodiceMateria',
        'columns[7][searchable]': 'true',
        'columns[7][orderable]': 'true',
        'columns[7][search][value]': '',
        'columns[7][search][regex]': 'false',
        'columns[8][data]': 'Materia',
        'columns[8][name]': 'Materia',
        'columns[8][searchable]': 'true',
        'columns[8][orderable]': 'true',
        'columns[8][search][value]': '',
        'columns[8][search][regex]': 'false',
        'columns[9][data]': 'CognomeDocente',
        'columns[9][name]': 'CognomeDocente',
        'columns[9][searchable]': 'true',
        'columns[9][orderable]': 'true',
        'columns[9][search][value]': '',
        'columns[9][search][regex]': 'false',
        'columns[10][data]': 'Docente',
        'columns[10][name]': 'Docente',
        'columns[10][searchable]': 'true',
        'columns[10][orderable]': 'true',
        'columns[10][search][value]': '',
        'columns[10][search][regex]': 'false',
        'columns[11][data]': 'DataGiustificazione',
        'columns[11][name]': 'DataGiustificazione',
        'columns[11][searchable]': 'true',
        'columns[11][orderable]': 'true',
        'columns[11][search][value]': '',
        'columns[11][search][regex]': 'false',
        'columns[12][data]': 'Note',
        'columns[12][name]': 'Note',
        'columns[12][searchable]': 'true',
        'columns[12][orderable]': 'true',
        'columns[12][search][value]': '',
        'columns[12][search][regex]': 'false',
        'columns[13][data]': 'idLezione',
        'columns[13][name]': 'idLezione',
        'columns[13][searchable]': 'true',
        'columns[13][orderable]': 'true',
        'columns[13][search][value]': '',
        'columns[13][search][regex]': 'false',
        'columns[14][data]': 'idAlunno',
        'columns[14][name]': 'idAlunno',
        'columns[14][searchable]': 'true',
        'columns[14][orderable]': 'true',
        'columns[14][search][value]': '',
        'columns[14][search][regex]': 'false',
        'columns[15][data]': 'DeveGiustificare',
        'columns[15][name]': 'DeveGiustificare',
        'columns[15][searchable]': 'true',
        'columns[15][orderable]': 'true',
        'columns[15][search][value]': '',
        'columns[15][search][regex]': 'false',
        'order[0][column]': '2',
        'order[0][dir]': 'desc',
        'order[1][column]': '3',
        'order[1][dir]': 'desc',
        'start': '0',
        'length': '10000',
        'search[value]': '',
        'search[regex]': 'false',
        'NumeroColonne': '15',
        "idAnnoAccademicoFiltroRR": [13, 14],  #in base a questo numero vediamo le assenze dei vari anni, il primo anno era il 13
        "MateriePFFiltroRR": 0,
        "idTipologiaLezioneFiltroRR": "",
        "RisultatiPagina": 10000,
        "SuffissoCampo": "FiltroRR",
        "Oggetto": "",
        "idScheda": "",
        "NumeroPagina": 1,
        "OrderBy": "DataOraInizio",
        "ajax_target": "DIVRisultati",
        "ajax_tipotarget": "elenco_ricerca_registri",
        "z": 1681895380050
        }
        presenze = r.post('https://itsar.registrodiclasse.it/geopcfp2/json/data_tables_ricerca_registri.asp', headers=f_header, data=payload).text
    except:
        return jsonify({'error': 'could not access'}), 500
    pres1 = presenze.replace("\r", "")
    pres2 = pres1.replace("\n", "")
    pres3 = pres2.replace("\t", "")
    pres4 = pres3.replace("\\", "")
    pres5 = pres4.replace('<a href="javascript: ModalLezione(', '')
    pres6 = pres5.replace('class="btn btn-xs btn-danger btn-block jq-tooltip" Title="Assente<br>Apri scheda lezione">A</a>"', '')
    pres7 = pres6.replace('class="btn btn-xs btn-success btn-block jq-tooltip" Title="Presente<br>Apri scheda lezione">P</a>"', '')
    pres8 = pres7.replace('Ã\xa0', 'à').replace(' h', '').replace(' min', '')
    data = json.loads(pres8)['data']
    presenze_assenze = []

    for item in data:
        codice_materia = item['CodiceMateria']
        materia = item['Materia']
        presenza = float(item['MinutiPresenza'].replace(' ', '.'))
        assenza = float(item['MinutiAssenza'].replace(' ', '.'))
        date = item['Data']
        ora_inizio = item['DataOraInizio']
        ora_fine = item['DataOraFine']
        presenza = {
            "codice_materia": codice_materia,
            "materia": materia,
            "ore_presenza": presenza,
            "ore_assenza": assenza,
            "date": date,
            "ora_inizio": ora_inizio,
            "ora_fine": ora_fine
        }
        presenze_assenze.append(presenza)

    final_result = {
        'voti': materia_voto,
        'calendario': calendario,
        'presenze_assenze': presenze_assenze
    }


    return jsonify(final_result)

if __name__ == '__main__':
  app.run(port=5000)
