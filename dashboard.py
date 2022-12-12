import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests, json
import plotly.graph_objects as pgo 
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium

# page and data config
APP_TITLE = "SDC Dashboard Covid-19"
APP_SUB_TITLE = "Author: Beatrice Pscheidl"
st.set_page_config(layout="wide")
locations = pd.DataFrame([
    ['Africa', '0', '18', '3', 'data/africa.geojson'],
    ['Asia', '25', '85', '3', 'data/asia.geojson'],
    ['North America', '55', '-100', '3', 'data/namerica.geojson'],
    ['South America', '-12', '-65', '3', 'data/samerica.geojson'],
    ['Europe', '57', '25', '3.4', 'data/europe.geojson'],
    ['Australia/Oceania', '-23', '133', '3', 'data/oceania.geojson']]
)
locations.columns = ['Continent', 'Lat', 'Lon', 'Zoom', 'GeoJSON']
locations.set_index('Continent', inplace=True)

# load data into cache
@st.cache
def read_epi():
    df = pd.read_csv("data/epidemiology_processed.csv")
    return df

@st.cache
def read_health():
    df = pd.read_csv("data/health_processed.csv")
    return df

@st.cache
def read_hosp():
    df = pd.read_csv("data/hospitalizations_processed.csv")
    return df

@st.cache
def read_vacc():
    df = pd.read_csv("data/vaccinations_processed.csv")
    return df

@st.cache
def read_weather():
    df = pd.read_csv("data/weather_processed.csv")
    return df

# display map function
def display_map(continent, df):
    loc = [locations.loc[continent]['Lat'], locations.loc[continent]['Lon']]
    zoom = locations.loc[continent]['Zoom']
    gjsn = locations.loc[continent]['GeoJSON']
    map = folium.Map(location=loc, zoom_start=zoom, tiles="CartoDB positron")
    choropleth = folium.Choropleth(
        geo_data = gjsn,
        data = df,
        columns = ("ISO_A3", 'len'),
        key_on = "feature.properties.ISO_A3",
        highlight=True
    )
    choropleth.geojson.add_to(map)
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['ISO_A3'], labels=False)
    )
    st_map = st_folium(map, width=700, height=450)

    state = ''
    if st_map['last_active_drawing']:
        state = st_map['last_active_drawing']['properties']['ISO_A3']
    return state

# create chart function
def create_chart(df, country, year, cw):
    # retrieve start end of timeseries from FastAPI endpoint
    url = "http://127.0.0.1:8000/get_calenderweek_dates/" + str(cw) + "/" + str(year) 
    response = requests.get(url)
    dates = json.loads(response.content)
    start = pd.to_datetime(dates['start'])
    end = pd.to_datetime(dates['end'])
    st.write("Selected Timeframe: " + start.strftime("%m/%d/%Y") + " to " + end.strftime("%m/%d/%Y"))

    # chart
    series = df[
        (df["country_name"]==country) 
            & (pd.to_datetime(df["date"]) >= start)
            & (pd.to_datetime(df["date"]) <= end)
    ].get(['new_confirmed', 'new_deceased', 'date'])
    chart = make_subplots(specs=[[{"secondary_y": True}]])
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['new_confirmed'], name="New Confirmed"),
        secondary_y=False
    )
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['new_deceased'], name="New Deceased"),
        secondary_y=True
    )
    chart.update_layout(title_text="Confirmed Cases and Deaths")
    chart.update_xaxes(title_text="Date")
    chart.update_yaxes(title_text="New Confirmed", secondary_y=False)
    chart.update_yaxes(title_text="New Deceased", secondary_y=True)
    return chart

# render country general information
def render_information(key, df):
    health_info = df[df['location_key'] == key]
    st.header("General Information")
    st.write("Population: " + str(health_info['population'].iloc[0]))
    st.write("Life Expectancy: " + str(health_info['life_expectancy'].iloc[0]) + " yrs")
    st.write("Diabetes Prevalence: " + str(health_info['diabetes_prevalence'].iloc[0]) + " %")
    st.write("Smoking Prevalence: " + str(health_info['smoking_prevalence'].iloc[0]) + " %")
    #st.write("Hospital Beds: " + str(health_info['hospital_beds_per_1000'].iloc[0]) + " per 1000 inh.")
    st.write("Health Expenditure " + str(health_info['health_expenditure_usd'].iloc[0]) + " USD")

# render epidemiology chart
def render_epidemiology_chart(key, df):
    series = df[
        (df["location_key"]==key)
    ].get(['new_confirmed', 'new_deceased', 'date'])
    chart = make_subplots(specs=[[{"secondary_y": True}]])
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['new_confirmed'], name="New Confirmed"),
        secondary_y=False
    )
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['new_deceased'], name="New Deceased"),
        secondary_y=True
    )
    #chart.update_layout(title_text="Confirmed Cases and Deaths")
    chart.update_xaxes(title_text="Date")
    chart.update_yaxes(title_text="New Confirmed", secondary_y=False)
    chart.update_yaxes(title_text="New Deceased", secondary_y=True)
    st.header("Epidemiology Information")
    st.plotly_chart(chart)

# render vaccinations chart
def render_vaccinations_chart(key, df):
    series = df[
        (df["location_key"]==key)
    ].get(['new_persons_vaccinated', 'cumulative_persons_vaccinated', 'date'])
    chart = make_subplots(specs=[[{"secondary_y": True}]])
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['new_persons_vaccinated'], name="Persons vaccinated"),
        secondary_y=False
    )
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['cumulative_persons_vaccinated'], name="Cummulative vaccinations"),
        secondary_y=True
    )
    #chart.update_layout(title_text="Confirmed Cases and Deaths")
    chart.update_xaxes(title_text="Date")
    chart.update_yaxes(title_text="Persons vaccinated", secondary_y=False)
    chart.update_yaxes(title_text="Cummulative vaccinations", secondary_y=True)
    st.header("Vaccinations Information")
    st.plotly_chart(chart)

# render weather chart
def render_weather_chart(key, df):
    series = df[
        (df["location_key"]==key)
    ].get(['average_temperature_celsius', 'relative_humidity', 'date'])
    chart = make_subplots(specs=[[{"secondary_y": True}]])
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['average_temperature_celsius'], name="Avg. Temperature"),
        secondary_y=False
    )
    chart.add_trace(
        pgo.Scatter(x=series['date'], y=series['relative_humidity'], name="Avg. Rel. Humidity"),
        secondary_y=True
    )
    #chart.update_layout(title_text="Confirmed Cases and Deaths")
    chart.update_xaxes(title_text="Date")
    chart.update_yaxes(title_text="Avg. Temperature", secondary_y=False)
    chart.update_yaxes(title_text="Avg. Rel. Humidity", secondary_y=True)
    st.header("Weather Information")
    st.plotly_chart(chart)

# retrieve locations
def get_locations(address):
    url = "http://127.0.0.1:8000/calculate_lat_lon/" + address
    response = requests.get(url)
    location = json.loads(response.content)
    lat = location['lat']
    lon = location['lon']
    return lat, lon
    

# main function of dashboard
def main():
    # read data
    df_epidemiology = read_epi()
    df_health = read_health()
    df_hospitalizations = read_hosp()
    df_vaccinations = read_vacc()
    df_weather = read_weather()

    # app title
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    # set up columns (2 columns)
    left, right = st.columns(2)

    # left column
    with left:
        # upper part of left side
        continent_1 = st.selectbox(
           'Select Continent',
           list(locations.index.values)
        )
        selected_state = display_map(continent_1, df_epidemiology)

        # horizontal line
        st.caption("""---""")

        # lower part of left side
        country_2 = st.selectbox(
            "Select Country",
            df_epidemiology["country_name"].unique()
        )
        year_2 = st.radio(
            label="Select Year",
            options=("2020", "2021", "2022"),
            index=0,
            horizontal=True
        )
        cw_2 = st.selectbox(
            "Select calendar week",
            list(range(1,53))
        )

        # # gauge
        # gauge_2 = pgo.Figure(pgo.Indicator(
        #     mode = "gauge+number",
        #     value = 270,
        #     domain = {'x': [0, 1], 'y': [0, 1]},
        #     title = {'text': "7-Day Incidence"})
        # )
        # st.plotly_chart(gauge_2)

        # timeseries chart
        chart_2 = create_chart(df_epidemiology, country_2, year_2, cw_2)
        st.plotly_chart(chart_2)

    # right column
    with right:
        if selected_state:
            st.write("Selected country: " + selected_state)
        else:
            st.write("Please use the map to select a country!")

        if selected_state:
            # get location key from epidemology df
            location_key = pd.unique(df_epidemiology[df_epidemiology['ISO_A3'] == selected_state]['location_key'])[0]
            render_information(location_key, df_health)
            render_epidemiology_chart(location_key, df_epidemiology)
            render_vaccinations_chart(location_key, df_vaccinations)
            render_weather_chart(location_key, df_weather)

    # reset layout
    f1, f2 = st.columns(2)
    with f1:
        # FastAPI Location Example
        address = st.text_input(label="Search Address:", value="Höchstädtplatz 5, 1200 Wien")
        if address:
            lat, lon = get_locations(address)
            latlon = pd.DataFrame({
                'lat': [lat],
                'lon': [lon]
            })
            st.map(latlon)
        else:
            # default: show FH on the map
            st.map(
                pd.DataFrame({
                    'lat': [48.23931055], 
                    'lon': [16.378076104231624]
                })
            )

if __name__ == "__main__":
    main()