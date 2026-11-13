# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 20:30:13 2026

@author: brian

This script performs calculations for lab 4, the lab where we measure in-situ
flux and delta 13C of said flux in the field at Kessler.
"""
import pandas as pd
import os
from pathlib import Path
from matplotlib import pyplot as plt
from scipy.stats import linregress
import openpyxl

cwd = Path(os.getcwd())
dataPath = cwd/"Lab 4a - Keeling_Plot_Master_Compilation-final.xlsx"
dataFile = pd.ExcelFile(dataPath)
# %%
"""Calculating flux and the isotope ratio of the flux for tree 15"""
insituFluxSheets = dataFile.sheet_names[1:-1]
chamberVolume = 4244.1
cavityVolume = 33.1
tubingVolume = 19.0
idealGasConstant = 8.314

tree15 = pd.read_excel(dataFile, insituFluxSheets[0], header=1)
tree15 = tree15.loc[1:, :]

tree15metadata = tree15.iloc[0:1, 5:]
tree15metadata["H2O"] = tree15.loc[1, "H2O"]
tree15 = tree15.iloc[0:, :5]

tree15metadata["totalVolume"] = (tree15metadata["Collar Area (cm2)"] * tree15metadata["Collar Height (cm)"]) + chamberVolume + cavityVolume + tubingVolume
tree15metadata["airTempKelvin"] = tree15metadata["Air Temperature (Celsius)"] + 273.15

"""Going to do a linear regression now to get a rate of change in CO2
concentration to get a flux. I will set a deadband of 25 s since that's what
the smart chamber does for flux. I will also apply this deadband to the
Keeling plot as well."""
tree15 = tree15.loc[tree15["Elapsed TIME"] > 25]
tree15 = tree15.astype({"Elapsed TIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
tree15regress = linregress(tree15["Elapsed TIME"], tree15["CO2"])
"""Regression for flux
slope = 0.4583162 micromole CO2 / (mol dry air * s)
R2 = 0.9978796

From this slope, let's calculate flux
"""
tree15flux = tree15metadata.totalVolume * tree15metadata["Atmospheric Pressure (kPa)"] * (1 - (tree15metadata.H2O/1e6)) * tree15regress.slope * 10/(idealGasConstant * tree15metadata.airTempKelvin * tree15metadata["Collar Area (cm2)"])

"""Now, let's work on the Keeling regression for tree 15"""
tree15["1/CO2"] = 1/tree15.CO2
tree15isotopeRegress = linregress(tree15["1/CO2"], tree15["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from tree 15, is
-28.889 permille
"""

"""Now, let's make a figure with 2 subplots, the 1st subplot being
concentration vs time, the 2nd subplot being the Keeling plot"""
tree15figure = plt.figure("Tree 15", (20, 10), 450)
tree15fluxSubplot = tree15figure.add_subplot(1, 2, 1)
tree15fluxSubplot.scatter("Elapsed TIME", "CO2", data=tree15, label="Data")
tree15minTime = tree15.loc[tree15["Elapsed TIME"] == tree15["Elapsed TIME"].min(), "Elapsed TIME"].tolist()[0]
tree15maxTime = tree15.loc[tree15["Elapsed TIME"] == tree15["Elapsed TIME"].max(), "Elapsed TIME"].tolist()[0]
tree15concentrationRegress = pd.DataFrame({"time": [tree15minTime, tree15maxTime]})
tree15concentrationRegress["CO2"] = (tree15regress.slope * tree15concentrationRegress.time) + tree15regress.intercept
tree15fluxSubplot.plot("time", "CO2", "k", data=tree15concentrationRegress, label="slope = 0.458316, R2 = 0.998, flux = 3.999 umol CO2/(m2 * s)")
tree15fluxSubplot.set_xlabel("Time (s)")
tree15fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
tree15fluxSubplot.set_title("CO2 concentration vs time")
tree15fluxSubplot.legend()
tree15fluxSubplot.grid()

tree15isotopeSubplot = tree15figure.add_subplot(1, 2, 2)
tree15isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=tree15, label="Data")

tree15minReciprocal = tree15.loc[tree15["1/CO2"] == tree15["1/CO2"].min(), "1/CO2"].tolist()[0]
tree15maxReciprocal = tree15.loc[tree15["1/CO2"] == tree15["1/CO2"].max(), "1/CO2"].tolist()[0]
tree15isotopeRegressDF = pd.DataFrame({"1/CO2": [0, tree15maxReciprocal]})
tree15isotopeRegressDF["isotopeRatio"] = (tree15isotopeRegress.slope * tree15isotopeRegressDF["1/CO2"]) + tree15isotopeRegress.intercept
tree15isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=tree15isotopeRegressDF, label="intercept = -28.889145, R2 = 0.978")
tree15isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
tree15isotopeSubplot.set_ylabel("delta 13C (permille)")
tree15isotopeSubplot.set_title("Keeling plot")
tree15isotopeSubplot.legend()
tree15isotopeSubplot.grid()

# Recording the flux and delta 13C of tree 15
fluxes = tree15flux.tolist()
isotopeRatios = [tree15isotopeRegress.intercept]

# Saving the figure for tree 15
tree15figurePath = cwd/"Output"/"Task 1"/"Tree 15.png"
if os.path.exists(tree15figurePath) is False:
    tree15figure.savefig(tree15figurePath, bbox_inches="tight")
# %%
"""Calculating flux and isotope ratio of flux for grass 15"""
grass15 = pd.read_excel(dataFile, insituFluxSheets[1], header=1)
grass15 = grass15.loc[1:, :]

grass15metadata = grass15.iloc[0:1, 5:]
grass15metadata["H2O"] = grass15.loc[1, "H2O"]
grass15 = grass15.iloc[0:, :5]

grass15metadata["totalVolume"] = (grass15metadata["Collar Area (cm2)"] * grass15metadata["Collar Height (cm)"]) + chamberVolume + cavityVolume + tubingVolume
grass15metadata["airTempKelvin"] = grass15metadata["Air Temperature (Celsius)"] + 273.15

"""Linear regression on concentration data with time for grass 15 to get a
slope that will be used to calculate flux"""
grass15 = grass15.loc[grass15["ETIME"] > 25]
grass15 = grass15.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
grass15regress = linregress(grass15["ETIME"], grass15["CO2"])

"""Regression for flux
slope = 0.276590 micromole CO2 / (mol dry air * s)
R2 = 0.998

From this slope, let's calculate flux
"""

grass15flux = grass15metadata.totalVolume * grass15metadata["Atmospheric Pressure "] * (1 - (grass15metadata.H2O/1e6)) * grass15regress.slope * 10/(idealGasConstant * grass15metadata.airTempKelvin * grass15metadata["Collar Area (cm2)"])

"""Keeling regression for grass 15"""
grass15["1/CO2"] = 1/grass15.CO2
grass15isotopeRegress = linregress(grass15["1/CO2"], grass15["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from grass 15, is
-21.935 permille
"""

"""Concentration and Keeling plots for grass 15"""
grass15figure = plt.figure("Grass 15", (20, 10), 450)
grass15fluxSubplot = grass15figure.add_subplot(1, 2, 1)
grass15fluxSubplot.scatter("ETIME", "CO2", data=grass15, label="Data")
grass15minTime = grass15.loc[grass15["ETIME"] == grass15["ETIME"].min(), "ETIME"].tolist()[0]
grass15maxTime = grass15.loc[grass15["ETIME"] == grass15["ETIME"].max(), "ETIME"].tolist()[0]
grass15concentrationRegress = pd.DataFrame({"time": [grass15minTime, grass15maxTime]})
grass15concentrationRegress["CO2"] = (grass15regress.slope * grass15concentrationRegress.time) + grass15regress.intercept
grass15fluxSubplot.plot("time", "CO2", "k", data=grass15concentrationRegress, label="slope = 0.276590, R2 = 0.998, flux = 1.887025 umol CO2/(m2 * s)")
grass15fluxSubplot.set_xlabel("Time (s)")
grass15fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
grass15fluxSubplot.set_title("CO2 concentration vs time")
grass15fluxSubplot.legend()
grass15fluxSubplot.grid()

grass15isotopeSubplot = grass15figure.add_subplot(1, 2, 2)
grass15isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=grass15, label="Data")

grass15minReciprocal = grass15.loc[grass15["1/CO2"] == grass15["1/CO2"].min(), "1/CO2"].tolist()[0]
grass15maxReciprocal = grass15.loc[grass15["1/CO2"] == grass15["1/CO2"].max(), "1/CO2"].tolist()[0]
grass15isotopeRegressDF = pd.DataFrame({"1/CO2": [0, grass15maxReciprocal]})
grass15isotopeRegressDF["isotopeRatio"] = (grass15isotopeRegress.slope * grass15isotopeRegressDF["1/CO2"]) + grass15isotopeRegress.intercept
grass15isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=grass15isotopeRegressDF, label="intercept = -21.935046, R2 = 0.920")
grass15isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
grass15isotopeSubplot.set_ylabel("delta 13C (permille)")
grass15isotopeSubplot.set_title("Keeling plot")
grass15isotopeSubplot.legend()
grass15isotopeSubplot.grid()

# Recording the flux and delta 13C of grass 15
fluxes.extend(grass15flux.tolist())
isotopeRatios.append(grass15isotopeRegress.intercept)

# Saving the figure for grass 15
grass15figurePath = cwd/"Output"/"Task 1"/"Grass 15.png"
if os.path.exists(grass15figurePath) is False:
    grass15figure.savefig(grass15figurePath, bbox_inches="tight")
# %%
"""Calculating flux and isotope ratio of flux for tree 17"""
tree17 = pd.read_excel(dataFile, insituFluxSheets[2], header=1)
tree17 = tree17.loc[1:, :]

tree17metadata = tree17.iloc[0:1, 5:]
tree17metadata["H2O"] = tree17.loc[1, "H2O"]
tree17 = tree17.iloc[0:, :5]

tree17metadata["totalVolume"] = (tree17metadata["Collar Area"] * tree17metadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
tree17metadata["airTempKelvin"] = tree17metadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for tree 17 to get a
slope that will be used to calculate flux"""
tree17 = tree17.loc[tree17["ETIME"] > 25]
tree17 = tree17.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
tree17regress = linregress(tree17["ETIME"], tree17["CO2"])

"""Regression for flux
slope = 0.409992 micromole CO2 / (mol dry air * s)
R2 = 0.998

From this slope, let's calculate flux
"""

tree17flux = tree17metadata.totalVolume * tree17metadata["Atmospheric Pressure "] * (1 - (tree17metadata.H2O/1e6)) * tree17regress.slope * 10/(idealGasConstant * tree17metadata.airTempKelvin * tree17metadata["Collar Area"])

"""Keeling regression for tree 17"""
tree17["1/CO2"] = 1/tree17.CO2
tree17isotopeRegress = linregress(tree17["1/CO2"], tree17["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from tree 17, is
-28.693 permille
"""

"""Concentration and Keeling plots for tree 17"""
tree17figure = plt.figure("Tree 17", (20, 10), 450)
tree17fluxSubplot = tree17figure.add_subplot(1, 2, 1)
tree17fluxSubplot.scatter("ETIME", "CO2", data=tree17, label="Data")
tree17minTime = tree17.loc[tree17["ETIME"] == tree17["ETIME"].min(), "ETIME"].tolist()[0]
tree17maxTime = tree17.loc[tree17["ETIME"] == tree17["ETIME"].max(), "ETIME"].tolist()[0]
tree17concentrationRegress = pd.DataFrame({"time": [tree17minTime, tree17maxTime]})
tree17concentrationRegress["CO2"] = (tree17regress.slope * tree17concentrationRegress.time) + tree17regress.intercept
tree17fluxSubplot.plot("time", "CO2", "k", data=tree17concentrationRegress, label="slope = 0.409992, R2 = 0.998, flux = 3.347 umol CO2/(m2 * s)")
tree17fluxSubplot.set_xlabel("Time (s)")
tree17fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
tree17fluxSubplot.set_title("CO2 concentration vs time")
tree17fluxSubplot.legend()
tree17fluxSubplot.grid()


tree17isotopeSubplot = tree17figure.add_subplot(1, 2, 2)
tree17isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=tree17, label="Data")

tree17maxReciprocal = tree17.loc[tree17["1/CO2"] == tree17["1/CO2"].max(), "1/CO2"].tolist()[0]
tree17isotopeRegressDF = pd.DataFrame({"1/CO2": [0, tree17maxReciprocal]})
tree17isotopeRegressDF["isotopeRatio"] = (tree17isotopeRegress.slope * tree17isotopeRegressDF["1/CO2"]) + tree17isotopeRegress.intercept
tree17isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=tree17isotopeRegressDF, label="intercept = -28.693315, R2 = 0.984")
tree17isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
tree17isotopeSubplot.set_ylabel("delta 13C (permille)")
tree17isotopeSubplot.set_title("Keeling plot")
tree17isotopeSubplot.legend()
tree17isotopeSubplot.grid()


# Saving the figure for tree 17
tree17figurePath = cwd/"Output"/"Task 1"/"Tree 17.png"
if os.path.exists(tree17figurePath) is False:
    tree17figure.savefig(tree17figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of tree 17
fluxes.extend(tree17flux.tolist())
isotopeRatios.append(tree17isotopeRegress.intercept)
# %%
"""Calculating flux and isotope ratio of flux for grass 17"""
grass17 = pd.read_excel(dataFile, insituFluxSheets[3], header=1)
grass17 = grass17.loc[1:, :]

grass17metadata = grass17.iloc[0:1, 5:]
grass17metadata["H2O"] = grass17.loc[1, "H2O"]
grass17 = grass17.iloc[0:, :5]

grass17metadata["totalVolume"] = (grass17metadata["Collar Area"] * grass17metadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
grass17metadata["airTempKelvin"] = grass17metadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for grass 17 to get a
slope that will be used to calculate flux"""
grass17 = grass17.loc[grass17["ETIME"] > 25]
grass17 = grass17.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
grass17regress = linregress(grass17["ETIME"], grass17["CO2"])

"""Regression for flux
slope = 0.281518 micromole CO2 / (mol dry air * s)
R2 = 0.9998

From this slope, let's calculate flux
"""

grass17flux = grass17metadata.totalVolume * grass17metadata["Atmospheric Pressure "] * (1 - (grass17metadata.H2O/1e6)) * grass17regress.slope * 10/(idealGasConstant * grass17metadata.airTempKelvin * grass17metadata["Collar Area"])

"""Keeling regression for grass 17"""
grass17["1/CO2"] = 1/grass17.CO2
grass17isotopeRegress = linregress(grass17["1/CO2"], grass17["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from grass 17, is
-24.372 permille
"""

"""Concentration and Keeling plots for grass 17"""
grass17figure = plt.figure("Grass 17", (20, 10), 450)
grass17fluxSubplot = grass17figure.add_subplot(1, 2, 1)
grass17fluxSubplot.scatter("ETIME", "CO2", data=grass17, label="Data")
grass17minTime = grass17.loc[grass17["ETIME"] == grass17["ETIME"].min(), "ETIME"].tolist()[0]
grass17maxTime = grass17.loc[grass17["ETIME"] == grass17["ETIME"].max(), "ETIME"].tolist()[0]
grass17concentrationRegress = pd.DataFrame({"time": [grass17minTime, grass17maxTime]})
grass17concentrationRegress["CO2"] = (grass17regress.slope * grass17concentrationRegress.time) + grass17regress.intercept
grass17fluxSubplot.plot("time", "CO2", "k", data=grass17concentrationRegress, label="slope = 0.281518, R2 = 0.9998, flux = 1.951 umol CO2/(m2 * s)")
grass17fluxSubplot.set_xlabel("Time (s)")
grass17fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
grass17fluxSubplot.set_title("CO2 concentration vs time")
grass17fluxSubplot.legend()
grass17fluxSubplot.grid()


grass17isotopeSubplot = grass17figure.add_subplot(1, 2, 2)
grass17isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=grass17, label="Data")


grass17maxReciprocal = grass17.loc[grass17["1/CO2"] == grass17["1/CO2"].max(), "1/CO2"].tolist()[0]
grass17isotopeRegressDF = pd.DataFrame({"1/CO2": [0, grass17maxReciprocal]})
grass17isotopeRegressDF["isotopeRatio"] = (grass17isotopeRegress.slope * grass17isotopeRegressDF["1/CO2"]) + grass17isotopeRegress.intercept
grass17isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=grass17isotopeRegressDF, label="intercept = -24.372193, R2 = 0.883")
grass17isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
grass17isotopeSubplot.set_ylabel("delta 13C (permille)")
grass17isotopeSubplot.set_title("Keeling plot")
grass17isotopeSubplot.legend()
grass17isotopeSubplot.grid()


# Saving the figure for grass 17
grass17figurePath = cwd/"Output"/"Task 1"/"Grass 17.png"
if os.path.exists(grass17figurePath) is False:
    grass17figure.savefig(grass17figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of grass 17
fluxes.extend(grass17flux.tolist())
isotopeRatios.append(grass17isotopeRegress.intercept)
# %%
"""Calculating flux and isotope ratio of flux for tree 16"""
tree16 = pd.read_excel(dataFile, insituFluxSheets[4], header=1)
tree16 = tree16.loc[1:, :]

tree16metadata = tree16.iloc[0:1, 5:]
tree16metadata["H2O"] = tree16.loc[1, "H2O"]
tree16 = tree16.iloc[0:, :5]

tree16metadata["totalVolume"] = (tree16metadata["Collar Area"] * tree16metadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
tree16metadata["airTempKelvin"] = tree16metadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for tree 16 to get a
slope that will be used to calculate flux"""
tree16 = tree16.loc[tree16["ETIME"] > 25]
tree16 = tree16.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
tree16regress = linregress(tree16["ETIME"], tree16["CO2"])

"""Regression for flux
slope = 0.476122 micromole CO2 / (mol dry air * s)
R2 = 0.999

From this slope, let's calculate flux
"""

tree16flux = tree16metadata.totalVolume * tree16metadata["Atmospheric Pressure "] * (1 - (tree16metadata.H2O/1e6)) * tree16regress.slope * 10/(idealGasConstant * tree16metadata.airTempKelvin * tree16metadata["Collar Area"])

"""Keeling regression for tree 16"""
tree16["1/CO2"] = 1/tree16.CO2
tree16isotopeRegress = linregress(tree16["1/CO2"], tree16["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from tree 16, is
-26.977 permille
"""

"""Concentration and Keeling plots for tree 16"""
tree16figure = plt.figure("Tree 16", (20, 10), 450)
tree16fluxSubplot = tree16figure.add_subplot(1, 2, 1)
tree16fluxSubplot.scatter("ETIME", "CO2", data=tree16, label="Data")
tree16minTime = tree16.loc[tree16["ETIME"] == tree16["ETIME"].min(), "ETIME"].tolist()[0]
tree16maxTime = tree16.loc[tree16["ETIME"] == tree16["ETIME"].max(), "ETIME"].tolist()[0]
tree16concentrationRegress = pd.DataFrame({"time": [tree16minTime, tree16maxTime]})
tree16concentrationRegress["CO2"] = (tree16regress.slope * tree16concentrationRegress.time) + tree16regress.intercept
tree16fluxSubplot.plot("time", "CO2", "k", data=tree16concentrationRegress, label="slope = 0.476, R2 = 0.999, flux = 4.194 umol CO2/(m2 * s)")
tree16fluxSubplot.set_xlabel("Time (s)")
tree16fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
tree16fluxSubplot.set_title("CO2 concentration vs time")
tree16fluxSubplot.legend()
tree16fluxSubplot.grid()


tree16isotopeSubplot = tree16figure.add_subplot(1, 2, 2)
tree16isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=tree16, label="Data")
tree16maxReciprocal = tree16.loc[tree16["1/CO2"] == tree16["1/CO2"].max(), "1/CO2"].tolist()[0]
tree16isotopeRegressDF = pd.DataFrame({"1/CO2": [0, tree16maxReciprocal]})
tree16isotopeRegressDF["isotopeRatio"] = (tree16isotopeRegress.slope * tree16isotopeRegressDF["1/CO2"]) + tree16isotopeRegress.intercept
tree16isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=tree16isotopeRegressDF, label="intercept = -26.976655, R2 = 0.980")
tree16isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
tree16isotopeSubplot.set_ylabel("delta 13C (permille)")
tree16isotopeSubplot.set_title("Keeling plot")
tree16isotopeSubplot.legend()
tree16isotopeSubplot.grid()

# Saving the figure for tree 16
tree16figurePath = cwd/"Output"/"Task 1"/"Tree 16.png"
if os.path.exists(tree16figurePath) is False:
    tree16figure.savefig(tree16figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of tree 16
fluxes.extend(tree16flux.tolist())
isotopeRatios.append(tree16isotopeRegress.intercept)
# %%
"""Calculating flux and isotope ratio of flux for grass 16"""
grass16 = pd.read_excel(dataFile, insituFluxSheets[5], header=1)
grass16 = grass16.loc[1:, :]

grass16metadata = grass16.iloc[0:1, 5:]
grass16metadata["H2O"] = grass16.loc[1, "H2O"]
grass16 = grass16.iloc[0:, :5]

grass16metadata["totalVolume"] = (grass16metadata["Collar Area"] * grass16metadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
grass16metadata["airTempKelvin"] = grass16metadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for grass 16 to get a
slope that will be used to calculate flux"""
grass16 = grass16.loc[grass16["ETIME"] > 25]
grass16 = grass16.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
grass16regress = linregress(grass16["ETIME"], grass16["CO2"])

"""Regression for flux
slope = 0.283737 micromole CO2 / (mol dry air * s)
R2 = 0.9998

From this slope, let's calculate flux
"""

grass16flux = grass16metadata.totalVolume * grass16metadata["Atmospheric Pressure "] * (1 - (grass16metadata.H2O/1e6)) * grass16regress.slope * 10/(idealGasConstant * grass16metadata.airTempKelvin * grass16metadata["Collar Area"])

"""Keeling regression for grass 16"""
grass16["1/CO2"] = 1/grass16.CO2
grass16isotopeRegress = linregress(grass16["1/CO2"], grass16["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from grass 16, is
-20.943 permille
"""

"""Concentration and Keeling plots for grass 16"""
grass16figure = plt.figure("Grass 16", (20, 10), 450)
grass16fluxSubplot = grass16figure.add_subplot(1, 2, 1)
grass16fluxSubplot.scatter("ETIME", "CO2", data=grass16, label="Data")
grass16minTime = grass16.loc[grass16["ETIME"] == grass16["ETIME"].min(), "ETIME"].tolist()[0]
grass16maxTime = grass16.loc[grass16["ETIME"] == grass16["ETIME"].max(), "ETIME"].tolist()[0]
grass16concentrationRegress = pd.DataFrame({"time": [grass16minTime, grass16maxTime]})
grass16concentrationRegress["CO2"] = (grass16regress.slope * grass16concentrationRegress.time) + grass16regress.intercept
grass16fluxSubplot.plot("time", "CO2", "k", data=grass16concentrationRegress, label="slope = 0.284, R2 = 0.9998, flux = 2.006 umol CO2/(m2 * s)")
grass16fluxSubplot.set_xlabel("Time (s)")
grass16fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
grass16fluxSubplot.set_title("CO2 concentration vs time")
grass16fluxSubplot.legend()
grass16fluxSubplot.grid()


grass16isotopeSubplot = grass16figure.add_subplot(1, 2, 2)
grass16isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=grass16, label="Data")
grass16maxReciprocal = grass16.loc[grass16["1/CO2"] == grass16["1/CO2"].max(), "1/CO2"].tolist()[0]
grass16isotopeRegressDF = pd.DataFrame({"1/CO2": [0, grass16maxReciprocal]})
grass16isotopeRegressDF["isotopeRatio"] = (grass16isotopeRegress.slope * grass16isotopeRegressDF["1/CO2"]) + grass16isotopeRegress.intercept
grass16isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=grass16isotopeRegressDF, label="intercept = -20.943024, R2 = 0.902")
grass16isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
grass16isotopeSubplot.set_ylabel("delta 13C (permille)")
grass16isotopeSubplot.set_title("Keeling plot")
grass16isotopeSubplot.legend()
grass16isotopeSubplot.grid()

# Saving the figure for grass 16
grass16figurePath = cwd/"Output"/"Task 1"/"Grass 16.png"
if os.path.exists(grass16figurePath) is False:
    grass16figure.savefig(grass16figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of grass 16
fluxes.extend(grass16flux.tolist())
isotopeRatios.append(grass16isotopeRegress.intercept)
# %%
"""Calculating flux and isotope ratio of flux for tree 11"""
tree11 = pd.read_excel(dataFile, insituFluxSheets[6], header=1)
tree11 = tree11.loc[1:, :]

tree11metadata = tree11.iloc[0:1, 5:]
tree11metadata["H2O"] = tree11.loc[1, "H2O"]
tree11 = tree11.iloc[0:, :5]

tree11metadata["totalVolume"] = (tree11metadata["Collar Area"] * tree11metadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
tree11metadata["airTempKelvin"] = tree11metadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for tree 11 to get a
slope that will be used to calculate flux"""
tree11 = tree11.loc[tree11["ETIME"] > 25]
tree11 = tree11.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
tree11regress = linregress(tree11["ETIME"], tree11["CO2"])

"""Regression for flux
slope = 0.613364 micromole CO2 / (mol dry air * s)
R2 = 0.999

From this slope, let's calculate flux
"""

tree11flux = tree11metadata.totalVolume * tree11metadata["Atmospheric Pressure "] * (1 - (tree11metadata.H2O/1e6)) * tree11regress.slope * 10/(idealGasConstant * tree11metadata.airTempKelvin * tree11metadata["Collar Area"])

"""Keeling regression for tree 11"""
tree11["1/CO2"] = 1/tree11.CO2
tree11isotopeRegress = linregress(tree11["1/CO2"], tree11["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from tree 11, is
-27.997297 permille
R2 = 0.981
"""

"""Concentration and Keeling plots for tree 11"""
tree11figure = plt.figure("Tree 11", (20, 10), 450)
tree11fluxSubplot = tree11figure.add_subplot(1, 2, 1)
tree11fluxSubplot.scatter("ETIME", "CO2", data=tree11, label="Data")
tree11minTime = tree11.loc[tree11["ETIME"] == tree11["ETIME"].min(), "ETIME"].tolist()[0]
tree11maxTime = tree11.loc[tree11["ETIME"] == tree11["ETIME"].max(), "ETIME"].tolist()[0]
tree11concentrationRegress = pd.DataFrame({"time": [tree11minTime, tree11maxTime]})
tree11concentrationRegress["CO2"] = (tree11regress.slope * tree11concentrationRegress.time) + tree11regress.intercept
tree11fluxSubplot.plot("time", "CO2", "k", data=tree11concentrationRegress, label="slope = 0.613, R2 = 0.999, flux = 5.582 umol CO2/(m2 * s)")
tree11fluxSubplot.set_xlabel("Time (s)")
tree11fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
tree11fluxSubplot.set_title("CO2 concentration vs time")
tree11fluxSubplot.legend()
tree11fluxSubplot.grid()


tree11isotopeSubplot = tree11figure.add_subplot(1, 2, 2)
tree11isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=tree11, label="Data")
tree11maxReciprocal = tree11.loc[tree11["1/CO2"] == tree11["1/CO2"].max(), "1/CO2"].tolist()[0]
tree11isotopeRegressDF = pd.DataFrame({"1/CO2": [0, tree11maxReciprocal]})
tree11isotopeRegressDF["isotopeRatio"] = (tree11isotopeRegress.slope * tree11isotopeRegressDF["1/CO2"]) + tree11isotopeRegress.intercept
tree11isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=tree11isotopeRegressDF, label="intercept = -27.997297, R2 = 0.981")
tree11isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
tree11isotopeSubplot.set_ylabel("delta 13C (permille)")
tree11isotopeSubplot.set_title("Keeling plot")
tree11isotopeSubplot.legend()
tree11isotopeSubplot.grid()

# Saving the figure for tree 11
tree11figurePath = cwd/"Output"/"Task 1"/"Tree 11.png"
if os.path.exists(tree11figurePath) is False:
    tree11figure.savefig(tree11figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of tree 11
fluxes.extend(tree11flux.tolist())
isotopeRatios.append(tree11isotopeRegress.intercept)
# %%
"""Calculating flux and isotope ratio of flux for grass 11"""
grass11 = pd.read_excel(dataFile, insituFluxSheets[7], header=1)
grass11 = grass11.loc[1:, :]

grass11metadata = grass11.iloc[0:1, 5:]
grass11metadata["H2O"] = grass11.loc[1, "H2O"]
grass11 = grass11.iloc[0:, :5]

grass11metadata["totalVolume"] = (grass11metadata["Collar Area"] * grass11metadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
grass11metadata["airTempKelvin"] = grass11metadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for grass 11 to get a
slope that will be used to calculate flux"""
grass11 = grass11.loc[grass11["ETIME"] > 25]
grass11 = grass11.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
grass11regress = linregress(grass11["ETIME"], grass11["CO2"])

"""Regression for flux
slope = 0.320062 micromole CO2 / (mol dry air * s)
R2 = 0.9996

From this slope, let's calculate flux
"""

grass11flux = grass11metadata.totalVolume * grass11metadata["Atmospheric Pressure "] * (1 - (grass11metadata.H2O/1e6)) * grass11regress.slope * 10/(idealGasConstant * grass11metadata.airTempKelvin * grass11metadata["Collar Area"])

"""Keeling regression for grass 11"""
grass11["1/CO2"] = 1/grass11.CO2
grass11isotopeRegress = linregress(grass11["1/CO2"], grass11["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from grass 11, is
-18.659409 permille
R2 = 0.861
"""

"""Concentration and Keeling plots for grass 11"""
grass11figure = plt.figure("Grass 11", (20, 10), 450)
grass11fluxSubplot = grass11figure.add_subplot(1, 2, 1)
grass11fluxSubplot.scatter("ETIME", "CO2", data=grass11, label="Data")
grass11minTime = grass11.loc[grass11["ETIME"] == grass11["ETIME"].min(), "ETIME"].tolist()[0]
grass11maxTime = grass11.loc[grass11["ETIME"] == grass11["ETIME"].max(), "ETIME"].tolist()[0]
grass11concentrationRegress = pd.DataFrame({"time": [grass11minTime, grass11maxTime]})
grass11concentrationRegress["CO2"] = (grass11regress.slope * grass11concentrationRegress.time) + grass11regress.intercept
grass11fluxSubplot.plot("time", "CO2", "k", data=grass11concentrationRegress, label="slope = 0.320, R2 = 0.9996, flux = 2.210 umol CO2/(m2 * s)")
grass11fluxSubplot.set_xlabel("Time (s)")
grass11fluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
grass11fluxSubplot.set_title("CO2 concentration vs time")
grass11fluxSubplot.legend()
grass11fluxSubplot.grid()


grass11isotopeSubplot = grass11figure.add_subplot(1, 2, 2)
grass11isotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=grass11, label="Data")
grass11maxReciprocal = grass11.loc[grass11["1/CO2"] == grass11["1/CO2"].max(), "1/CO2"].tolist()[0]
grass11isotopeRegressDF = pd.DataFrame({"1/CO2": [0, grass11maxReciprocal]})
grass11isotopeRegressDF["isotopeRatio"] = (grass11isotopeRegress.slope * grass11isotopeRegressDF["1/CO2"]) + grass11isotopeRegress.intercept
grass11isotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=grass11isotopeRegressDF, label="intercept = -18.659409, R2 = 0.861")
grass11isotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
grass11isotopeSubplot.set_ylabel("delta 13C (permille)")
grass11isotopeSubplot.set_title("Keeling plot")
grass11isotopeSubplot.legend()
grass11isotopeSubplot.grid()

# Saving the figure for grass 11
grass11figurePath = cwd/"Output"/"Task 1"/"Grass 11.png"
if os.path.exists(grass11figurePath) is False:
    grass11figure.savefig(grass11figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of grass 11
fluxes.extend(grass11flux.tolist())
isotopeRatios.append(grass11isotopeRegress.intercept)
# %%
"""Calculating flux and isotope ratio of flux for wet needles"""
wetNeedles = pd.read_excel(dataFile, insituFluxSheets[8], header=1)
wetNeedles = wetNeedles.loc[1:, :]

wetNeedlesMetadata = wetNeedles.iloc[0:1, 5:]
wetNeedlesMetadata["H2O"] = wetNeedles.loc[1, "H2O"]
wetNeedles = wetNeedles.iloc[0:, :5]

wetNeedlesMetadata["totalVolume"] = (wetNeedlesMetadata["Collar Area"] * wetNeedlesMetadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
wetNeedlesMetadata["airTempKelvin"] = wetNeedlesMetadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for wet needles to get a
slope that will be used to calculate flux"""
wetNeedles = wetNeedles.loc[wetNeedles["ETIME"] > 25]
wetNeedles = wetNeedles.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
wetNeedlesRegress = linregress(wetNeedles["ETIME"], wetNeedles["CO2"])

"""Regression for flux
slope = 0.933928 micromole CO2 / (mol dry air * s)
R2 = 0.9998

From this slope, let's calculate flux
"""

wetNeedlesFlux = wetNeedlesMetadata.totalVolume * wetNeedlesMetadata["Atmospheric Pressure "] * (1 - (wetNeedlesMetadata.H2O/1e6)) * wetNeedlesRegress.slope * 10/(idealGasConstant * wetNeedlesMetadata.airTempKelvin * wetNeedlesMetadata["Collar Area"])

"""Keeling regression for wet needles"""
wetNeedles["1/CO2"] = 1/wetNeedles.CO2
wetNeedlesIsotopeRegress = linregress(wetNeedles["1/CO2"], wetNeedles["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from wet needles, is
-29.526598 permille
R2 = 0.987
"""

"""Concentration and Keeling plots for wet needles"""
wetNeedlesFigure = plt.figure("Wet needles", (20, 10), 450)
wetNeedlesFluxSubplot = wetNeedlesFigure.add_subplot(1, 2, 1)
wetNeedlesFluxSubplot.scatter("ETIME", "CO2", data=wetNeedles, label="Data")
wetNeedlesMinTime = wetNeedles.loc[wetNeedles["ETIME"] == wetNeedles["ETIME"].min(), "ETIME"].tolist()[0]
wetNeedlesMaxTime = wetNeedles.loc[wetNeedles["ETIME"] == wetNeedles["ETIME"].max(), "ETIME"].tolist()[0]
wetNeedlesConcentrationRegress = pd.DataFrame({"time": [wetNeedlesMinTime, wetNeedlesMaxTime]})
wetNeedlesConcentrationRegress["CO2"] = (wetNeedlesRegress.slope * wetNeedlesConcentrationRegress.time) + wetNeedlesRegress.intercept
wetNeedlesFluxSubplot.plot("time", "CO2", "k", data=wetNeedlesConcentrationRegress, label="slope = 0.933928, R2 = 0.9998, flux = 7.365 umol CO2/(m2 * s)")
wetNeedlesFluxSubplot.set_xlabel("Time (s)")
wetNeedlesFluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
wetNeedlesFluxSubplot.set_title("CO2 concentration vs time")
wetNeedlesFluxSubplot.legend()
wetNeedlesFluxSubplot.grid()


wetNeedlesIsotopeSubplot = wetNeedlesFigure.add_subplot(1, 2, 2)
wetNeedlesIsotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=wetNeedles, label="Data")
wetNeedlesMaxReciprocal = wetNeedles.loc[wetNeedles["1/CO2"] == wetNeedles["1/CO2"].max(), "1/CO2"].tolist()[0]
wetNeedlesIsotopeRegressDF = pd.DataFrame({"1/CO2": [0, wetNeedlesMaxReciprocal]})
wetNeedlesIsotopeRegressDF["isotopeRatio"] = (wetNeedlesIsotopeRegress.slope * wetNeedlesIsotopeRegressDF["1/CO2"]) + wetNeedlesIsotopeRegress.intercept
wetNeedlesIsotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=wetNeedlesIsotopeRegressDF, label="intercept = -29.526598, R2 = 0.987")
wetNeedlesIsotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
wetNeedlesIsotopeSubplot.set_ylabel("delta 13C (permille)")
wetNeedlesIsotopeSubplot.set_title("Keeling plot")
wetNeedlesIsotopeSubplot.legend()
wetNeedlesIsotopeSubplot.grid()

# Saving the figure for wet needles
grass11figurePath = cwd/"Output"/"Task 1"/"Wet needles.png"
if os.path.exists(grass11figurePath) is False:
    wetNeedlesFigure.savefig(grass11figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of wet needles
fluxes.extend(wetNeedlesFlux.tolist())
isotopeRatios.append(wetNeedlesIsotopeRegress.intercept)
# %%
"""Calculating flux and isotope ratio of flux for dry needles"""
dryNeedles = pd.read_excel(dataFile, insituFluxSheets[9], header=1)
dryNeedles = dryNeedles.loc[1:, :]

dryNeedlesMetadata = dryNeedles.iloc[0:1, 5:]
dryNeedlesMetadata["H2O"] = dryNeedles.loc[1, "H2O"]
dryNeedles = dryNeedles.iloc[0:, :5]

dryNeedlesMetadata["totalVolume"] = (dryNeedlesMetadata["Collar Area"] * dryNeedlesMetadata["Collar Height"]) + chamberVolume + cavityVolume + tubingVolume
dryNeedlesMetadata["airTempKelvin"] = dryNeedlesMetadata["Air Temperature "] + 273.15

"""Linear regression on concentration data with time for dry needles to get a
slope that will be used to calculate flux"""
dryNeedles = dryNeedles.loc[dryNeedles["ETIME"] > 25]
dryNeedles = dryNeedles.astype({"ETIME": "int", "CO2": "float", "C13_DELTA_CORR_-9.0": "float"})
dryNeedlesRegress = linregress(dryNeedles["ETIME"], dryNeedles["CO2"])

"""Regression for flux
slope = 0.070497 micromole CO2 / (mol dry air * s)
R2 = 0.9996

From this slope, let's calculate flux
"""

dryNeedlesFlux = dryNeedlesMetadata.totalVolume * dryNeedlesMetadata["Atmospheric Pressure "] * (1 - (dryNeedlesMetadata.H2O/1e6)) * dryNeedlesRegress.slope * 10/(idealGasConstant * dryNeedlesMetadata.airTempKelvin * dryNeedlesMetadata["Collar Area"])

"""Keeling regression for dry needles"""
dryNeedles["1/CO2"] = 1/dryNeedles.CO2
dryNeedlesIsotopeRegress = linregress(dryNeedles["1/CO2"], dryNeedles["C13_DELTA_CORR_-9.0"])
"""The intercept, or the delta 13C of soil respiration from dry needles, is
-30.331082 permille
R2 = 0.724
"""

"""Concentration and Keeling plots for dry needles"""
dryNeedlesFigure = plt.figure("Dry needles", (20, 10), 450)
dryNeedlesFluxSubplot = dryNeedlesFigure.add_subplot(1, 2, 1)
dryNeedlesFluxSubplot.scatter("ETIME", "CO2", data=dryNeedles, label="Data")
dryNeedlesMinTime = dryNeedles.loc[dryNeedles["ETIME"] == dryNeedles["ETIME"].min(), "ETIME"].tolist()[0]
dryNeedlesMaxTime = dryNeedles.loc[dryNeedles["ETIME"] == dryNeedles["ETIME"].max(), "ETIME"].tolist()[0]
dryNeedlesConcentrationRegress = pd.DataFrame({"time": [dryNeedlesMinTime, dryNeedlesMaxTime]})
dryNeedlesConcentrationRegress["CO2"] = (dryNeedlesRegress.slope * dryNeedlesConcentrationRegress.time) + dryNeedlesRegress.intercept
dryNeedlesFluxSubplot.plot("time", "CO2", "k", data=dryNeedlesConcentrationRegress, label="slope = 0.070497, R2 = 0.9996, flux = 0.554 umol CO2/(m2 * s)")
dryNeedlesFluxSubplot.set_xlabel("Time (s)")
dryNeedlesFluxSubplot.set_ylabel("CO2 concentration in dry air (ppm)")
dryNeedlesFluxSubplot.set_title("CO2 concentration vs time")
dryNeedlesFluxSubplot.legend()
dryNeedlesFluxSubplot.grid()


dryNeedlesIsotopeSubplot = dryNeedlesFigure.add_subplot(1, 2, 2)
dryNeedlesIsotopeSubplot.scatter("1/CO2", "C13_DELTA_CORR_-9.0", data=dryNeedles, label="Data")
dryNeedlesMaxReciprocal = dryNeedles.loc[dryNeedles["1/CO2"] == dryNeedles["1/CO2"].max(), "1/CO2"].tolist()[0]
dryNeedlesIsotopeRegressDF = pd.DataFrame({"1/CO2": [0, dryNeedlesMaxReciprocal]})
dryNeedlesIsotopeRegressDF["isotopeRatio"] = (dryNeedlesIsotopeRegress.slope * dryNeedlesIsotopeRegressDF["1/CO2"]) + dryNeedlesIsotopeRegress.intercept
dryNeedlesIsotopeSubplot.plot("1/CO2", "isotopeRatio", "k", data=dryNeedlesIsotopeRegressDF, label="intercept = -30.331082, R2 = 0.724")
dryNeedlesIsotopeSubplot.set_xlabel("1/CO2 concentration in dry air (1/ppm)")
dryNeedlesIsotopeSubplot.set_ylabel("delta 13C (permille)")
dryNeedlesIsotopeSubplot.set_title("Keeling plot")
dryNeedlesIsotopeSubplot.legend()
dryNeedlesIsotopeSubplot.grid()

# Saving the figure for dry needles
grass11figurePath = cwd/"Output"/"Task 1"/"Dry needles.png"
if os.path.exists(grass11figurePath) is False:
    dryNeedlesFigure.savefig(grass11figurePath, bbox_inches="tight")

# Recording the flux and delta 13C of dry needles
fluxes.extend(dryNeedlesFlux.tolist())
isotopeRatios.append(dryNeedlesIsotopeRegress.intercept)
# %%
"""Tabulating the fluxes and isotope ratios"""
fluxAndRatioDF = pd.DataFrame({"measurement": insituFluxSheets, "flux": fluxes, "d13C": isotopeRatios})
fluxAndRatioDF["landscapeElement"] = fluxAndRatioDF.measurement.str.extract(r"^([A-Z]+)(?:\d)")
fluxAndRatioNoNeedles = fluxAndRatioDF.query("landscapeElement.notna()")

fluxSummary = (fluxAndRatioDF.groupby("landscapeElement")["flux"].agg(["mean", "count", "std"])
               .reset_index(drop=False)
               )
fluxSummary["standardError"] = fluxSummary["std"]/(fluxSummary["count"]**(1/2))

isotopeRatioSummary = (fluxAndRatioDF.groupby("landscapeElement")["d13C"].agg(["mean", "count", "std"])
                       .reset_index(drop=False)
                       )
isotopeRatioSummary["standardError"] = isotopeRatioSummary["std"]/(isotopeRatioSummary["count"]**(1/2))

"""Plotting flux and isotope ratio as bar charts."""
fluxRatioBarFigure = plt.figure("Flux and ratio bar charts", (20, 10), 450)
fluxSubplot = fluxRatioBarFigure.add_subplot(1, 2, 1)
fluxSubplot.bar(fluxSummary["landscapeElement"], fluxSummary["mean"], yerr=fluxSummary["standardError"])
fluxSubplot.set_xlabel("Landscape element")
fluxSubplot.set_ylabel("Soil CO2 efflux (umol CO2/(m2 * s))")
fluxSubplot.grid(axis="y")

isotopeRatioSubplot = fluxRatioBarFigure.add_subplot(1, 2, 2)
isotopeRatioSubplot.bar(isotopeRatioSummary["landscapeElement"], isotopeRatioSummary["mean"], yerr=isotopeRatioSummary["standardError"])
isotopeRatioSubplot.set_xlabel("Landscape element")
isotopeRatioSubplot.set_ylabel("d13C (permille)")
isotopeRatioSubplot.grid(axis="y")

# Saving the bar charts
fluxRatioBarPath = cwd/"Output"/"Task 1"/"Bar charts.png"
if os.path.exists(fluxRatioBarPath) is False:
    fluxRatioBarFigure.savefig(fluxRatioBarPath, bbox_inches="tight")

"""I'm going to export the flux and isotope ratio for each landscape element
as well

"""
fluxRatioExcelPath = cwd/"Output"/"Task 1"/"FLuxes and isotope ratios.xlsx"
if os.path.exists(fluxRatioExcelPath) is False:
    wb = openpyxl.Workbook()
    dataTab = wb.active
    dataTab.title = "Data"
    dataTab.append(fluxAndRatioDF.columns.tolist())
    fluxAndRatioList = fluxAndRatioDF.to_numpy().tolist()
    for line in fluxAndRatioList:
        dataTab.append(line)

    fluxSummaryTab = wb.create_sheet("Fluxes summary")
    fluxSummaryTab.append(fluxSummary.columns.tolist())
    fluxSummaryList = fluxSummary.to_numpy().tolist()
    for line in fluxSummaryList:
        fluxSummaryTab.append(line)

    isotopeRatioSummaryTab = wb.create_sheet("d13C summary")
    isotopeRatioSummaryTab.append(isotopeRatioSummary.columns.tolist())
    isotopeRatioSummaryList = isotopeRatioSummary.to_numpy().tolist()
    for line in isotopeRatioSummaryList:
        isotopeRatioSummaryTab.append(line)
    wb.save(fluxRatioExcelPath)
# %%
# Task 2
# Part 1. Gonna use fluxAndRatioDF again.
fluxAndRatioNoNeedles["C4endMember"] = -13.7
fluxAndRatioNoNeedles.loc[fluxAndRatioNoNeedles.landscapeElement == "TG", "C3endMember"] = -28.5
fluxAndRatioNoNeedles.loc[fluxAndRatioNoNeedles.landscapeElement == "ERCT", "C3endMember"] = -27.4
fluxAndRatioNoNeedles["FC4_Rs"] = (fluxAndRatioNoNeedles.d13C - fluxAndRatioNoNeedles.C3endMember)/(fluxAndRatioNoNeedles.C4endMember - fluxAndRatioNoNeedles.C3endMember)
fluxAndRatioNoNeedles["FC3_Rs"] = 1 - fluxAndRatioNoNeedles.FC4_Rs
fluxAndRatioNoNeedles["plotID"] = fluxAndRatioNoNeedles.measurement.str.extract(r"[A-Z]+([0-9]+)")
fluxAndRatioNoNeedles = fluxAndRatioNoNeedles.astype({"plotID": "int"})

# Part 2
fluxAndRatioNoNeedles["grasslandSurfaceLitter"] = -15.3
fluxAndRatioNoNeedles["FTG_Rs"] = (fluxAndRatioNoNeedles.d13C - fluxAndRatioNoNeedles.C3endMember)/(fluxAndRatioNoNeedles.grasslandSurfaceLitter - fluxAndRatioNoNeedles.C3endMember)

# Part 3
lab3data = pd.read_excel(dataFile, "Lab 3 Flux results")
lab3bulkSoil = (lab3data.filter(["Landscape Element", "Plot ID", "Bulk Soil FC4\u200b"])
                .drop_duplicates()
                .rename(columns={"Bulk Soil FC4\u200b": "bulkSoilFC4",
                                 "Plot ID": "plotID"})
                .query("plotID ==[11, 15, 16, 17]")
                )
lab3bulkSoil.loc[lab3bulkSoil["Landscape Element"] == "Transitional Grassland", "landscapeElement"] = "TG"
lab3bulkSoil.loc[lab3bulkSoil["Landscape Element"] == "ERC Individual Tree", "landscapeElement"] = "ERCT"
fluxAndRatioNoNeedles2 = (fluxAndRatioNoNeedles.copy()
                          .merge(lab3bulkSoil, "inner", ["landscapeElement", "plotID"])
                          .drop_duplicates()
                          )

"""I'm going to make a bar chart with standard error as error bars again"""
FC4_RsSummary = (fluxAndRatioNoNeedles2.groupby("landscapeElement")["FC4_Rs"].agg(["mean", "std", "size"])
                 .reset_index()
                 .rename(columns={"mean": "meanFC4_Rs", "std": "stdFC4_Rs"})
                 )
FC4_RsSummary["standardErrorFC4_Rs"] = FC4_RsSummary["stdFC4_Rs"]/(FC4_RsSummary["size"] ** (1/2))

bulkSoilFC4summary = (fluxAndRatioNoNeedles2.groupby("landscapeElement")["bulkSoilFC4"].agg(["mean", "std", "size"])
                      .reset_index()
                      .rename(columns={"mean": "meanBulkSoilFC4", "std": "stdBulkSoilFC4"})
                      )
bulkSoilFC4summary["standardErrorBulkSoilFC4"] = bulkSoilFC4summary["stdBulkSoilFC4"]/(bulkSoilFC4summary["size"] ** (1/2))

FC4summary = (FC4_RsSummary.merge(bulkSoilFC4summary, "inner", ["size", "landscapeElement"])
              .set_index("landscapeElement")
              .filter(["meanFC4_Rs", "meanBulkSoilFC4"])
              .rename(columns={"meanFC4_Rs": "FC4_Rs", "meanBulkSoilFC4": "Bulk Soil FC4"})
              )

FC4barFigure = plt.figure("FC4 comparison", (10, 10), 450)
FC4barSubplot = FC4barFigure.add_subplot(1, 1, 1)
FC4barSubplot.grouped_bar(FC4summary)
FC4barSubplot.legend()
FC4barSubplot.set_xlabel("Landscape element")
FC4barSubplot.set_ylabel("Fraction of C4 carbon")
FC4barSubplot.grid(axis="y")

"""Let's export the figure and the table of fluxAndRatioNoNeedles2"""
FC4barPath = cwd/"Output"/"Task 2"/"FC4 bar chart.png"
if os.path.exists(FC4barPath) is False:
    FC4barFigure.savefig(FC4barPath, bbox_inches="tight")

FC4calculationsPath = cwd/"Output"/"Task 2"/"FC4 calculations.xlsx"
if os.path.exists(FC4calculationsPath) is False:
    wb = openpyxl.Workbook()
    dataTab = wb.active
    dataTab.append(fluxAndRatioNoNeedles2.columns.tolist())
    data = fluxAndRatioNoNeedles2.to_numpy().tolist()
    for line in data:
        dataTab.append(line)
    wb.save(FC4calculationsPath)
# %%
# Task 4
"""Part 5. I already calculated the fraction of soil respiration as autotrophic
respiration. Now I'm just making a bar chart comparing between the 2 landscape
elements."""
autotrophicPath = cwd/"Autotrophic respiration fraction.xlsx"
autotrophicDF = (pd.read_excel(autotrophicPath)
                 .dropna()
                 )

autotrophicSummary = (autotrophicDF.groupby("Landscape Element")["fRa"].agg(["mean", "size", "std"])
                      .reset_index()
                      )
autotrophicSummary["standardError"] = autotrophicSummary["std"]/(autotrophicSummary["size"]**(1/2))

# Making a bar chart
autotrophicRespirationBarFigure = plt.figure("Autotrophic respiration fraction", (10, 10), 450)
autotrophicRespirationSubplot = autotrophicRespirationBarFigure.add_subplot(1, 1, 1)
autotrophicRespirationSubplot.bar(autotrophicSummary["Landscape Element"], autotrophicSummary["mean"], yerr=autotrophicSummary["standardError"])
autotrophicRespirationSubplot.set_xlabel("Landscape element")
autotrophicRespirationSubplot.set_ylabel("Fraction of respiration as autotrophic")
autotrophicRespirationSubplot.grid(axis="y")
autotrophicBarPath = cwd/"Output"/"Task 4"/"Autotrophic respiration fraction.png"
if os.path.exists(autotrophicBarPath) is False:
    autotrophicRespirationBarFigure.savefig(autotrophicBarPath, bbox_inches="tight")
