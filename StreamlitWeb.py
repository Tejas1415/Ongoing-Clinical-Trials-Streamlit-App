# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 20:05:17 2023

@author: karun
"""

from sqlalchemy import create_engine
import pandas as pd
import AACTConfig as C
import streamlit as st



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




##streamlit App

st.balloons()

st.write("""
         
# Ongoing Clinical Trails in USA 
         
        """)
        
st.sidebar.header('Select your Filters')        
        
disease=st.sidebar.selectbox('Disease',(df_con["mesh_term"].unique()))

phase=st.sidebar.selectbox('Phase',(df_study["phase"].unique()))

location=st.sidebar.selectbox('Location',(df_facil["state"].unique()))
        
        




st.subheader('Trail Details')
st.write(df_study)

st.subheader('Trail Location')
st.write(df_facil)


st.subheader('Trail Patient Eligibility')
st.write(df_elg)


st.subheader('Trail Contacts')
st.write(df_facilcon)   

st.subheader('Trail Interventions')     
st.write(df_int)      


st.subheader('Trail Sponsors')
st.write(df_spon)








##merg two tables

df_merge=df_study.merge(df_spon,on="nct_id",how="left")










##General Plotting


x=df_study.sample(500)
x["enrollment"].plot(kind="hist")


df_con.sample(10)
df_con["mesh_term"].nunique()
x=df_con["mesh_term"].value_counts()
