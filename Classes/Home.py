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
import math

# Extract Data
@st.cache_data

def fetch_data():
    return get_data_from_sql()

df_segmentation, df_contact, df_entete, df_adresse, df_ligne, df_email,df_telephone,df_media_invalide= fetch_data()

@st.cache_data
def etiquettes(df_entete):
     ### calcul du CA et pourcentage changememnt du CA   
     recent_annee = df_entete['date_entete'].dt.year.max() 
     df_recent_annee=df_entete[df_entete['date_entete'].dt.year==recent_annee]  
     Total_CA_actu = math.floor(df_recent_annee['montant_net_ttc'].sum())
     prec_annee= recent_annee - 1 
     df_prec_annee=df_entete[df_entete['date_entete'].dt.year==prec_annee]
     Total_CA_prec = round(df_prec_annee['montant_net_ttc'].sum(), 2)
     percentage_change_CA =((Total_CA_actu - Total_CA_prec) / Total_CA_prec) * 100
     
     ## calcul du total de l'actif  et pourcentage du changement de l'actif 
     Actifs = df_segmentation.groupby('periode')['id_ava_contact'].nunique().reset_index(name='total_actifs')
     Actifs['annee'] = Actifs['periode'].str[:4]
     Actifs['semestre'] = Actifs['periode'].str[-2:]
     Actifs=Actifs.rename(columns={'periode':'date_entete'})
     Actifs_sorted = Actifs.sort_values(by='date_entete', ascending=False)

     date_recente=Actifs_sorted.iloc[1]['date_entete']
     date_prec=Actifs_sorted.iloc[2]['date_entete']
     tota_Actif_actu= Actifs[Actifs['date_entete'] == date_recente]['total_actifs'].values[0]
     tota_Actif_prec= Actifs[Actifs['date_entete'] == date_prec]['total_actifs'].values[0]
     percentage_change_actif=((tota_Actif_actu -tota_Actif_prec) /tota_Actif_prec) * 100
     percentage_change_actif

    #calcul du CA

    ## panier moyen et pourcentage change par rapport au smestre precedent 
    # calcul du chiffre d'affaire par semestre 
     df_q1=df_entete[df_entete['date_entete'].dt.month<=6]
     df_q2=df_entete[df_entete['date_entete'].dt.month>=6]

     df_q1['annee'] = df_q1['date_entete'].dt.year
     df_q1['date_entete'] = df_q1['annee'].astype(str) + 'S1'
     df_q2['annee'] = df_q2['date_entete'].dt.year
     df_q2['date_entete'] = df_q2['annee'].astype(str) + 'S2'

     df_q1_semestre1=df_q1.groupby('date_entete')['montant_net_ttc'].sum().reset_index()
     df_q2_semestre2=df_q2.groupby('date_entete')['montant_net_ttc'].sum().reset_index()
     df_q1_CA_semestre1 = df_q1_semestre1.rename(columns={'montant_net_ttc': 'CA'})
     df_q2_CA_semestre2 = df_q2_semestre2.rename(columns={'montant_net_ttc': 'CA'})
     CA_per_semestre = pd.concat([df_q1_CA_semestre1, df_q2_CA_semestre2], axis=0)
    ## calcul  Actifs par semestre 
     Actifs = df_segmentation.groupby('periode')['id_ava_contact'].nunique().reset_index(name='total_actifs')
     Actifs['annee'] = Actifs['periode'].str[:4]
     Actifs['semestre'] = Actifs['periode'].str[-2:]
     Actifs=Actifs.rename(columns={'periode':'date_entete'})
     Actifs = Actifs.drop(columns=[ 'semestre'])
    ## clacul du total de comande par semestre et par année 
     commandes_s1=df_q1.groupby('date_entete')['is_affecte_client_valide'].sum().reset_index()
     commandes_s1=commandes_s1.rename(columns={'is_affecte_client_valide': 'Total_commandes'})
     commandes_s2=df_q2.groupby('date_entete')['is_affecte_client_valide'].sum().reset_index()
     commandes_s2=commandes_s2.rename(columns={'is_affecte_client_valide': 'Total_commandes'})
     Total_commandes = pd.concat([commandes_s1, commandes_s2], axis=0)
     ## merger le total des commandes et le CA par semestre sur panier 
     panier = pd.merge(CA_per_semestre, Total_commandes)
     panier = pd.merge(panier, Actifs, on='date_entete', how='outer')
     ## calcul du panier moyen en divisant le CA par le total des commandes 
     panier['CA'] = panier['CA'].astype(float)
     panier['paniermoyen']=panier['CA']/panier['Total_commandes']
     panier['annee']=panier['date_entete'].str[:4]
     annee=panier['annee'].unique()
     panier_sorted=panier.sort_values(by='date_entete', ascending=False)
     ## total du pnaier moye sur le semestre actuelle 
     total_panier_actu=math.floor(panier_sorted[panier_sorted['date_entete'] == date_recente]['paniermoyen'].values[0])
     ## total du pnaier moyen sur le semestre precedant 
     total_panier_prec=panier_sorted[panier_sorted['date_entete'] == date_prec]['paniermoyen'].values[0]
     ## pourcentage change du panier moyen par rapport au semestre precedant 
     percentage_change_panier=((total_panier_actu- total_panier_prec) / total_panier_prec) * 100

     ## calcul de la  Fréquence par seemstre et par année 
     
     panier['Fréquence']=round(panier['Total_commandes']/panier['total_actifs'],2)
     freq_sorted=panier.sort_values(by='date_entete', ascending=False)
     ## fréquence du semestre actuelle 
     freq_actu=round(freq_sorted[freq_sorted['date_entete'] == date_recente]['Fréquence'].values[0],2)
     #fréquence du semestre précedant 
     freq_prec=round(freq_sorted[freq_sorted['date_entete'] == date_prec]['Fréquence'].values[0],2)
    #pourcentage changement du fréquence par rapport au semestre precedant 
     percentage_change_freq = ((freq_actu - freq_prec) / freq_prec) * 100
    
     return (Total_CA_actu, Total_CA_prec,percentage_change_CA,Actifs_sorted,tota_Actif_actu,percentage_change_actif,CA_per_semestre,Actifs,Total_commandes,
             panier, panier_sorted,total_panier_actu,total_panier_prec,percentage_change_panier,freq_sorted, freq_actu,percentage_change_freq,annee)


    
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






     
     
     

     





@st.cache_data
def calcul_graph__CA_per_semestre(df_entete):
     

    df_entete['date_entete'] = pd.to_datetime(df_entete['date_entete'])


    df_q1=df_entete[df_entete['date_entete'].dt.month<= 6]



    df_q1.loc[:, 'annee'] = df_q1['date_entete'].dt.year.astype(str) + 'S1'

    df_q2=df_entete[df_entete['date_entete'].dt.month>= 6]
    df_q2.loc[:, 'annee'] = df_q2['date_entete'].dt.year.astype(str) +'S2'





    df_q1['montant_net_ttc'] = df_q1['montant_net_ttc'].astype(float)
    df_q2['montant_net_ttc'] = df_q2['montant_net_ttc'].astype(float)





    CA_annee_Q1 = df_q1.groupby('annee')['montant_net_ttc'].sum().reset_index()
    CA_annee_Q2 = df_q2.groupby('annee')['montant_net_ttc'].sum().reset_index()
    CA_annee_Q1['annee_base']=CA_annee_Q1['annee'].str[:4]
    CA_annee_Q2['annee_base']=CA_annee_Q2['annee'].str[:4]


    CA_annee_concat = pd.concat([CA_annee_Q1, CA_annee_Q2])

#df_clients_sorted = df_entete.groupby('id_ava_contact')['montant_net_ttc'].sum().reset_index().sort_values(by='montant_net_ttc', ascending=False)
#total_CA = df_clients_sorted['montant_net_ttc'].sum()
     
#CA_annee['annee']=CA_annee['annee'].str[:4]
    CA_per_annee=CA_annee_concat.sort_values(by=['annee'])

    CA_per_annee['semestre']=CA_per_annee['annee'].str[-2:]
    annee=CA_annee_concat['annee_base'].unique()
    
    return   CA_per_annee,annee



     
(Total_CA_actu,Total_CA_prec,percentage_change_CA,Actifs_sorted,tota_Actif_actu,percentage_change_actif,CA_per_semestre,Actifs,Total_commandes,
 panier, panier_sorted,total_panier_actu,total_panier_prec,percentage_change_panier,freq_sorted, freq_actu,percentage_change_freq,annee) = etiquettes(df_entete)

age_distribution = calcul_graph_age(df_contact)





CA_per_annee,annee= calcul_graph__CA_per_semestre(df_entete)






















@st.cache_data
def update_progress_bar(percentage):
            top_percentage_count = int(percentage * len(df_clients_sorted) / 100)
            top_percentage_clients = df_clients_sorted.head(top_percentage_count)
            top_percentage_CA = top_percentage_clients['montant_net_ttc'].sum()
            top_percentage_CA_proportion = top_percentage_CA / total_CA * 100 

#Graphique pourcentage des client sen CA 

df_clients_sorted = df_entete.groupby('id_ava_contact')['montant_net_ttc'].sum().reset_index().sort_values(by='montant_net_ttc', ascending=False)
total_CA = df_clients_sorted['montant_net_ttc'].sum()

def update_progress_bar(percentage):
    top_percentage_count = int(percentage * len(df_clients_sorted) / 100)
    top_percentage_clients = df_clients_sorted.head(top_percentage_count)
    top_percentage_CA = top_percentage_clients['montant_net_ttc'].sum()
    top_percentage_CA_proportion = top_percentage_CA / total_CA * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=top_percentage_CA_proportion,
        
            number={'suffix': "% CA", 'font': {'color': 'black'}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 100], 'color': "gray"}
            ],
        }
    ))
    fig.update_layout(
    title={
        'text': f"<b style='color:black;'>{percentage}% des Clients</b>",
        'y': 0.95,  # Valeur comprise entre 0 et 1, où 1 fait référence au bord supérieur de la zone de traçage
        'x': 0.5,  # Centrer le titre en définissant x à 0.5
        'xanchor': 'center', 
        'yanchor': 'top'  
    }
)
    return(fig)


# Fonction pour afficher le graphique de fréquence et total de commandes

def plot_frequence(filtred_panier):
    fig_freq = go.Figure()

    fig_freq.add_trace(go.Bar(
          x=filtred_panier['date_entete'],
          y=filtred_panier['Fréquence'],
    
        marker=dict(color='orange',opacity=0.5),
        name='Fréquence',
        yaxis='y1',
        width=0.2,
        hovertemplate='<b>Date:%{x}</b><br><b>Fréquence: %{y}<extra></extra>'))

        # Add scatter trace
    fig_freq.add_trace(go.Scatter(
        x=filtred_panier['date_entete'],
        y=filtred_panier['Total_commandes'],
        mode='lines',
        line=dict(color='green', width=2),
        name='Total_commandes',
        yaxis='y2',
        hovertemplate='<b>Date:%{x}</b><br><b>Total_commandes: %{y}<extra></extra>'
))
    

    fig_freq.add_trace(go.Scatter(
    x=filtred_panier['date_entete'],
    y=filtred_panier['Total_commandes'],
    mode='markers',  # Mode pour afficher des points
    marker=dict(color='green', size=8),  # Couleur et taille des points
    name='Panier',
    yaxis='y2',
    showlegend=False,
     
 hovertemplate='<b>Date:%{x}</b><br><b>Total_commandes: %{y}<extra></extra>'   ))

        
    fig_freq.update_layout(width=500, height=400,
    title=dict(text='Évolution de la Fréquence et Total commandes ', x=0.5, xanchor='center'),
    xaxis_title='Semestre',
    title_font_color='black',
    plot_bgcolor='white',
    paper_bgcolor='white',
    
    
    
    yaxis2=dict(
        title='Orders',
        overlaying='y',
        side='right',
        title_font=dict(size=14, color='#800080'),
        ),
        yaxis=dict(
        title='Valeurs',
        
        side='left',
        title_font=dict(size=14, color='blue'),
        
        
    ),
    legend=dict(
        orientation='h', 
        yanchor='top',  
        y=1.1,  
        xanchor='center', 
        x=0.5  ,
        font=dict(color='black') 
    )
)
    
    
    return fig_freq


def plot_panier_CA(filtred_panier):
    
    
    fig_panier_freq=go.Figure()
     
     # Add bar trace with base
    fig_panier_freq.add_trace(go.Bar(
          x=filtred_panier['date_entete'],
          y=filtred_panier['CA'],
    
        marker=dict(color='#800080',opacity=0.5),
        name='Chiffre d\'affaires',
        yaxis='y2',
        width=0.2,
        hovertemplate='<b>Date:%{x}</b><br><b>CA: %{y}<extra></extra>'))

# Add scatter trace
    fig_panier_freq.add_trace(go.Scatter(
        x=filtred_panier['date_entete'],
        y=filtred_panier['paniermoyen'],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Panier moyen',
        yaxis='y1',
        hovertemplate='<b>Date:%{x}</b><br><b>panier moyen: %{y}<extra></extra>'
))
    

    
   






    fig_panier_freq.add_trace(go.Scatter(
     x=filtred_panier['date_entete'],
     y=filtred_panier['paniermoyen'],
     mode='markers',  # Mode pour afficher des points
     marker=dict(color='blue', size=8),  # Couleur et taille des points
     name='Panier',
     yaxis='y1',
     showlegend=False,
      hovertemplate='<b>Date:%{x}</b><br><b>panier moyen: %{y}<extra></extra>'
    ))

# Add titles and labels
    fig_panier_freq.update_layout(width=500, height=400,
    title=dict(text='Évolution du panier moyen et CA ', x=0.5, xanchor='center'),
    xaxis_title='Semestre',
    title_font_color='black',
    
    plot_bgcolor='white',
    paper_bgcolor='white',
    
    
    
    yaxis2=dict(
        title='CA',
        overlaying='y',
        side='right',
        title_font=dict(size=14, color='#800080'),
        ),
        yaxis=dict(
        title='Valeurs',
        
        side='left',
        title_font=dict(size=14, color='blue'),
        
        
    ),
    legend=dict(
        orientation='h', 
        yanchor='top',  
        y=1.1,  
        xanchor='center', 
        x=0.5  ,
        font=dict(color='black') 
    )
)
    return fig_panier_freq






    


           
       
     
def plot_CA_per_semestre(CA_annee_filtred):     
         
         fig_bar = px.bar(CA_annee_filtred,y='annee_base', x='montant_net_ttc',color='semestre',barmode='group',
         labels={'value': 'CA'},
         color_discrete_map={'S1': 'yellow', 'S2' : "skyblue"},
        orientation='h')
         fig_bar.update_traces(
    hovertemplate='<b>CA: %{x}</b><br><b> Année: %{y}</b><extra></extra>'
)
         fig_bar.update_layout(width=600, height=400,
    title_text='CA par semestre',
                      title_font_color='black',
                      title_x=0.3,
    xaxis_title='CA',
    yaxis_title='Année',
      
    xaxis=dict(color='black'
    ), plot_bgcolor='white',
    paper_bgcolor='white',
    yaxis=dict(color='black',
        showgrid=True,
        zeroline=True
    ),
    legend=dict(font=dict(color='black')))
         fig_bar.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')
         fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)') 

         return fig_bar 









      
     
def plot_balance(merged_df):
          fig_reactivation= go.Figure()
          fig_reactivation.add_trace(go.Scatter(
        x=merged_df['annee_semestre'],
        y=merged_df['Balance client'],
        mode='lines',
        line=dict(color='#800080', width=3, dash='solid',  shape='spline'),
        
        name='Balance client',
        yaxis='y1'
))
          fig_reactivation.add_trace(go.Scatter(
        x=merged_df['annee_semestre'],
        y=merged_df['Réactivation'],
        mode='lines',
        line=dict(color='skyblue', width=3),
        name='Réactivation',
        yaxis='y1'
))
          fig_reactivation.add_trace(go.Scatter(
        x=merged_df['annee_semestre'],
        y=merged_df['conquête'],
        mode='lines',
        line=dict(color='orange', width=3),
        name='conquête',
        yaxis='y1'
))
          fig_reactivation.add_trace(go.Scatter(
    x=merged_df['annee_semestre'],
    y=merged_df['Balance client'],
    mode='markers',  # Mode pour afficher des points
    marker=dict(color='#800080', size=4),  # Couleur et taille des points
    name='Balance',
    yaxis='y1',
    showlegend=False
    ))
          fig_reactivation.add_trace(go.Scatter(
    x=merged_df['annee_semestre'],
    y=merged_df['conquête'],
    mode='markers',  # Mode pour afficher des points
    marker=dict(color='orange', size=5),  # Couleur et taille des points
    name='Balance',
    yaxis='y1',
    showlegend=False
    ))
          fig_reactivation.add_trace(go.Scatter(
    x=merged_df['annee_semestre'],
    y=merged_df['Réactivation'],
    mode='markers',  # Mode pour afficher des points
    marker=dict(color='skyblue', size=5),  # Couleur et taille des points
    name='Réactivation',
    yaxis='y1',
    showlegend=False
    ))
          fig_reactivation.add_trace(go.Scatter(
    x=merged_df['annee_semestre'],
    y=merged_df['Balance client'],
    mode='markers',
    marker=dict(color='#800080', size=5),
    name='Balance client',
    yaxis='y1',
    hovertemplate='Date: %{x}<br>Balance client: %{y}',
    showlegend=False
))
          fig_reactivation.add_trace(go.Scatter(
    x=merged_df['annee_semestre'],
    y=merged_df['Réactivation'],
    mode='markers',
    marker=dict(color='skyblue', size=5),
    name='Balance client',
    yaxis='y1',
    hovertemplate='Date: %{x}<br>Réactivation: %{y}',
    showlegend=False
))
          fig_reactivation.add_trace(go.Scatter(
    x=merged_df['annee_semestre'],
    y=merged_df['conquête'],
    mode='markers',
    marker=dict(color='orange', size=5),
    name='Balance client',
    yaxis='y1',
    hovertemplate='Date: %{x}<br>conquête: %{y}',
    showlegend=False
))
          fig_reactivation.update_layout(width=800, height=400,
    title={'text':'Balance,Réactivation,conquête' , 'font' : {'color':'black'}, 'x': 0.4},
    xaxis_title='Semestre',
    
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=False,
               gridcolor='lightgrey',linecolor='rgba(0,0,0,0.2)'),
    yaxis=dict(showgrid=False,
               gridcolor='lightgrey',linecolor='rgba(0,0,0,0.2)'),


    legend=dict(
        orientation='h', 
        yanchor='top',  
        y=1.1,  
        xanchor='center', 
        x=0.5  ,
        font=dict(color='black') 
    )
)
          return fig_reactivation
     
     






# Définir la fonction show_Home
def show_Home(df_segmentation):
    df_segmentation, df_contact, df_entete, df_adresse,df_ligne,df_email,df_telephone,df_media_invalide= get_data_from_sql()
    (Total_CA_actu,Total_CA_prec,percentage_change_CA,Actifs_sorted,tota_Actif_actu,percentage_change_actif,CA_per_semestre,Actifs,Total_commandes,
 panier, panier_sorted,total_panier_actu,total_panier_prec,percentage_change_panier,freq_sorted, freq_actu,percentage_change_freq,annee) = etiquettes(df_entete)

    
    

    CA_per_annee,annee = calcul_graph__CA_per_semestre(df_entete)
    
      
    
    

    
    
    


    ##filtre annee pour l'onglet home
    selected_years=st.sidebar.multiselect("choisir l'année", options=list(annee), default=list(annee)[:3], key="annee_multiselect")

    filtred_panier=panier[panier['annee'].isin(selected_years)]
   
    col0,col2 = st.columns([15,14])
    
    with col0:
        
        fig_freq = plot_frequence(filtred_panier)
        st.plotly_chart(fig_freq, use_container_width=True)

    with col2:

        fig_panier_freq=plot_panier_CA(filtred_panier)

        st.plotly_chart(fig_panier_freq, use_container_width=True)




    col4, col5= st.columns([2, 2])



    

    

    
    CA_annee_filtred=CA_per_annee[CA_per_annee['annee_base'].isin(selected_years)]
    
    with col4:
         
         fig_bar=plot_CA_per_semestre(CA_annee_filtred)
         st.plotly_chart(fig_bar, use_container_width=True, config={"modeBarButtonsToRemove": ['pan2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'hoverClosestCartesian', 
        'hoverCompareCartesian'],'displaylogo': False})
    
    
    
    with col5:
        
            
           percentage_slider = st.sidebar.slider("Pourcentage clients:", min_value=0, max_value=100, step=10, value=20)
           fig = update_progress_bar(percentage_slider)
           fig.update_layout(
    
    margin={'t': 20, 'b': 20, 'l': 20, 'r': 20}
)
           st.plotly_chart(fig, use_container_width=True, width=200, height=200)


    





   
    
    



    







         
   


         
           









# Fermer le conteneur rectangulaireTotal_CA_actu
st.markdown('</div>', unsafe_allow_html=True)

##.\venv\Scripts\Activate
