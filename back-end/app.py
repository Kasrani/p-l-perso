import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from io import StringIO
from tqdm import tqdm
from werkzeug.utils import secure_filename
import os
from flask_socketio import SocketIO, emit
from flask_cors import cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://aidviz-frontend.onrender.com", "http://localhost:3000"]}})
socketio = SocketIO(app, cors_allowed_origins="*")


# Chemins des dossiers
UPLOAD_FOLDER = './upload'
RESULT_FOLDER = './result'
pcg_filepath = './data/plan-comptable-francais-excel.csv'
output_csv_filepath = os.path.join(RESULT_FOLDER, 'mapped_grand_livre.csv')



def load_csv(filepath, header=None, skiprows=0, names=None, dtype=None, usecols=None, compte_filter=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_data = f.read()
    cleaned_lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
    df = pd.read_csv(StringIO('\n'.join(cleaned_lines)), header=header, skiprows=skiprows, names=names, dtype=dtype, usecols=usecols)
    
    # Filtrage basé sur les numéros de compte, si nécessaire
    if compte_filter is not None:
        df = df[df['compte'].astype(str).str.startswith(tuple(compte_filter))]
    
    return df


# Chargement du DataFrame avec type spécifié
pcg_df = load_csv(pcg_filepath, header=None, dtype={'compte_code': str})
pcg_df.columns = ['compte_code', 'categorie']

print(pcg_df.head())  # Pour vérifier les premières lignes du DataFrame
print(pcg_df.dtypes)  # Pour vérifier les types de données des colonnes


@app.route('/submit-csv-link', methods=['POST'])
@cross_origin(origins=["https://aidviz-frontend.onrender.com", "http://localhost:3000"])
def submit_csv_link():
    global grand_livre_df

    data = request.get_json()
    csv_link = data.get('link')
    pcg_df = load_csv(pcg_filepath, header=None, dtype={'compte_code': str})
    pcg_df.columns = ['compte_code', 'categorie']

    grand_livre_df = load_csv(csv_link, header=0)
    grand_livre_df = map_titles_to_labels(grand_livre_df, pcg_df)

    if not os.path.exists(RESULT_FOLDER):
        os.makedirs(RESULT_FOLDER)
    grand_livre_df.to_csv(output_csv_filepath, index=False)

    return jsonify({'message': 'Lien du fichier CSV soumis avec succès.'})


pcg_df['compte_code'] = pcg_df['compte_code'].astype(str)
mapping_dict = pcg_df.set_index('compte_code')['categorie'].to_dict()

def map_titles_to_labels(grand_livre_df, mapping_dict, socketio):
    # Préparation des colonnes pour le mappage
    for i in range(1, 4):
        grand_livre_df[f'mapped_categorie_{i}'] = ''

    # Fonction pour effectuer le mappage
    def map_category(row, mapping_dict):
        compte = str(row['compte'])
        matched = False

        # Mappage pour la catégorie de niveau 1 basé sur deux chiffres du compte
        code = compte[:2]
        if code in mapping_dict:
            row['mapped_categorie_1'] = mapping_dict[code]
            matched = True

        # Boucle à l'envers pour commencer par la correspondance la plus longue pour les catégories suivantes
        for i in range(len(compte), 2, -1):
            code = compte[:i]
            if code in mapping_dict and not matched:
                row['mapped_categorie_2'] = mapping_dict[code]
                matched = True
            elif code in mapping_dict and matched:
                row['mapped_categorie_3'] = mapping_dict[code]
                break  # Sortir de la boucle une fois la catégorie de niveau 3 mappée

        return row

    # Application du mappage en utilisant apply
    grand_livre_df = grand_livre_df.apply(lambda row: map_category(row, mapping_dict), axis=1)

    # Envoi de la progression via SocketIO
    total_rows = len(grand_livre_df)
    for index in range(total_rows):
        progress = int((index / total_rows) * 100)
        socketio.emit('progress', {'progress': progress}, namespace='/')

    return grand_livre_df





@app.route('/submit-csv-file', methods=['POST'])
@cross_origin(origins=["https://aidviz-frontend.onrender.com", "http://localhost:3000"])
def submit_csv_file():
    global grand_livre_df

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(RESULT_FOLDER):
        os.makedirs(RESULT_FOLDER)

    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier trouvé.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné.'}), 400

    if file:
        filename = secure_filename(file.filename)
        csv_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(csv_path)

        pcg_df = load_csv(pcg_filepath, header=None, dtype={'compte_code': str})
        pcg_df.columns = ['compte_code', 'categorie']

        cols_to_load = ['date', 'compte', 'libelleCompte', 'debit', 'credit']
        compte_startswith = ['6', '7']

        grand_livre_df = load_csv(csv_path, header=0, usecols=cols_to_load, compte_filter=compte_startswith)
        grand_livre_df = map_titles_to_labels(grand_livre_df, mapping_dict, socketio)

        grand_livre_df.to_csv(output_csv_filepath, index=False)

        return jsonify({'message': 'Fichier CSV soumis avec succès.'})

    return jsonify({'error': 'Erreur lors du chargement du fichier.'}), 500


@app.route('/mapping-results', methods=['GET'])
@cross_origin(origins=["https://aidviz-frontend.onrender.com", "http://localhost:3000"])
def get_mapping_results():
    # Charger les résultats de mapping depuis le fichier CSV sauvegardé
    try:
        mapping_results_df = pd.read_csv(output_csv_filepath)
        return mapping_results_df.to_json(orient='records')
    except FileNotFoundError:
        return jsonify({'error': 'Aucun fichier de résultat trouvé.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
