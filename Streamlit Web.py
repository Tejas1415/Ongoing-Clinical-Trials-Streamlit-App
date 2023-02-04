# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 20:05:17 2023

@author: karun
"""

from sqlalchemy import create_engine
import pandas as pd
import AACTConfig as C


engine = create_engine(f'postgresql://{C.IDUsername}:{C.Password}@{C.Hostname}:5432/{C.Databasename}')


sql_study = "SELECT x.* FROM ctgov.studies x WHERE overall_status IN ('Active, not recruiting','Available','Enrolling by invitation','Not yet recruiting','Recruiting','Unknown status')"
df_study = pd.read_sql(sql_study,con=engine)


sql_facil= "SELECT x.* FROM ctgov.facilities x WHERE country IN ('United States')"
df_facil = pd.read_sql(sql_facil,con=engine)


sql_con="SELECT nct_id,mesh_term FROM ctgov.browse_conditions"
df_con = pd.read_sql(sql_con,con=engine)



sql_elg="SELECT nct_id,minimum_age,maximum_age FROM ctgov.eligibilities "
df_elg = pd.read_sql(sql_elg,con=engine)



sql_facilcon="SELECT x.* FROM ctgov.facility_contacts x "
df_facilcon = pd.read_sql(sql_facilcon,con=engine)



sql_int="SELECT x.* FROM ctgov.interventions x "
df_int = pd.read_sql(sql_int,con=engine)


sql_spon="SELECT x.* FROM ctgov.sponsors x "
df_spon = pd.read_sql(sql_spon,con=engine)





df_con.sample(10)
df_con["mesh_term"].nunique()
x=df_con["mesh_term"].value_counts()
