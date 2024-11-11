import streamlit as st
import plotly.graph_objects as go
from Classes.Dataserver import get_data_from_sql

def inject_css_for_dataquality():
    st.markdown(
        """
        <style>
        /* Target only elements in the Dataquality section */
        .Data quality-container .stSelectbox, 
        .Data quality-container .stMultiSelect {
            color: black !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


@st.cache_data
def fetch_data():
    return get_data_from_sql()


@st.cache_data
def calcul_email(df_email):

    total_clients = len(df_email)
    null_clients = len(df_email[df_email['email_retraite'].isnull()])
    not_null_clients = total_clients - null_clients
    joignable_emails = df_email[df_email['is_joignable'] == 1]['email_retraite']
    count_joignable_emails = joignable_emails.notnull().sum()
    valide_email = df_contact[df_contact['is_valide_email'] == 1]['is_valide_email']
    optin_email = df_contact[df_contact['is_optin_email'] == 1]['is_optin_email']
    optin_email_counts = optin_email.notnull().sum()
    counts_valide = valide_email.notnull().sum()
    

    return total_clients,counts_valide,not_null_clients,count_joignable_emails
@st.cache_data
def calcul_telephone_mobile(df_telephone):

    Telephone_Mobile=df_telephone[df_telephone['fixe_mobile'] == 'MOBILE']
    total_clients_mobile=total_clients_FIXE=len(df_contact['id_ava_contact'])
    null_clients_Mobile= len(df_telephone[df_telephone['telephone_retraite'].isnull()])
    not_clients_mobile= total_clients_mobile - null_clients_Mobile
    count_joignable_mobile= df_telephone['is_joignable'].notnull().sum()
    count_valide_mobile=df_telephone['is_valide_traitement_externe'].notnull().sum()

    return total_clients_mobile,null_clients_Mobile,not_clients_mobile,count_joignable_mobile,count_valide_mobile


def calcul_telehone_Fixe(df_telephone):
    Telephone_FIXE=df_telephone[df_telephone['fixe_mobile'] == 'FIXE']
    total_clients_FIXE=len(df_contact['id_ava_contact'])
    count_valide_FIXE=df_telephone['is_valide_traitement_externe'].notnull().sum()
    null_clients_FIXE= len(df_telephone[df_telephone['telephone_retraite'].isnull()])
    not__null_clients_FIXE= total_clients_FIXE - null_clients_FIXE
    count_joignable_FIXE= df_telephone['is_joignable'].notnull().sum()

    return total_clients_FIXE,count_valide_FIXE,null_clients_FIXE,not__null_clients_FIXE,count_joignable_FIXE









    




# Function to display data quality charts
def Dataquality(df_segmentation, df_contact, df_entete, df_adresse,df_ligne,df_email, df_telephone,df_media_invalide,choix):
    colors= ['#636EFA', '#00CC96', '#EF553B', 'skyblue']

    total_clients,counts_valide,not_null_clients,count_joignable_emails=calcul_email(df_email)
    total_clients_mobile,null_clients_Mobile,not_clients_mobile,count_joignable_mobile,count_valide_mobile=calcul_telephone_mobile(df_telephone)
    total_clients_FIXE,count_valide_FIXE,null_clients_FIXE,not__null_clients_FIXE,count_joignable_FIXE=calcul_telehone_Fixe(df_telephone)



    

    

# Load custom CSS

    # Calculations for the selected choice
    if choix == 'Email':
        


        values_email = [
            total_clients,
            counts_valide,
            not_null_clients,
            count_joignable_emails,
            
        ]

        stages_email = [
            "<b style='color:black;'>Total de clients:</b>",
            "<b style='color:black;'>Email valide:</b>",
            "<b style='color:black;'>Email renseignée:</b>",
            "<b style='color:black;'>Email joignable:</b>"
        ]

        domaine_counts = df_email['domaine'].value_counts().to_dict()
        colors_email = ['#636EFA', '#00CC96', '#EF553B', 'skyblue']
        colors= ['#636EFA', '#00CC96', '#EF553B', 'skyblue']
        custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        fig_donut_domaine = go.Figure(data=[go.Pie(
            labels=list(domaine_counts.keys()),
            values=list(domaine_counts.values()),
            hole=0.3,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>',
            marker=dict(colors=custom_colors)
        )])

        fig_donut_domaine.update_layout(
            title=dict(text='Distribution des domaines', x=0.5, xanchor='center'),
            title_font_color='black',
            title_font_size=17,
            title_x=0.5,
            title_y=0.95,
            title_font_family='Arial',
            legend_title='Domaines',
            legend_font_size=14,
            legend_traceorder='reversed',
            width=800,
            height=600
        )

        bar_chart = go.Figure(go.Bar(
            x=stages_email,
            y=values_email,
            text=values_email,
            textposition='auto',
            marker_color=colors_email,
            width=0.2,

        ))

        

        bar_chart.update_layout(title="Qualité des données Email",
                                title_font_color='black')
        st.sidebar.markdown("<h3 style='color: #FFFFFF;'> Choisir le type de données</h3>", unsafe_allow_html=True)
        
        inject_css_for_dataquality()


        selected_filter=st.sidebar.selectbox (
            'Select media_invalide_detail',
            ['All', 'VERIFICATION EMAIL', 'HARDBOUNCE'],key="media_invalide")
        

        
        
        
        if selected_filter != 'All':
            df_filtered=df_media_invalide
            
        elif selected_filter!= 'VERIFICATION EMAIL':
            df_filtered = df_media_invalide[df_media_invalide['media_invalide_detail'] == 'VERIFICATION EMAIL']
            
        elif selected_filter!= 'HARDBOUNCE':
            df_filtered = df_media_invalide[df_media_invalide['media_invalide_detail'] == 'HARDBOUNCE']
            

        else:
            df_filtered = df_media_invalide()
            

        
        media_count=df_filtered['detail'].value_counts()
        
        stages = media_count.index.tolist()
        counts = media_count.values.tolist()
        colors = ['#636EFA', '#00CC96', '#EF553B', '#AB63FA'][:len(stages)]




        
        bar_chart_media = go.Figure(data=[
    go.Bar(
        x=stages,
        y=counts,
        textposition='auto',
        marker_color=colors,
        width=0.2
    )
])
        
        


        bar_chart_media.update_layout(
    title='Media Invalid  par Detail',
    title_font_color='black',
    xaxis_title='Detail',
    yaxis_title='Valeurs',
    xaxis=dict(
        tickmode='array',
        tickvals=stages
    )
)    

        

        

        

        



        





# Show the figure
       

       

        col2,col3 = st.columns([3,3])
        
        col2.plotly_chart(bar_chart)
        col3.plotly_chart(bar_chart_media)

        col1=st.columns([12])
        st.plotly_chart(fig_donut_domaine)
        

    elif choix == 'Genre':
        total_clients = len(df_contact)
        null_clients = len(df_contact[df_contact['genre'].isnull()])
        not_null_clients = total_clients - null_clients

        values_genre = [
            
            not_null_clients,
            null_clients,
        ]

        stages_genre = [
            
            "<b style='color:black;'>Genre  non renseignés:</b>",
            "<b style='color:black;'>Genre  renseigné:</b>",
        ]

        fig_donut_genre = go.Figure(data=[go.Pie(
        labels=stages_genre,
        values=values_genre,
        hole=0.3,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>',
        marker=dict(colors=("Orange","blue")
        ))])


        st.plotly_chart(fig_donut_genre,width=100, height=100)

    elif choix == "date_naissance":
        total_clients = len(df_contact)
        null_clients_naissance = len(df_contact[df_contact['date_naissance'].isnull()])
        not_null_clients_naissance = total_clients - null_clients_naissance 
        values_naissance=[ null_clients_naissance,not_null_clients_naissance]
        
        stages_naissance = [
           
            "<b style='color:black;'>Naissancee  renseignés:</b>",
            "<b style='color:black;'>Naissance non  renseigné:</b>",
        ]
           
        fig_donut = go.Figure(data=[go.Pie(
        labels=stages_naissance,
        values=values_naissance,
        hole=0.3,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>',
        marker=dict(colors=("Orange","blue")
        ))])        
        

        
        


        fig_donut.update_layout(title="Qualité des données Date de naissance",
                                title_font_color='black')
        st.plotly_chart(fig_donut)

    elif choix == "telephone mobile":
        
        values_tel = [
            total_clients_mobile,
            count_valide_mobile,
            not_clients_mobile,
            count_joignable_mobile,
            
        ]

        stages_tel = [
            "<b style='color:black;'>Total de clients:</b>",
            "<b style='color:black;'>Téléphone Mobile valide:</b>",
            "<b style='color:black;'>Téléphone Mobile renseigné:</b>",
            "<b style='color:black;'>Téléphone Mobile joingable:</b>"
        ]

        bar_chart_telephone_mobile = go.Figure(go.Bar(
            x=stages_tel,
            y=values_tel,
            text=values_tel,
            textposition='auto',
            marker_color=colors,
            width=0.2
        ))

        bar_chart_telephone_mobile.update_layout(title="Qualité des données Téléphone Mobile",
                                                 title_font_color='black')
        st.plotly_chart(bar_chart_telephone_mobile)


    elif choix == "telephone Fixe":
        
        
        values_tel = [
            total_clients_FIXE,
            count_valide_FIXE,
            not__null_clients_FIXE,
            count_joignable_FIXE,
        ]

        stages_tel = [
            "<b style='color:black;'>Total de clients:</b>",
            "<b style='color:black;'> Téléphone FIXE valide:</b>",
            "<b style='color:black;'>  Téléphone renseigné :</b>",
            "<b style='color:black;'> Téléphone FIXE joignable:</b>"
        ]

        bar_chart_telephone_FIXE = go.Figure(go.Bar(
            x=stages_tel,
            y=values_tel,
            text=values_tel,
            textposition='auto',
            marker_color=colors,
            width=0.2
        ))


        bar_chart_telephone_FIXE .update_layout(title="Qualité des données Téléphone Fixe",title_font_color='black')
        st.plotly_chart(bar_chart_telephone_FIXE )

        





# Fetch data
df_segmentation, df_contact, df_entete, df_adresse, df_ligne, df_email,df_telephone,df_media_invalide=fetch_data()

# Selector in the sidebar
choix = st.sidebar.selectbox("Choisir le type de données",["Email", "Genre", "date_naissance","telephone mobile","telephone Fixe"])

# Call the function to display the charts
Dataquality(df_segmentation, df_contact, df_entete, df_adresse, df_ligne, df_email,df_telephone,df_media_invalide,choix)

