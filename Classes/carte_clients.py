import streamlit as st
import pandas as pd
import folium
from shapely import wkt
from streamlit_folium import folium_static
from matplotlib import cm
import matplotlib.pyplot as plt

def map_color(value, min_value, max_value):
    cmap = plt.get_cmap('YlOrRd')
    norm = plt.Normalize(vmin=min_value, vmax=max_value)
    rgba = cmap(norm(value))
    hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))
    return hex_color

def show_clients_map(df_departements):
    st.markdown(
        """
        <style>
        .custom-header h2 {
            text-align: center;
            color: black;
        }
        </style>
        <div class="custom-header">
            <h2>Carte des clients par département</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Define map size
    map_width = 1200
    map_height = 1200

    # Create map
    m = folium.Map(location=[47.0, 1.0], zoom_start=6)
    france_bounds = [[41.333, -5.5], [51.124199, 9.6625]]

    # Restrict map view to France only
    m.fit_bounds(france_bounds)
    max_clients = df_departements["nombre_clients"].max()
    min_clients = df_departements["nombre_clients"].min()

    # Add departments to map
    for geo_shape, region_name, nombre_clients,per_client_per_departement, in zip(df_departements["WKT"], df_departements["nom"].str.replace('"', ' '), df_departements["nombre_clients"],df_departements['per_client_per_departement']):
        geometry = wkt.loads(geo_shape)
        color = map_color(nombre_clients, min_clients, max_clients)
        folium.GeoJson(
            geometry,
            style_function=lambda feature, color=color: {
                'fillColor': color,
                'color': 'black',
                'weight': 2,
                'dashArray': '5, 5',
                'fillOpacity': 0.5,
            },
            highlight_function=lambda feature: {
                "fillColor": "green" if "e" in region_name.lower() else "#34ebe5"
            },
            tooltip=f"{region_name}<br>Nombre de clients:{nombre_clients}<br> Pourcentage des clients: {per_client_per_departement:.2f}%" if not pd.isnull(nombre_clients) else region_name
        ).add_to(m)

    folium_static(m, width=map_width, height=map_height)
