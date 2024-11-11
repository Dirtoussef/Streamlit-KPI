import streamlit as st
import plotly.express as px
import pandas as pd
import streamlit_shadcn_ui as ui
from Classes.Dataserver import get_data_from_sql
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import streamlit_shadcn_ui as ui
from datetime import datetime
import plotly.graph_objects as go



@st.cache_data

def fetch_data():
    return get_data_from_sql()

df_segmentation, df_contact, df_entete, df_adresse, df_ligne, df_email, df_telephone,df_media_invalide = fetch_data()

@st.cache_data
def calcul_graph_age(df_contact):
     
     # Calcul de la distribution des âges
     
     df_contact['date_naissance'] = pd.to_datetime(df_contact['date_naissance'])
     date_actuelle = datetime.now()
     diff_en_jours = (date_actuelle - df_contact['date_naissance']).dt.days
     df_contact['age'] = diff_en_jours // 365

    # Categorize ages into ranges
     bins = [18, 40, 60, 80]
     labels = ['18-40', '40-60', '60-80']
     df_contact['age_range'] = pd.cut(df_contact['age'], bins=bins, labels=labels, right=False)
     age_distribution = df_contact['age_range'].value_counts()

     return age_distribution

## graphique type of contact
def plot_type_contact(df_contact):
      type_contact=df_contact['type_contact']
      counts_type_contact=type_contact.value_counts().to_dict()
      values_type=list(counts_type_contact.values())
      label_type=list(counts_type_contact.keys())
      pull_values = [0.1 if label == 'COMPTE SANS ACHAT' else 0 for label in label_type]
      color_sequence = ['#FF9999', '#66B2FF', '#99FF99'] 
# Conversion du graphique en plotly.graph_objects pour ajouter l'explosion
      fig_donut_contact = go.Figure(data=[go.Pie(
    labels=label_type,
    values=values_type,
    hole=.3,
    pull=pull_values ,
    marker=dict(colors=color_sequence)
)])

# Mise à jour de la mise en page
      fig_donut_contact.update_layout(width=500, height=500,  title_text='Type de client',title_font_color='black')

      return  fig_donut_contact

# donut des catégoris de la seg 
def plot_seg_donut(df_segmentation):
      segmentation_counts=df_segmentation['libelle_segment'].value_counts()
      labels=list(segmentation_counts.keys())
      values=list(segmentation_counts.to_list())
      custom_colors = ['yellow', 'skyblue', 'blue', '#d62728','orange']
      fig_donut_seg = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>',
            marker=dict(colors=custom_colors)
        )])
      fig_donut_seg.update_layout(
            title=dict(text='Segmentation', x=0.5, xanchor='center'),
            title_font_color='black',
            title_font_size=24,
            title_x=0.5,
            title_y=0.95,
            title_font_family='Arial',
            legend_title='Catégories',
            legend_font_size=14,
            legend_traceorder='reversed',
            width=500,
            height=500
        )
      return fig_donut_seg

@st.cache_data
def calcul_graph_pyramide(df_contact):

    df_contact = df_contact.dropna(subset=['age', 'genre'])

    # Définir les tranches d'âge
    age_bins = np.arange(10, 90, 10)

# Regrouper les données par genre et tranche d'âge
    df_male = df_contact[df_contact['genre'] == 'M']
    df_female = df_contact[df_contact['genre'] == 'F']

    male_counts, _ = np.histogram(df_male['age'], bins=age_bins)
    female_counts, _ = np.histogram(df_female['age'], bins=age_bins)

    total_male=len(df_male)
    total_female=len(df_female)

    male_pourcentage=((male_counts/total_male) * 100).round().astype(int)
    female_pourcentage=((female_counts/total_female) * 100).round().astype(int)

# Préparation des données pour le graphique
    y_age = [f"{left}-{right-1}" for left, right in zip(age_bins[:-1], age_bins[1:])]
    x_M = male_pourcentage
    x_F = - female_pourcentage
    x_F_abs = female_pourcentage  

    return y_age,x_F,x_M,x_F_abs

def plot_pyramide(df_contact):
    # Création de la figure
    y_age,x_F,x_M,x_F_abs=calcul_graph_pyramide(df_contact)
    fig_pyramide = go.Figure()

# Ajout des barres pour les hommes
    fig_pyramide.add_trace(go.Bar(
    y=y_age,
    x=x_M,
    name='Hommes',
    orientation='h',  # Orientation horizontale
    marker=dict(color='blue'),
    hovertemplate='%{x}%<extra></extra>' # Couleur pour les hommes
))

# Ajout des barres pour les femmes
    fig_pyramide.add_trace(go.Bar(
    y=y_age,
    x=x_F,
    name='Femmes',
    orientation='h',  # Orientation horizontale
    marker=dict(color='pink'),
    customdata=x_F_abs,
    hovertemplate='%{customdata}%<extra></extra>'  # Couleur pour les femmes
))

# Mise à jour du layout du graphique
    fig_pyramide.update_layout(
    title={'text': 'Pyramide des ages  ', 'font': {'color': 'black'}, 'x': 0.4},
    xaxis_title='Pourcentage',
    yaxis_title='Tranche d\'âge',
    barmode='relative',  # Mode relatif pour superposer les barres
    bargap=0.2,  # Pas d'espace entre les barres d'un même groupe
    bargroupgap=0,  # Pas d'espace entre les groupes de barres
    xaxis=dict(
        tickvals=[-20,-10, -5, 0, 5, 10,20],  # Ajustez selon vos données
        ticktext=['20%','10%', '5%', '0', '5%', '10%', '20%'],
        title='Pourcentage',
        title_font_size=14
    ) 
)
    return fig_pyramide
      

age_distribution = calcul_graph_age(df_contact)


## graphique type de vente 
def plot_canal_vente(df_entete):
    counts = df_entete['canal_vente'].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()

    custom_colors = ['#8A2BE2', 'skyblue', 'yellow']  # Couleurs personnalisées

    fig_pie_canalvente = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hole=0.2,
    hovertemplate='<b>%{label}</b><br>%{value}</b><br>',  # Template pour info au survol
    marker=dict(colors=custom_colors)
)])

# Mise en forme du layout du graphique pie
    fig_pie_canalvente.update_layout(
    title=dict(text='Répartition des canaux de vente', x=0.5, xanchor='center'),
    title_font_color='black',
    title_font_size=20,
    title_x=0.5,
    title_y=0.95,
    title_font_family='Arial',
    legend_title='Canaux de vente',
    legend_font_size=14,
    width=  500,  # Ajustement de la largeur
    height=500  # Ajustement de la hauteur
)
    return fig_pie_canalvente
def plot_type_tephone(df_entete):
    counts_telephone=df_telephone['fixe_mobile'].value_counts().to_dict()

    labels=list(counts_telephone.keys())
    values=list(counts_telephone.values())

    fig_donut_telephone = px.pie(df_telephone,df_telephone['fixe_mobile'], 
                              title='Type de Telephone',labels={'label': 'Telephone', 'value': 'Count'},color_discrete_sequence=['blue', 'Orange'])
    fig_donut_telephone.update_layout(width=500,height=500,title_font_color='black')
    
    return fig_donut_telephone

##raphique  de la distribution age 
def plot_age_distribution():
    colors = px.colors.qualitative.Pastel
    fig_age_distribution = px.pie(age_distribution, values=age_distribution.values, names=age_distribution.index,
                              title='Age', color_discrete_sequence=colors,
                              
                              labels={'label': 'Age', 'value': 'Count'})
    
    fig_age_distribution.update_layout(title_font_color='black',title_x=0.4,width=600,height=600)

    return fig_age_distribution
# graphique distribution genre 
def plot_genre_distribution(df_contact):
    genre_counts = df_contact['genre'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']
    fig_genre= px.pie(genre_counts,values='count',names='genre',title='sexe',color_discrete_sequence=['blue', '#FF69B4'],
    labels={'genre': 'Sexe', 'count': 'count'}) 

    fig_genre.update_traces(textposition='inside', textinfo='percent+label',hovertemplate='<b> sexe: %{label}</b><br><b>Count: %{value}<extra></extra>')
    fig_genre.update_layout(width=500,height=500,showlegend=False,   
                                     title_x=0.5, title_y=0.95,
                                     plot_bgcolor='white', paper_bgcolor='white',
                                     title_font_color='black')
    
    return fig_genre
    


def show_Audience(df_segmentation,df_contact,df_entete,df_adresse,df_ligne,df_email,df_telephone):
    y_age,x_F,x_M,x_F_abs=calcul_graph_pyramide(df_contact)




    
    
    
    
    
    
    col1,col2=st.columns([10,4])
    
    with col1:
        fig_pyramide=plot_pyramide(df_contact)
        st.plotly_chart(fig_pyramide)
    
    with col2:
        fig_pie_canalvente=plot_canal_vente(df_entete)
        st.plotly_chart(fig_pie_canalvente)
    

    
   
    
    
    
    
    


    

    
    

    col3,col4,col5=st.columns([5,5,5])
    
    
    
    with col3:
        fig_donut_telephone=plot_type_tephone(df_entete)
        st.plotly_chart(fig_donut_telephone)

    with col4:
        fig_age_distribution=plot_age_distribution()
        st.plotly_chart(fig_age_distribution)

    with col5:
        fig_genre=plot_genre_distribution(df_contact)
        st.plotly_chart(fig_genre)

    col11,col12=st.columns([10,10])
    with col11:
        fig_donut_contact=plot_type_contact(df_contact)
        st.plotly_chart(fig_donut_contact)

    with col12:
        fig_donut_seg=plot_seg_donut(df_segmentation)
        st.plotly_chart(fig_donut_seg)










    








    




    


