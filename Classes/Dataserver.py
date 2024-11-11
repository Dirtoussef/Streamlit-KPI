import pyodbc
import pandas as pd
import streamlit as st

@st.cache_data
def get_data_from_sql():
    server = 'avancisqldev01.domavanci.local'
    database = 'Stage_2024_Youssef'
    username = 'A_avancisqldev01'
    password = 'Y8tlSduh01L3CpsxzCvi'
    driver = 'ODBC Driver 18 for SQL Server'

    # Connexion à la base de données avec TrustServerCertificate
    conn = pyodbc.connect(
        f'DRIVER={{{driver}}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'TrustServerCertificate=yes'
    )

    # Récupérer les données de manière optimisée
    df_entete = pd.read_sql("SELECT * FROM [Stage_2024_Youssef].[dbo].[AVA_entete]", conn)
    df_contact = pd.read_sql("SELECT * FROM [Stage_2024_Youssef].[dbo].[AVA_contact]", conn)
    df_segmentation = pd.read_sql("""
        SELECT seg.*, cl.perimetre, cl.axe, cl.groupe, cl.libelle_segment, cl.regroupement_segment, 
               cl.segment_suivant, cl.is_actif, cl.is_inactif
        FROM AVA_histo_segmentation AS seg
        JOIN (
            SELECT DISTINCT segment, MIN(id_ava_classement) AS min_id
            FROM NFO_classement
            GROUP BY segment
        ) AS cl_min ON seg.segment = cl_min.segment
        JOIN NFO_classement AS cl ON cl.id_ava_classement = cl_min.min_id
        ORDER BY seg.id_ava_contact, seg.periode
    """, conn)
    df_adresse = pd.read_sql("SELECT * FROM [Stage_2024_Youssef].[dbo].[AVA_histo_adresse_postale]", conn)
    df_ligne = pd.read_sql("""
        SELECT code_source_entete, code_source_produit, montant_net_ttc, quantite_net
        FROM [Stage_2024_Youssef].[dbo].[AVA_ligne]
    """, conn)
    df_email = pd.read_sql("""
        SELECT id_ava_contact_initial, email_retraite, domaine, is_joignable, is_dernier
        FROM [Stage_2024_Youssef].[dbo].[AVA_histo_email]
    """, conn)
    df_telephone = pd.read_sql("""SELECT telephone_retraite,fixe_mobile,telephone_source,is_joignable,is_dernier,is_valide_traitement_externe 
                               FROM [Stage_2024_Youssef].[dbo].[AVA_histo_telephone]""", conn)
    
    df_media_invalide=pd.read_sql("""SELECT 
                   id_ava_histo_media_invalide,media_invalide_detail,detail
                                 

                   FROM[stage_2024_Youssef].dbo.[AVA_histo_media_invalide]
                   
                    """,conn)

    conn.close()




    return df_segmentation, df_contact, df_entete, df_adresse, df_ligne, df_email, df_telephone,df_media_invalide





