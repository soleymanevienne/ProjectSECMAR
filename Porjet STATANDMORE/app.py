from flask import Flask, render_template, request
import folium
import io
import pandas as pd
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import base64
import seaborn as sns  
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')  # Maintenant, Flask cherchera les modèles dans le dossier 'templates'


# Définir la fonction sorted dans le contexte de rendu de modèle
@app.context_processor
def utility_processor():
    def custom_sorted(iterable):
        return sorted(iterable)
    return dict(sorted=custom_sorted)

# Charger les données
df_final = pd.read_csv(r"df_final.csv", low_memory=False)
df_final = df_final.dropna(subset=['latitude', 'longitude'])
df_final['latitude'] = pd.to_numeric(df_final['latitude'], errors='coerce')
df_final['longitude'] = pd.to_numeric(df_final['longitude'], errors='coerce')
df_final = df_final.dropna(subset=['latitude', 'longitude'])
df_final['type_operation'] = df_final['type_operation'].astype(str).replace('nan', 'Inconnu')
df_final['departement'] = df_final['departement'].astype(str).replace('nan', 'Inconnu')

# Obtenez les dates uniques de la colonne "date"
dates_uniques = sorted(df_final['date'].unique())
# Route pour la page 1 (page1.html)
@app.route('/page1')
def page1():
    return render_template('page1.html')

# Route pour la page 2 (page2.html)
@app.route('/page2')
def page2():
    return render_template('page2.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    # Filtres initiaux ou mis à jour
    type_operation = request.form.get('type_operation', 'Tous')
    departement = request.form.get('departement', 'Tous')
    evenement = request.form.get('evenement', 'Tous')
    date_intervention = request.form.get('date_intervention', '')
    saison = request.form.get('saison', 'Tous')
    operation_id = request.form.get('operation_id', '')
    nombre_personnes_tous_deces = request.form.get('nombre_personnes_tous_deces', '')
    resultat_humain = request.form.get('resultat_humain', '')
    categorie_personne = request.form.get('categorie_personne', '')
    nombre_personnes_tous_deces_ou_disparues = request.form.get('nombre_personnes_tous_deces_ou_disparues', '')
    pavillon = request.form.get('pavillon', '')
    date = request.form.get('date', 'Tous')
    zone_responsabilite = request.form.get('zone_responsabilite', 'Tous')
    autorite = request.form.get('autorite', 'Tous')
    categorie_evenement = request.form.get('categorie_evenement', 'Tous')
    cross = request.form.get('cross', 'Tous')
    date_debut = request.form.get('date_debut', '')
    date_fin = request.form.get('date_fin', '')

    # Filtrer les données en fonction des filtres
    filtered_data = df_final.copy()
    if type_operation != 'Tous':
        filtered_data = filtered_data[filtered_data['type_operation'] == type_operation]
    if departement != 'Tous':
        filtered_data = filtered_data[filtered_data['departement'] == departement]
    if evenement != 'Tous':
        filtered_data = filtered_data[filtered_data['evenement'] == evenement]
    if saison != 'Tous':
        filtered_data = filtered_data[filtered_data['saison'] == saison]
    if date_debut and date_fin:
        filtered_data = filtered_data[(filtered_data['date_heure_reception_alerte'] >= date_debut) & (filtered_data['date_heure_reception_alerte'] <= date_fin)]
    if pavillon != 'Tous':
        filtered_data = filtered_data[filtered_data['pavillon'] == pavillon]
    if date != 'Tous':
        filtered_data = filtered_data[filtered_data['date'] == date]
    if zone_responsabilite != 'Tous':
        filtered_data = filtered_data[filtered_data['zone_responsabilite'] == zone_responsabilite]
    if autorite != 'Tous':
        filtered_data = filtered_data[filtered_data['autorite'] == autorite]
    if categorie_evenement != 'Tous': 
        filtered_data = filtered_data[filtered_data['categorie_evenement'] == categorie_evenement]
    if cross != 'Tous':
        filtered_data = filtered_data[filtered_data['cross'] == cross]

    # Ajoutez d'autres filtres de données ici...

    # Prendre un échantillon après filtrage
    df_sample = filtered_data.sample(n=200, random_state=42) if len(filtered_data) > 1000 else filtered_data
    
    map1 = folium.Map(location=[20, 60], zoom_start=2, min_zoom=2, max_zoom=10, tiles='OpenStreetMap', max_bounds=True,
                  min_lon=-90, max_lon=120, min_lat=-100, max_lat=100)

    
    

    marker_cluster = MarkerCluster().add_to(map1)

    for _, row in df_sample.iterrows():
        popup_content = (
            f"<b>Événement:</b> {row['evenement']}<br>"
            f"<b>Type d'opération:</b> {row['type_operation']}<br>"
            f"<b>Département:</b> {row['departement']}<br>"
                        # Ajoutez d'autres informations de la ligne ici
        )
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_content,
            icon=folium.Icon(color='blue', icon='info', prefix='fa')
        ).add_to(marker_cluster)

    map_html = map1._repr_html_()

    # Générer le graphique en secteur interactif
    
    # Définir les paramètres par défaut de Matplotlib
    plt.rcParams.update({'text.color': 'white', 'axes.labelcolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'})

    # Générer le graphique en secteur interactif
    df_pie = filtered_data['evenement'].value_counts()
    plt.figure(figsize=(7, 3))  # Taille du graphique
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']  # Choix des couleurs
    plt.pie(df_pie, labels=df_pie.index, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops=dict(width=0.4))  # Ajout des couleurs et réglage de l'épaisseur des tranches
    plt.axis('equal')
    plt.tight_layout()

    # Ajouter une couleur de fond transparente
    plt.gca().set_facecolor('#1f2630')  # Définir la couleur de fond du graphique

    # Convertir le graphique en image pour l'afficher dans le template HTML
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True)  # Utiliser un fond transparent
    img_stream.seek(0)
    img_data = img_stream.getvalue()

    img_data_base64 = base64.b64encode(img_data).decode('utf-8')

    img_html = f'<img src="data:image/png;base64,{img_data_base64}" alt="Pie Chart">'

    plt.close()
    
    # Définir les paramètres par défaut de Matplotlib
    plt.rcParams.update({'text.color': '#1f2630', 'axes.labelcolor': '#1f2630', 'xtick.color': '#1f2630', 'ytick.color': '#1f2630'})


    # Grouper les données par 'categorie_flotteur' et compter les 'operation_id'
    bar_data = filtered_data.groupby('categorie_flotteur')['operation_id'].nunique().reset_index()

    # Trier les données pour un meilleur affichage
    bar_data = bar_data.sort_values('operation_id', ascending=False)

    # Création du graphique en barres avec Seaborn pour un style plus raffiné
    # Création du graphique en barres avec Seaborn pour un style plus raffiné
    plt.figure(figsize=(7, 6))
    bar_plot = sns.barplot(x='categorie_flotteur', y='operation_id', data=bar_data)

    # Rotation des étiquettes de l'axe des x pour une meilleure lisibilité
    plt.xticks(rotation=45, ha='right')

    # Ajout de titres et d'étiquettes
    plt.title('Nombre d\'opérations par type de flotteur')
    plt.xlabel('Catégorie de Flotteur')
    plt.ylabel('Nombre d\'Opérations')

    # Ajouter une couleur de fond transparente
    plt.gca().set_facecolor('#1f2630')  # Définir la couleur de fond du graphique

    # Rendre la légende opaque
    legend = plt.legend()
    legend.get_frame().set_alpha(1.0)  # Rendre la légende opaque
    for index, value in enumerate(bar_data['operation_id']):
        plt.text(index, value + 0.005 * max(bar_data['operation_id']), f'{value} operations', ha='center', va='bottom', color='white', fontsize=10)

    # Sauvegarder le graphique en barres dans un objet StringIO
    # Convertir le graphique en image pour l'afficher dans le template HTML
    bar_img_stream = io.BytesIO()
    plt.savefig(bar_img_stream, format='png', bbox_inches='tight')
    bar_img_stream.seek(0)
    bar_img_data = bar_img_stream.getvalue()

    # Encodage en base64 pour intégration dans le HTML
    bar_img_data_base64 = base64.b64encode(bar_img_data).decode('utf-8')
    # Ajouter un style CSS pour la couleur de fond et les couleurs de texte
    bar_chart_html = f'<img src="data:image/png;base64,{bar_img_data_base64}" alt="Bar Chart" style="max-width: 100%; height: auto; background-color: #1f2630; color: #1f2630;">'

    plt.close()


    # Rendre le template avec les données
    return render_template('template.html', df_final=df_final, type_operation=type_operation, departement=departement,
                           evenement=evenement, date_intervention=date_intervention, saison=saison,
                           operation_id=operation_id, nombre_personnes_tous_deces=nombre_personnes_tous_deces,
                           resultat_humain=resultat_humain, categorie_personne=categorie_personne,
                           nombre_personnes_tous_deces_ou_disparues=nombre_personnes_tous_deces_ou_disparues,
                           pavillon=pavillon, date=date, zone_responsabilite=zone_responsabilite,
                           autorite=autorite, categorie_evenement=categorie_evenement, cross=cross,
                           dates_uniques=dates_uniques, date_debut=date_debut, date_fin=date_fin,
                           map_html=map_html, img_html=img_html, bar_chart=bar_chart_html)
if __name__ == '__main__':
    app.run(debug=True)