# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 20:05:17 2023

@author: karun
"""

from sqlalchemy import create_engine
import pandas as pd
import AACTConfig as C
import streamlit as st
import plotly.graph_objects as go


@st.cache()
def Fetching_Clinical_Data():

    

    engine = create_engine(f'postgresql://{C.IDUsername}:{C.Password}@{C.Hostname}:5432/{C.Databasename}')
    
    
    sql_study = "SELECT nct_id,overall_status,phase,enrollment,enrollment_type FROM ctgov.studies x WHERE (overall_status IN ('Active, not recruiting','Available','Enrolling by invitation','Not yet recruiting','Recruiting','Unknown status')) AND (phase IN ('Early Phase 1','Phase 1','Phase 1/Phase 2','Phase 2','Phase 2/Phase 3','Phase 3','Phase 4'))"
    df_study = pd.read_sql(sql_study,con=engine)
    
    
    ongoing_nct=df_study["nct_id"].unique()
    t= tuple(ongoing_nct)
    
    
    sql_facil= "SELECT nct_id,city,state,zip FROM ctgov.facilities x WHERE (country IN ('United States')) AND (nct_id IN {})".format(t)
    df_facil = pd.read_sql(sql_facil,con=engine)
    
    
    
    sql_con="SELECT nct_id,mesh_term FROM ctgov.browse_conditions WHERE (nct_id IN {})".format(t)
    df_con = pd.read_sql(sql_con,con=engine)
    
    
    
    sql_elg="SELECT nct_id,gender,healthy_volunteers,minimum_age,maximum_age,criteria FROM ctgov.eligibilities WHERE (nct_id IN {})".format(t)
    df_elg = pd.read_sql(sql_elg,con=engine)
    
    
    
    sql_facilcon="SELECT nct_id,contact_type,name,email,phone FROM ctgov.facility_contacts WHERE (nct_id IN {})".format(t)
    df_facilcon = pd.read_sql(sql_facilcon,con=engine)
    
    
    
    sql_int="SELECT nct_id,intervention_type,name,description FROM ctgov.interventions WHERE (nct_id IN {})".format(t)
    df_int = pd.read_sql(sql_int,con=engine)
    
    
    
    sql_spon="SELECT nct_id,agency_class,lead_or_collaborator,name FROM ctgov.sponsors WHERE (nct_id IN {})".format(t)
    df_spon = pd.read_sql(sql_spon,con=engine)
    
    
    
    
    return df_study,df_facil,df_con,df_elg,df_facilcon,df_int,df_spon 


df_study,df_facil,df_con,df_elg,df_facilcon,df_int,df_spon = Fetching_Clinical_Data()


##streamlit App



st.balloons()



st.write("""
         
# Ongoing Clinical Trails in USA 
         
        """)
        
st.sidebar.header('Select your Filters')        
        
disease=st.sidebar.selectbox('Disease',(df_con["mesh_term"].unique()))

phase=st.sidebar.selectbox('Phase',(df_study["phase"].unique()))





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



## Location


###fig = px.choropleth(locations=df_facil['state'], locationmode="USA-states", scope="usa")
###fig.show()

## USA state Abbrev

df_facilcount= df_facil1['state'].value_counts().reset_index()
df_facilcount=df_facilcount.rename(columns={'index':'State','state':'Count'})



us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
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
    title_text = 'Location of Going Clinical Trails in USA State-Wise ',
    geo_scope='usa', # limite map scope to USA 
    plot_bgcolor='rgb(0,0,0,0)',
    
)




## Displaying of each Table


st.subheader('Trail Details')
st.dataframe(data=df_study1, width=700, height=768)
###st.write(df_study1)


st.subheader('Location')
st.dataframe(data=df_facil1, width=700, height=768)
###st.write(df_facil1)

## Displaying of Map

st.plotly_chart(fig)

## Displaying of each Table

st.subheader('Disease Name')
st.dataframe(data=df_con1, width=700, height=768)
###st.write(df_con1)



st.subheader('Patient Eligibility')
st.dataframe(data=df_elg1, width=700, height=768)
###st.write(df_elg1)


st.subheader('Contacts')
st.dataframe(data=df_facilcon1, width=700, height=768)
###st.write(df_facilcon1)   



st.subheader('Trail Interventions')    
st.dataframe(data=df_int1, width=700, height=768)
###st.write(df_int1)      


st.subheader('Sponsors')
st.dataframe(data=df_spon1, width=700, height=768)
###st.write(df_spon1)




st.write('All the Above Data was extracted from the AACT Clinical Trail Database')








