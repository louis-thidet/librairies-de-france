import branca
import folium
from folium.plugins import MarkerCluster
from pathlib import Path
import pandas as pd
import requests


# =============================================================#
# ================== CHARGEMENT DES DONNEES ================== #
# =============================================================#

def bookshop_locations():
    data_path = Path("data/librairies_francaises_2018.csv")
    # Si les données ne sont pas téléchargées
    if not data_path.is_file():
        url = "https://www.data.gouv.fr/fr/datasets/r/18ecebc7-febd-48ab-9f51-db4623617905"
        response = requests.get(url)  # Télécharger les données
        response.raise_for_status()  # Vérifier s'il y a des erreurs
        with open(data_path, "wb") as file:
            file.write(response.content)
    # Charger les données dans un DataFrame
    df = pd.read_csv(data_path, encoding="UTF-8", on_bad_lines="skip", delimiter=";")
    # Convertir les coordonnées au format numérique
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    # Supprimer les données dont les coordonnées n'ont pas pu être converties
    df = df.dropna(subset=["latitude", "longitude"])
    return df


# =============================================================#
# =============== LOCALISATION DES LIBRAIRIES ================ #
# =============================================================#

def creer_carte(df):
    # Tuile personnalisée
    tiles = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
    attr = ("&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors &copy; <a "
            "href='https://carto.com/attributions'>CARTO</a>")

    # Création de la carte
    m = folium.Map(location=(46.5, 2.5),
                   no_wrap=True,
                   tiles=tiles,
                   attr=attr,
                   attributionControl=False,
                   zoom_start=5,
                   min_zoom=3,
                   zoom_control=False,
                   max_bounds=True)

    # Créer des clusters de marqueurs
    marker_cluster = MarkerCluster().add_to(m)

    # Pour chaque librairie (chaque ligne de donnée)
    for idx, row in df.iterrows():
        # Texte de recherche pour Google Map
        search_text = f"librairie {row['Designation']} {row['result_label']}".replace(" ", "+")
        # Création d'un lien pour rechercher la librairie sur Google Map
        google_maps_url = f"https://www.google.com/maps/search/{search_text}/@{row['latitude']},{row['longitude']}"
        # Création d'une fenêtre contextuelle
        html = f"""
            <html>
                <head>
                    <style>
                      body {{ font-family: "Roboto", sans-serif; font-size: 14px; }}
                        p {{ margin: 5px 0; }}
                    </style>
                </head>
                <body>
                    <p><b>Nom :</b> {row["Designation"]}</p>
                    <p><b>Adresse :</b> {row["Adresse"]}</p>
                    <p>Voir sur <a href="{google_maps_url}" target="_blank">Google Maps</a></p>
                </body>
            </html>
            """
        # Insertion du code HTML dans un Iframe
        iframe = branca.element.IFrame(html=html, width=270, height=100)
        popup = folium.Popup(iframe)

        # Ajout du marqueur de la librairie avec la fenêtre contextuelle aux clusters de marqueurs
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup,
            icon=folium.Icon(color="red", icon="glyphicon-book")
        ).add_to(marker_cluster),

    # Enregistrement de la carte : il faut l'enregistrer pour la lire et récupérer en tant que variable html
    m_path = "carte_librairies.html"
    m.save(m_path)
    # Lecture de la variable : la variable obtenue va pouvoir être insérée dans un iframe (l'iframe contient du html)
    with open(m_path, "r") as f:
        m_html = f.read()
    return m_html
