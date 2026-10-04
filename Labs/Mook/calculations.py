# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 23:00:07 2026

@author: brian

This script performs calculations on the data for the Mook lab that we did for
the class.
"""

import os
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt

cwd = Path(os.getcwd())
dataPath = cwd/"Data for Mook Lab-clean.xlsx"
data = (pd.read_excel(dataPath, "Final Results")
        .rename(columns={"13C of CO2": "delta13C_CO2"})
        .dropna()
        )
dataIDsplit = (data.ID.str.split("-", expand=True)
               .rename(columns={0: "group", 1: "vial", 2: "temperature", 3: "replicate"})
               .drop(columns=["temperature"])
               )
dataIDsplit.group = dataIDsplit.group.str[1:]
dataIDsplit.vial = dataIDsplit.vial.str[-1]
dataIDsplit.replicate = dataIDsplit.replicate.str[-1]
data = data.join(dataIDsplit)

"""Now I'm going to answer each question in the lab"""
# %%
# Task 1
delta13CvialB = data.loc[data.vial == "B", "delta13C_CO2"].mean()
# %%
# Task 2
enrichmentFactors = data.groupby("Temp")["delta13C_CO2"].mean()
enrichmentFactors = delta13CvialB - enrichmentFactors
enrichmentFactors = (enrichmentFactors.reset_index()
                     .query("Temp != 'Ref'")
                     .rename(columns={"delta13C_CO2": "enrichmentFactors"})
                     )
# %%
# Task 3
enrichmentFactors["tempKelvin"] = enrichmentFactors.Temp + 273.15
enrichmentFactors["xValues"] = 1000/enrichmentFactors["tempKelvin"]
enrichmentFactors["MookEnrichmentFactors"] = (9483/enrichmentFactors.tempKelvin) - 23.89
