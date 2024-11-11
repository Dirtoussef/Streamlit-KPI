import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from PIL import Image
from ipywidgets import interact, widgets
from IPython.display import display
from streamlit_folium import folium_static 
from streamlit_navigation_bar import st_navbar                                        
from matplotlib import cm
import matplotlib.pyplot as plt

from Classes.carte_clients import show_clients_map

from Classes.segmentation import show_segmentation
from Classes.Home import show_Home,etiquettes
from Classes.Dataserver import get_data_from_sql
from Classes.Audience import show_Audience
from Classes.Dataquality import Dataquality
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    body {
        font-family: 'Serif';
    }
    .stApp {
        background-color: #FFFFFF;
    }
    .sidebar .sidebar-content {
        background-color: #33607B;
    }
    /* Custom styles for metric labels and values */
    .metric-container {
        color: black !important;
        font-weight: bold;
    }
    .metric-label {
        color: black !important;
        font-size: large !important;
    }
    .metric-value {
        color: black !important;
        font-size: x-large !important;
    }.sidebar .sidebar-content {
        text-color: #FFFFFF;
    </style>
    """, unsafe_allow_html=True)

selected = st_navbar(["Home", "Carte", "Audience","Segmentation","Data quality",'IA'])


logo_image = Image.open("Images/avanci_logo.jfif")
logo_resized = logo_image.resize((50, 50))


# Affichage du logo dans la barre latérale

with st.sidebar:
    col1,col2= st.columns([0.8,3])
    col1.image(logo_resized)
    col2.markdown('<span style="font-weight: bold; font-size: large; display: inline-block; vertical-align: middle;">AVANCI</span>', unsafe_allow_html=True)
    
   



            
           

@st.cache_data

def fetch_data():
    return get_data_from_sql()

df_segmentation, df_contact, df_entete,df_adresse,df_ligne,df_email,df_telephone,df_media_invalide= get_data_from_sql()




(Total_CA_actu,Total_CA_prec,percentage_change_CA,Actifs_sorted,tota_Actif_actu,percentage_change_actif,CA_per_semestre,Actifs,Total_commandes,
 panier, panier_sorted,total_panier_actu,total_panier_prec,percentage_change_panier,freq_sorted, freq_actu,percentage_change_freq,annee) = etiquettes(df_entete)

## carte geographique selon les carte postaux
df_departements = pd.read_csv('departements.csv')
# Merge dataframes based on common key
merged_df = pd.merge(df_contact, df_entete, on='code_source_contact')
merged_df['date_entete'] = pd.to_datetime(merged_df['date_entete'])
merged_df=pd.merge(merged_df,df_adresse,on='id_ava_contact_initial')
merged_df['Code Département']=merged_df['code_postal_retraite'].str[:2]





   



## ajout des metrics 
if selected == "Home":
    cols = st.columns([2, 2, 2, 2, 2, 2])
    with cols[0]:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total CA</div>
            <div class="metric-value">€{Total_CA_actu}</div>
            <div class="metric-delta" style="color: {'green' if percentage_change_CA > 0 else 'red'};">{percentage_change_CA:.1f}% (année)</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Clients</div>
            <div class="metric-value">{tota_Actif_actu}</div>
            <div class="metric-delta" style="color: {'green' if percentage_change_actif > 0 else 'red'};">{percentage_change_actif:.1f}% (semestre)</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Panier moyen</div>
            <div class="metric-value">€{total_panier_actu}</div>
            <div class="metric-delta" style="color: {'green' if percentage_change_panier > 0 else 'red'};">{percentage_change_panier:.1f}% (semestre)</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Fréquence</div>
            <div class="metric-value">{freq_actu}</div>
            <div class="metric-delta" style="color: {'green' if percentage_change_freq > 0 else 'red'};">{percentage_change_freq:.1f}% (semestre)</div>
        </div>
        """, unsafe_allow_html=True)
    


# Sidebar filters
min_date = merged_df['date_entete'].min().date()
max_date = merged_df['date_entete'].max().date()

if selected == "Carte":
    
    start_date = st.sidebar.date_input("Date de début", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input("Date de fin", min_value=min_date, max_value=max_date, value=max_date)
    date_column_name = 'date_entete'
    filtered_df = merged_df[(merged_df['date_entete'].dt.date >= start_date) & (merged_df['date_entete'].dt.date <= end_date)]

    # Group by department and count number of clients
   
    clients_per_department = filtered_df.groupby("Code Département").size().reset_index(name="nombre_clients")
    total_clients=merged_df['id_ava_contact_initial'].nunique()
    clients_per_department['per_client_per_departement']=(clients_per_department['nombre_clients']/total_clients)*100

    df_departements = df_departements.merge(clients_per_department, left_on="code", right_on="Code Département", how="left")

    show_clients_map(df_departements)

elif selected == "analyse":
    
    st.sidebar.header("Analyse des données")
    show_data_analysis(df_entete)

elif selected == "Home":
    st.sidebar.header("Home")
    show_Home(df_entete)

elif selected=="Audience":
   st.sidebar.header("Audience")
   show_Audience(df_segmentation, df_contact, df_entete, df_adresse, df_ligne,df_email,df_telephone)

elif selected=="Data quality":
   st.sidebar.header("Dataquality")
   choix = st.sidebar.selectbox("Choisir le type de données", ["Email", "Genre","telephone mobile","telephone Fixe","date_naissance"])
   Dataquality(df_segmentation, df_contact, df_entete,df_adresse,df_ligne,df_email,df_telephone,df_media_invalide,choix)


elif selected== "Segmentation":
   st.sidebar.header("Segmentation")
   show_segmentation(df_segmentation, df_contact, df_entete,df_adresse,df_ligne,df_email,df_telephone,df_media_invalide)

   

   
    
   




