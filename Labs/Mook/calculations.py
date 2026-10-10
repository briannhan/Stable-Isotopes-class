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
from scipy.stats import linregress

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
# Formula from lab
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

# Creating the figure and subplot in matplotlib first before ploting the data
enrichmentFactorFigure = plt.figure("Enrichment factor figure", (10, 10))
enrichmentFactorSubplot = enrichmentFactorFigure.add_subplot(1, 1, 1)
enrichmentFactorSubplot.set_xlabel("1000/Temperature in Kelvin")
enrichmentFactorSubplot.set_ylabel("Enrichment factor (‰)")
enrichmentFactorSubplot.grid()

"""Task 3 also asked me to compare slopes between the data from the class and
from Mook et al 1974. Need to do some regression to get the slope for the class
data.

Since the Mook equation is epsilon = (9483/T) - 23.89 and we're plotting a
figure where the x-axis is in 1000/T, we can rearrange the Mook equation as
follows
epsilon = 9.483*(1,000/T) - 23.89
which would give the Mook relationship a slope of 9.483.

Now, to calculate the slope for the class data. I'll just do some linear
regression on the class data.
"""
classLinRegression = linregress(enrichmentFactors.xValues.tolist(), enrichmentFactors.enrichmentFactors.tolist())
classSlope = classLinRegression.slope
linRegressY = classLinRegression.slope*enrichmentFactors.xValues + classLinRegression.intercept

# Plotting the data
classData = enrichmentFactorSubplot.scatter(enrichmentFactors.xValues, enrichmentFactors.enrichmentFactors, label="Class data")
classRegress = enrichmentFactorSubplot.plot(enrichmentFactors.xValues, linRegressY, label="Regression of class data")
mookPlot = enrichmentFactorSubplot.plot(enrichmentFactors.xValues, enrichmentFactors.MookEnrichmentFactors, color="#FFC107", label="Mook et al 1974")
plt.legend()

# Saving the figure
figurePath = cwd/"Enrichment factor vs temperature.png"
if os.path.exists(figurePath) is False:
    enrichmentFactorFigure.savefig(figurePath, dpi=400, bbox_inches="tight")

# %%
# Task 5


def deltaBicarbonate(deltaGas, kelvin):
    """
    I derived an equation to calculate the isotopic composition of bicarbonate
    using the isotopic composition of CO2 and temperature in Kelvin. This
    function uses this equation to calculate the isotopic composition of
    bicarbonate

    Parameters
    ----------
    deltaGas : float
        Isotopic composition of CO2 gas.
    kelvin : float
        Temperature in Kelvin.

    Returns
    -------
    FLoat representing the isotopic composition of bicarbonate
    """
    numerator = deltaGas + 1000
    denominator = (9483/(1000*kelvin)) + 0.97611
    deltaBicarbonate = (numerator/denominator) - 1000
    return deltaBicarbonate


bicarbonate = deltaBicarbonate(-8.2, 298.15)
