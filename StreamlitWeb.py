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


## Here we are merging the Study table,Facility Table and the Browse Conditions

df_merge=df_study.merge(df_facil,on="nct_id",how="left")
df_merge1=df_merge.merge(df_con,on="nct_id",how="left")


## we are applying filters on df_merge1

df_merge1=df_merge1[df_merge1['mesh_term']==disease]
df_merge1=df_merge1[df_merge1['phase']==phase]
df_merge1=df_merge1[df_merge1['state']==location]

nct_id2=df_merge1["nct_id"].unique()


##Sample merg two tables

##"""df_merge=df_study.merge(df_spon,on="nct_id",how="left")"""

        
        
## df_con=df_con[df_con['mesh_term']==disease]



st.subheader('Trail Details')
df_study1=df_study[df_study["nct_id"].isin(nct_id2)]
st.write(df_study1)

st.subheader('Disease Name')
df_con1=df_con[df_con["nct_id"].isin(nct_id2)]
st.write(df_con1)

st.subheader('Trail Location')
df_facil1=df_facil[df_facil["nct_id"].isin(nct_id2)]
st.write(df_facil1)


st.subheader('Trail Patient Eligibility')
df_elg1=df_elg[df_elg["nct_id"].isin(nct_id2)]
st.write(df_elg1)


st.subheader('Trail Contacts')
df_facilcon1=df_facilcon[df_facilcon["nct_id"].isin(nct_id2)]
st.write(df_facilcon1)   

st.subheader('Trail Interventions')    
df_int1=df_int[df_int["nct_id"].isin(nct_id2)] 
st.write(df_int1)      


st.subheader('Trail Sponsors')
df_spon1=df_spon[df_spon["nct_id"].isin(nct_id2)]
st.write(df_spon1)



















##General Plotting


x=df_study.sample(500)
x["enrollment"].plot(kind="hist")


df_con.sample(10)
df_con["mesh_term"].nunique()
x=df_con["mesh_term"].value_counts()
