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



def load_csv(filepath, header=None, skiprows=0, names=None, dtype=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_data = f.read()
    cleaned_lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
    df = pd.read_csv(StringIO('\n'.join(cleaned_lines)), header=header, skiprows=skiprows, names=names, dtype=dtype)
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





def map_titles_to_labels(grand_livre_df, pcg_df, socketio):

    
    # Filtrer les données pour ne garder que celles de l'année 2021 (ou toute autre condition)
    grand_livre_df['date'] = pd.to_datetime(grand_livre_df['date'])
    grand_livre_df = grand_livre_df[grand_livre_df['date'].dt.year == 2021]

    grand_livre_df = grand_livre_df.copy()
    print(grand_livre_df)

    # Ajout des nouvelles colonnes avec des valeurs par défaut vides
    for i in range(1, 4):
        grand_livre_df[f'mapped_categorie_{i}'] = ''

    pcg_df['compte_code'] = pcg_df['compte_code'].astype(str)

    # Initialiser le total des lignes pour le calcul de la progression
    total_rows = len(grand_livre_df)

    # Boucle sur chaque ligne de DataFrame pour le mapping
    for index, row in tqdm(grand_livre_df.iterrows(), total=total_rows, desc='Mapping progress'):
        compte = str(row['compte'])
        levels = [compte[:i] for i in range(2, len(compte) + 1)]

        for i, level in enumerate(levels, start=1):
            matches = pcg_df[pcg_df['compte_code'].str.startswith(level)]
            if not matches.empty:
                categorie = matches.iloc[0]['categorie']
                if i <= 3:
                    grand_livre_df.at[index, f'mapped_categorie_{i}'] = categorie
                else:
                    break

        # Calculer la progression et envoyer à travers SocketIO
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

        grand_livre_df = load_csv(csv_path, header=0)
        grand_livre_df = map_titles_to_labels(grand_livre_df, pcg_df, socketio)

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
