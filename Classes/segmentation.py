import streamlit as st
import plotly.express as px
import pandas as pd
from Classes.Dataserver import get_data_from_sql
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import math



@st.cache_data

def fetch_data():
    return get_data_from_sql()
## calcul de la seg
@st.cache_data
def calcul_graph_fuite(df_segmentation):
     
     
    #calcul de la fuite 
     df_segmentation['periode_precedente'] = df_segmentation.groupby('id_ava_contact')['periode'].shift(1)
     df_segmentation['regroupement_precedent'] = df_segmentation.groupby('id_ava_contact')['regroupement_segment'].shift(1)
     df_segmentation['fuite'] = (df_segmentation['regroupement_precedent'] == 'ACTIF') & (df_segmentation['regroupement_segment'] == 'INACTIF')

     fuite = df_segmentation[df_segmentation['fuite']].groupby('periode')['fuite'].sum().reset_index()
     #calcul du total de l'actif  par semestre et par année 
     Actifs = df_segmentation.groupby('periode')['id_ava_contact'].nunique().reset_index(name='total_actifs')
     Actifs['annee'] = Actifs['periode'].str[:4]
     Actifs['semestre'] = Actifs['periode'].str[-2:]
    ## Calcul de la  Réactivation par semestre et par année 
     df_segmentation['Réactivation'] = (df_segmentation['regroupement_precedent'] == 'INACTIF') & (df_segmentation['regroupement_segment'] == 'ACTIF')
     rec = df_segmentation[df_segmentation['Réactivation']].groupby('periode')['Réactivation'].sum().reset_index()
     fuite['annee'] = fuite['periode'].str[:4]
     fuite['semestre'] = fuite['periode'].str[-2:]
     rec['annee'] = rec['periode'].str[:4]
     rec['semestre'] = rec['periode'].str[-2:]
    # calculd ela conquéte 
     nouveau = df_segmentation[df_segmentation['segment'] == 'N'].groupby('periode')['segment'].count().reset_index()
     nouveau = nouveau.rename(columns={'segment': 'conquête'})
     nouveau['semestre'] = nouveau['periode'].str[-2:]
     nouveau['annee'] = nouveau['periode'].str[:4]

     merged_df = fuite.merge(rec, on=['annee', 'semestre'], how='outer', suffixes=('_fuite', '_rec')).merge(nouveau, on=['annee', 'semestre'], how='outer', suffixes=('_nouveau', '_rec')).merge(Actifs, 
                                                                                on=['annee', 'semestre'], how='outer', suffixes=('_actifs', '_rec'))
     merged_df = merged_df.drop(columns=['periode_fuite', 'periode_rec', 'periode_actifs', 'periode_rec'])
     merged_df['fuite_per'] = (merged_df['fuite'] / merged_df['total_actifs']) * 100
     merged_df['conquête_per'] = (merged_df['conquête'] / merged_df['total_actifs']) * 100
     total_actif_sum = merged_df['total_actifs'].sum()
     merged_df['total_actifs_per'] = (merged_df['total_actifs'] / total_actif_sum) * 100
     merged_df.fillna(0, inplace=True)
    ## Balance client

     merged_df['Balance client']=merged_df['conquête']+merged_df['Réactivation'] - merged_df['fuite']
     merged_df['annee_semestre'] = merged_df['annee'].astype(str) + ' ' + merged_df['semestre']
    # fonction pour arrondir 
     def round_custom(x):
            if pd.isna(x):
                return np.nan
            str_x = f"{x:.2f}"
            if '.' in str_x:
                whole_part, decimal_part = str_x.split('.')
                if len(decimal_part) > 1 and int(decimal_part[1]) > 5:
                    return f"{int(np.ceil(x))}"
                return f"{int(np.round(x))}"
            return str_x

    ##   merger fuite conquete total_actifs ,balance 
     merged_df['fuite_per'] = merged_df['fuite_per'].apply(round_custom)
     merged_df['conquête_per'] = merged_df['conquête_per'].apply(round_custom)
     merged_df['total_actifs_per'] = merged_df['total_actifs_per'].apply(round_custom)

     merged_df['annee_semestre'] = merged_df['annee'].astype(str) + ' ' + merged_df['semestre']
     merged_df['fuite_per'] = merged_df['fuite_per'].fillna(0)
     merged_df['conquête_per'] = merged_df['conquête_per'].fillna(0)


     return  fuite,Actifs,rec,nouveau,merged_df
@st.cache_data
## graphique de la fuite conquete et total Actif 
def plot_fuite_conquete_actif(filtered_merged):
     
     fig_bar = go.Figure()
     fig_bar.add_trace(go.Bar(
                    x=filtered_merged['annee_semestre'],
                    y=filtered_merged['total_actifs'],
                    name='Total Actifs',
                    showlegend=True,
                    marker_color='#BEF574',
                    width=0.2,
                    hovertemplate='<b>Date:%{x}</b><br><b>Total Actifs: %{y}<extra></extra>'
                    
               
                ))

     fig_bar.add_trace(go.Bar(
                    x=filtered_merged['annee_semestre'],
                    y=-filtered_merged['fuite'],
                    name='Fuite',
                    marker_color='red',
                    width=0.2,
                    offset=-0.3,
                    hovertemplate='<b>Date:%{x}</b><br><b>fuite: %{y}<extra></extra>'
                ))

     fig_bar.add_trace(go.Bar(
                    x=filtered_merged['annee_semestre'],
                    y=filtered_merged['conquête'],
                    name='Conquête',
                    marker_color='blue',
                    width=0.2,
                    offset=0.1,
                    hovertemplate='<b>Date:%{x}</b><br><b>conquête: %{y}<extra></extra>'
                ))

     
     fig_bar.update_layout(width=800, height=400,
            title={'text': 'Actifs, Fuite, et Conquête par Semestre', 'font': {'color': 'black'}, 'x': 0.4},
            xaxis_title='Année Semestre',
            yaxis_title='Effectifs',
            barmode='overlay',
            xaxis=dict(color='black', categoryorder='array'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(color='white', showgrid=True, zeroline=True),
            legend=dict(font=dict(color='black'), traceorder='normal', bgcolor='rgba(0,0,0,0)'),
           
        )

     fig_bar.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')
     fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')

     return fig_bar

@st.cache_data
## graphique balance , réactivation , conquete 
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
     



def show_segmentation(df_segmentation, df_contact, df_entete,df_adresse,df_ligne,df_email,df_telephone,df_media_invalide):
      
      
      


      fuite, Actifs, rec, nouveau, merged_df = calcul_graph_fuite(df_segmentation)

      col8=st.columns([18])
      annee=merged_df['annee'].unique()
      selected_years=st.sidebar.multiselect(" Fuite et balance ", options=list(annee), default=list(annee)[:6], key="annee_multiselect7")
      
      filtered_merged=merged_df[merged_df['annee'].isin(selected_years)]
     
       
      fig_bar=plot_fuite_conquete_actif(filtered_merged)
    
    



      st.plotly_chart(fig_bar,use_container_width=True)
      
      col9=st.columns([16])
      filtered_merged=merged_df[merged_df['annee'].isin(selected_years)]

      fig_reactivation=plot_balance(filtered_merged)
      st.plotly_chart(fig_reactivation,use_container_width=True)

      
      
      







df_segmentation, df_contact, df_entete, df_adresse, df_ligne, df_email,df_telephone,df_media_invalide=fetch_data()
show_segmentation(df_segmentation, df_contact, df_entete, df_adresse, df_ligne, df_email, df_telephone, df_media_invalide)








