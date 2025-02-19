#01234567890123456789012345678901234567890123456789012345678901234567890123456789

import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

class RollLength:
    def __init__(self, file_raw, diam_roll=None, diam_core=None, caliper=None):
        """
        Initialize the RollLength class with the provided parameters
        JDL 18/2/2025
        """
        self.file_raw = file_raw
        self.diam_roll = diam_roll
        self.diam_core = diam_core
        self.caliper = caliper

        #Internal attributes
        self.df_raw = pd.DataFrame()
        self.slope = None
        self.intcpt = None
        self.R_squared = None
    """
    =================================================================================
    CaliperFromRawData Procedure
    =================================================================================
    """
    def ReadRawData(self):
        """ 
        Read raw data from the CSV file into the .df_raw attribute
        JDL Feb 18, 2025
        """
        self.df_raw = pd.read_csv(self.file_raw)

    def AddCalculatedRawCols(self):
        """ 
        Add calculated columns to the .df_raw attribute
        JDL Feb 18, 2025
        """
        self.df_raw['diam_m'] = self.df_raw['diameter'] / 1000
        self.df_raw['diam_m^2'] = self.df_raw['diam_m'] ** 2

    def FitRawData(self):
        """ 
        Fit a line with diam_m^2 as X and length as y
        JDL Feb 18, 2025
        """
        X = self.df_raw[['diam_m^2']].values
        y = self.df_raw['length'].values
        model = LinearRegression().fit(X, y)

        # Set attributes for fitted model
        self.slope = model.coef_[0]
        self.intcpt = model.intercept_
        self.R_squared = model.score(X, y)

    def CalculateCaliper(self):
        """ 
        Calculate the caliper attribute
        JDL Feb 18, 2025
        """
        caliper_m = np.pi / (4 * self.slope)
        caliper_mm = caliper_m * 1000
        self.caliper = round(caliper_mm, 4)