# --------------------------------------------
# Script for preprocessing data 
# from Google Covid-19 Open Data sources
# --------------------------------------------

import pandas as pd
import pycountry
import json

def get_country_info(location_key, field):
    if location_key:
        country = pycountry.countries.get(alpha_2=location_key)
        if country:
            if field == "name":
                return country.name
            elif field == "alpha_3":
                return country.alpha_3
        else:
            return ""

def filter_for_region(region, countries, geodata):
    features = []
    rgnlist = list(countries[countries['region']==region]['alpha-3'])
    for x in geodata['features']:
        if x['properties']['ISO_A3'] in rgnlist:
            features.append(x)
    return features

def filter_for_subregion(subregion, countries, geodata):
    features = []
    rgnlist = list(countries[countries['sub-region']==subregion]['alpha-3'])
    for x in geodata['features']:
        if x['properties']['ISO_A3'] in rgnlist:
            features.append(x)
    return features

# --------------------------------------------
# Epidemiology data
# --------------------------------------------
df = pd.read_csv("data/epidemiology.csv")
df2 = pd.read_csv("data/demographics.csv")
df2.set_index('location_key', inplace=True)

# create year and calendar week columns from date
df['year'] = pd.to_datetime(df["date"]).dt.strftime('%Y')
df['cw'] = pd.to_datetime(df["date"]).dt.strftime('%U')

# drop unwanted columns
df.drop(["new_recovered","new_tested","cumulative_confirmed","cumulative_deceased","cumulative_recovered","cumulative_tested"], axis=1, inplace=True)

# drop unwanted rows (country subdivisions)
df['len'] = df.apply(lambda x: len(str(x['location_key'])), axis=1)
df = df[df['len'] == 2]

# get country name and ISO_A3 value for map
df['country_name'] = df.apply(lambda x: get_country_info(x['location_key'], "name"), axis=1)
df['ISO_A3'] = df.apply(lambda x: get_country_info(x['location_key'], "alpha_3"), axis=1)

# export to csv
df.to_csv("data/epidemiology_processed.csv")
# --------------------------------------------

# --------------------------------------------
# Health data
# --------------------------------------------
df = pd.read_csv("data/health.csv")
df = df.join(df2, on='location_key')

# drop unwanted rows and columns
df.drop(["infant_mortality_rate","adult_male_mortality_rate","adult_female_mortality_rate","pollution_mortality_rate","comorbidity_mortality_rate","nurses_per_1000","physicians_per_1000","out_of_pocket_health_expenditure_usd",
         "population_male","population_female","population_rural","population_urban","population_largest_city","population_clustered","population_density","human_development_index","population_age_00_09","population_age_10_19",
         "population_age_20_29","population_age_30_39","population_age_40_49","population_age_50_59","population_age_60_69","population_age_70_79","population_age_80_and_older"], 
         axis=1, inplace=True)
df['len'] = df.apply(lambda x: len(str(x['location_key'])), axis=1)
df = df[df['len'] == 2]


# save to csv
df.to_csv("data/health_processed.csv")
# --------------------------------------------

# --------------------------------------------
# Hospitalizations data
# --------------------------------------------
df = pd.read_csv("data/hospitalizations.csv")

# drop unwanted rows and columns
df.drop(["new_hospitalized_patients","current_hospitalized_patients","new_intensive_care_patients","cumulative_intensive_care_patients","current_intensive_care_patients","new_ventilator_patients","cumulative_ventilator_patients","current_ventilator_patients"], axis=1, inplace=True)
df['len'] = df.apply(lambda x: len(str(x['location_key'])), axis=1)
df = df[df['len'] == 2]

# save to csv
df.to_csv("data/hospitalizations_processed.csv")
# --------------------------------------------

# --------------------------------------------
# Vaccinations data
# --------------------------------------------
df = pd.read_csv("data/vaccinations.csv")

# drop unwanted rows and columns
df.drop(["new_persons_fully_vaccinated","cumulative_persons_fully_vaccinated","new_vaccine_doses_administered","cumulative_vaccine_doses_administered","new_persons_vaccinated_pfizer","cumulative_persons_vaccinated_pfizer","new_persons_fully_vaccinated_pfizer","cumulative_persons_fully_vaccinated_pfizer","new_vaccine_doses_administered_pfizer","cumulative_vaccine_doses_administered_pfizer","new_persons_vaccinated_moderna","cumulative_persons_vaccinated_moderna","new_persons_fully_vaccinated_moderna","cumulative_persons_fully_vaccinated_moderna","new_vaccine_doses_administered_moderna","cumulative_vaccine_doses_administered_moderna","new_persons_vaccinated_janssen","cumulative_persons_vaccinated_janssen","new_persons_fully_vaccinated_janssen","cumulative_persons_fully_vaccinated_janssen","new_vaccine_doses_administered_janssen","cumulative_vaccine_doses_administered_janssen","new_persons_vaccinated_sinovac","total_persons_vaccinated_sinovac","new_persons_fully_vaccinated_sinovac","total_persons_fully_vaccinated_sinovac","new_vaccine_doses_administered_sinovac","total_vaccine_doses_administered_sinovac"], axis=1, inplace=True)
df['len'] = df.apply(lambda x: len(str(x['location_key'])), axis=1)
df = df[df['len'] == 2]

# save to csv
df.to_csv("data/vaccinations_processed.csv")
# --------------------------------------------

# --------------------------------------------
# Weather data
# --------------------------------------------
df = pd.read_csv("data/weather.csv")

# drop unwanted rows and columns
df.drop(["minimum_temperature_celsius","maximum_temperature_celsius","rainfall_mm","snowfall_mm","dew_point"], axis=1, inplace=True)
df['len'] = df.apply(lambda x: len(str(x['location_key'])), axis=1)
df = df[df['len'] == 2]

# save to csv
df.to_csv("data/weather_processed.csv")
# --------------------------------------------

# --------------------------------------------
# Continent data
# --------------------------------------------
# load countries info from csv
countries = pd.read_csv("data/countries.csv")

# load geojson file to dict
with open("data/countries.geojson", 'r', encoding='utf-8') as f:
    geojson = json.load(f)

# Africa ---
geojson_region = geojson.copy()
geojson_region['features'] = filter_for_region("Africa", countries, geojson_region)

# save to single file
with open("data/africa.geojson", 'w', encoding='utf-8') as f:
    f.write(json.dumps(geojson_region, indent=2))

# Europe ---
geojson_region = geojson.copy()
geojson_region['features'] = filter_for_region("Europe", countries, geojson_region)

# save to single file
with open("data/europe.geojson", 'w', encoding='utf-8') as f:
    f.write(json.dumps(geojson_region, indent=2))

# Asia ---
geojson_region = geojson.copy()
geojson_region['features'] = filter_for_region("Asia", countries, geojson_region)

# save to single file
with open("data/asia.geojson", 'w', encoding='utf-8') as f:
    f.write(json.dumps(geojson_region, indent=2))

# North-America ---
geojson_region = geojson.copy()
geojson_region['features'] = filter_for_subregion("Northern America", countries, geojson_region)

# save to single file
with open("data/namerica.geojson", 'w', encoding='utf-8') as f:
    f.write(json.dumps(geojson_region, indent=2))

# South-America ---
geojson_region = geojson.copy()
geojson_region['features'] = filter_for_subregion("Latin America and the Caribbean", countries, geojson_region)

# save to single file
with open("data/samerica.geojson", 'w', encoding='utf-8') as f:
    f.write(json.dumps(geojson_region, indent=2))

# Oceania ---
geojson_region = geojson.copy()
geojson_region['features'] = filter_for_region("Oceania", countries, geojson_region)

# save to single file
with open("data/oceania.geojson", 'w', encoding='utf-8') as f:
    f.write(json.dumps(geojson_region, indent=2))
# --------------------------------------------
