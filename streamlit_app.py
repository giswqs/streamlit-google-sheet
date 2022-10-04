# streamlit_app.py

import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import leafmap
from gsheetsdb import connect
from shapely.geometry import Polygon, mapping

st.set_page_config(layout="wide")

# Remove the sandwich menu in the upper right corner
hide_streamlit_style = """
            <style>
            # MainMenu {visibility: hidden;}
            header, footer {visibility: hidden;}
            div.block-container {padding-top:1rem;padding-left:2rem;padding-right:2rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("University of Tennessee Parking Lot Availability")

col1, col2 = st.columns([1, 3])

data = 'data/buildings.geojson'

gdf = gpd.read_file(data)
gdf = gdf.astype({"osmid": int})

# Create a connection object.
conn = connect()

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.


@st.cache(ttl=60)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows


# sheet_url = st.secrets["public_gsheets_url"]
# rows = run_query(f'SELECT * FROM "{sheet_url}"')

# # Print results.
# for row in rows:
#     st.write(f"{row.name} has a :{row.pet}:")

sheet_url = st.secrets["public_gsheets_parking"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

df = pd.DataFrame(rows)
df = df.astype({"osmid": int})
gdf2 = pd.merge(
    gdf, df[["osmid", "capacity", "remaining"]], on="osmid", how='outer')
with col1:
    st.header("Parking Lots")
    extruded = st.checkbox("3D View", value=False)
    st.dataframe(df)
    st.image(
        "https://brand.utk.edu/wp-content/uploads/sites/66/2019/02/University-HorizRightLogo-RGB.png")


layer = pdk.Layer(
    "GeoJsonLayer",
    gdf2,
    pickable=True,
    opacity=0.051,
    filled=True,
    stroked=True,
    extruded=extruded,
    wireframe=True,
    get_elevation="remaining",
    get_line_color=[255, 255, 0],
    get_fill_color=[165, 42, 42],
    get_line_width=1,
    line_width_min_pixels=1,
)

tooltip = {
    "text": "osmid: {osmid}\nbuilding: {building}\nname: {name}\namenity: {amenity}\ncapacity: {capacity}\nremaining: {remaining}",
}

with col2:
    st.pydeck_chart(
        pdk.Deck(
            # map_style=None,
            map_provider="mapbox",
            # map_style=pdk.map_styles.SATELLITE,
            initial_view_state=pdk.ViewState(
                latitude=35.951955,
                longitude=-83.930826,
                zoom=15,
                pitch=0,
                height=800,
            ),
            layers=[
                layer,
            ],
            tooltip=tooltip,
        )
    )
