# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 20:05:17 2023

@author: Manasa and Tejas
"""

from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

@st.cache_resource
def get_engine():
    # Use AACTConfig.py to get the engine connected to the database
    #import AACTConfig as C
    #engine = create_engine(f'postgresql://{C.IDUsername}:{C.Password}@{C.Hostname}:5432/{C.Databasename}', pool_pre_ping=True, pool_recycle=3600)     # Verify connections before using, # Recycle connections after 1 hour

    # Use streamlit secrets to get the engine connected to the database     
    engine = create_engine(f'postgresql://{st.secrets["IDUsername"]}:{st.secrets["Password"]}@{st.secrets["Hostname"]}:{st.secrets["Port"]}/{st.secrets["Databasename"]}', pool_pre_ping=True, pool_recycle=3600)
    
    return engine

@st.cache_data(ttl=3600, max_entries=1)  # Cache for 1 hour, avoid cache growth
def Fetching_Clinical_Data():
    
    engine = get_engine()
    
    ## From the study table, get only the required columns one per NCT_ID for only ongoing trials.
    sql_study = "SELECT nct_id, overall_status, last_known_status, phase, enrollment, enrollment_type FROM ctgov.studies WHERE overall_status IN ('ACTIVE_NOT_RECRUITING', 'AVAILABLE', 'ENROLLING_BY_INVITATION', 'NOT_YET_RECRUITING', 'RECRUITING', 'UNKNOWN', 'TEMPORARILY_NOT_AVAILABLE') AND phase IN ('EARLY_PHASE1', 'PHASE1', 'PHASE1/PHASE2', 'PHASE2', 'PHASE2/PHASE3', 'PHASE3', 'PHASE4')"
    df_study = pd.read_sql(sql_study,con=engine)
    
    ## Get the unique NCT_IDs for the ongoing trials.
    ongoing_nct=df_study["nct_id"].unique()
    t= tuple(ongoing_nct)
    
    ## Get the facilities data for the ongoing trials.
    sql_facil= "SELECT nct_id,city,state,zip FROM ctgov.facilities x WHERE (country IN ('United States')) AND (nct_id IN {})".format(t)
    df_facil = pd.read_sql(sql_facil,con=engine)
    
    ## Get the browse conditions data for the ongoing trials.
    sql_con="SELECT nct_id,mesh_term FROM ctgov.browse_conditions WHERE (nct_id IN {})".format(t)
    df_con = pd.read_sql(sql_con,con=engine)
    
    ## Get the eligibilities data for the ongoing trials.
    sql_elg="SELECT nct_id,gender,healthy_volunteers,minimum_age,maximum_age,criteria FROM ctgov.eligibilities WHERE (nct_id IN {})".format(t)
    df_elg = pd.read_sql(sql_elg,con=engine)
    
    ## Get the facility contacts data for the ongoing trials.
    sql_facilcon="SELECT nct_id,contact_type,name,email,phone FROM ctgov.facility_contacts WHERE (nct_id IN {})".format(t)
    df_facilcon = pd.read_sql(sql_facilcon,con=engine)
    
    ## Get the interventions data for the ongoing trials.
    sql_int="SELECT nct_id,intervention_type,name,description FROM ctgov.interventions WHERE (nct_id IN {})".format(t)
    df_int = pd.read_sql(sql_int,con=engine)
    
    ## Get the sponsors data for the ongoing trials.
    sql_spon="SELECT nct_id,agency_class,lead_or_collaborator,name FROM ctgov.sponsors WHERE (nct_id IN {})".format(t)
    df_spon = pd.read_sql(sql_spon,con=engine)
    
    return df_study,df_facil,df_con,df_elg,df_facilcon,df_int,df_spon 



## Fetch the latest data from the database.
df_study,df_facil,df_con,df_elg,df_facilcon,df_int,df_spon = Fetching_Clinical_Data()



########################### Streamlit App

## Display baloons animation every time the execution of the code is complete.
st.balloons()


## Display the title of the app.
st.write("""
# Ongoing Clinical Trials in the United States

Every day, thousands of clinical trials are conducted across the United States — pushing the boundaries of medical innovation and offering new hope to patients in need.

However, accessing these opportunities for a layman is challenging. Existing platforms are difficult to navigate for the general public to explore life-saving opportunities for their need in their geographical location.

To bridge this gap, we developed this intuitive, user-friendly dashboard that helps users:

- Discover ongoing clinical trials based on specific medical conditions and trial phases  
- Identify study locations conveniently accessible to them  
- Access key details such as eligibility criteria, interventions, and contact information  

This tool not only empowers patients, caregivers, and healthcare advocates with clear and accessible information — it also supports organizations in improving patient recruitment, one of the key reasons for clinical trial failure, especially in rare disease categories.
""")
## Display the sidebar with the filters.
st.sidebar.header('Select your Filters')        
## Display the disease filter.
disease=st.sidebar.selectbox('Disease Category',(df_con["mesh_term"].unique()))
## Display the phase filter.    
phase=st.sidebar.selectbox('Phase',(df_study["phase"].unique()))



############# Based on the filters and filter the cached data to display relevant tables in the app.

## Here we are merging the Study table,Facility Table and the Browse Conditions
df_merge=df_study.merge(df_facil,on="nct_id",how="left")
df_merge1=df_merge.merge(df_con,on="nct_id",how="left")


## we are applying filters on df_merge1
df_merge1=df_merge1[df_merge1['mesh_term']==disease]
df_merge1=df_merge1[df_merge1['phase']==phase]
###df_merge1=df_merge1[df_merge1['state']==location]

nct_id2=df_merge1["nct_id"].unique()



## Displaying of all the Filterred Data Frames

df_study1=df_study[df_study["nct_id"].isin(nct_id2)]
df_con1=df_con[df_con["nct_id"].isin(nct_id2)]
df_facil1=df_facil[df_facil["nct_id"].isin(nct_id2)]
df_elg1=df_elg[df_elg["nct_id"].isin(nct_id2)]
df_facilcon1=df_facilcon[df_facilcon["nct_id"].isin(nct_id2)]
df_int1=df_int[df_int["nct_id"].isin(nct_id2)] 
df_spon1=df_spon[df_spon["nct_id"].isin(nct_id2)]



## Location - Use plotly to show US map with a heat filter to indicate number of centers open in each state
## USA state Abbrev

df_facilcount= df_facil1['state'].value_counts().reset_index()
df_facilcount=df_facilcount.rename(columns={'state':'State','count':'Count'})

us_state_to_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "District of Columbia": "DC", "American Samoa": "AS", "Guam": "GU", "Northern Mariana Islands": "MP", "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM", "U.S. Virgin Islands": "VI",
}



us_state_to_abbrev = {state: abbrev for state, abbrev in us_state_to_abbrev.items()}
df_facilcount['abbrev'] = df_facilcount['State'].map(us_state_to_abbrev)



## ABBREV of Plotly (Location of States)
fig = go.Figure(data=go.Choropleth(
    locations=df_facilcount['abbrev'], # Spatial coordinates
    z = df_facilcount['Count'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'sunset',
    colorbar_title = "State Count",
))

fig.update_layout(
    title_text = 'Location of Going Clinical Trials in USA State-Wise ',
    geo_scope='usa', # limite map scope to USA 
    plot_bgcolor='rgb(0,0,0,0)',
    
)






################# Now that the figure and filtered tables are ready, display them in the app.


st.subheader('Trial Details')
st.write(
    "In this table, you will find one trial per row that is currently ongoing in the selected disease and phase.\n"
    "Find the NCT ID's that are of interest to you to grab further useful information from the other tables.\n"
    "Observe the trials that are actively recruiting or about to start recruiting in the phase you are comfortable with.\n"
    "You would also find information on the number of participants they are estimating to recruit in each trial."
)
st.dataframe(data=df_study1, width=700, height=768)
###st.write(df_study1)


st.subheader('Location')
st.write(
    "In this table, for each NCT ID you found interesting in the above table, you will find multiple locations where the trial has centers that are open for enrollment.\n"
    "Find the trials that are ongoing in an area in USA that you are comfortable with if you want to participate in the trial."
)
st.dataframe(data=df_facil1, width=700, height=768)
###st.write(df_facil1)

## Displaying of Map
st.subheader('Location Map')
st.write("This map shows the number of centers open in each state for the trials that are currently ongoing in the selected disease and phase.")
st.plotly_chart(fig)


## Displaying of each Table
st.subheader('Disease Name')
st.write("This table shows the specific disease name in the broader disease category you selected for the trials that are currently ongoing in the selected disease category and phase.")
st.dataframe(data=df_con1, width=700, height=768)
###st.write(df_con1)



st.subheader('Patient Eligibility')
st.write("This table shows the patient eligibility criteria for the trials that are currently ongoing in the selected disease and phase. Check this table to see if you are eligible for the trial.")
st.dataframe(data=df_elg1, width=700, height=768)
###st.write(df_elg1)


st.subheader('Contacts')
st.write("So far if you have chosen a trial that you are interested in, found the location you are comfortable with, checked the patient eligibility criteria and now you are ready to contact the trial team for more information.\n" 
"This table shows the contact information for the trials that are currently ongoing in the selected disease and phase. You can contact the trial team for more information.")
st.dataframe(data=df_facilcon1, width=700, height=768)
###st.write(df_facilcon1)   



st.subheader('Trial Interventions')    
st.write("This is additional information to help you understand how the trial aims to treat the disease. It shows the type of intervention, the name of the intervention and the description of the intervention.")
st.dataframe(data=df_int1, width=700, height=768)
###st.write(df_int1)      


st.subheader('Sponsors')
st.write("This is additional information on which organization (NGO, University or Company) is sponsoring this trial.")
st.dataframe(data=df_spon1, width=700, height=768)
###st.write(df_spon1)




st.write('All the Above Data was extracted from the AACT Clinical Trial Database')








