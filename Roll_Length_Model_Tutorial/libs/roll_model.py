import pandas as pd
from sklearn.linear_model import LinearRegression
import math
import matplotlib.pyplot as plt

"""
===============================================================================
RollLength Class
===============================================================================
"""
class RollLength:
    """
    Class to manage use cases from roll model
    JDL Feb 18, 2025
    """
    def __init__(self, file_raw, diam_roll=None, diam_core=None, caliper=None):
        self.file_raw = file_raw
        self.diam_roll = diam_roll
        self.diam_core = diam_core
        self.caliper = caliper

        # Internally-created attributes
        self.df_raw = pd.DataFrame()
        self.slope = None
        self.intcpt = None
        self.R_squared = None

    """
    ===========================================================================
    CaliperFromRawData Procedure
    ===========================================================================
    """
    @property
    def Caliper(self):
        """ 
        Property -- returns caliper attribute
        JDL Feb 18, 2025
        """
        self.CaliperFromRawData()
        return self.caliper

    def CaliperFromRawData(self):
        """ 
        Procedure to calculate caliper from raw data
        JDL Feb 18, 2025
        """
        self.ReadRawData()
        self.AddCalculatedRawCols()
        self.FitRawData()
        self.CalculateCaliper()

    def ReadRawData(self):
        """ 
        Read raw data from the file and store it in the df_raw attribute
        JDL Feb 18, 2025
        """
        self.df_raw = pd.read_csv(self.file_raw)

    def AddCalculatedRawCols(self):
        """ 
        Add calculated columns to the df_raw attribute
        JDL Feb 18, 2025
        """
        self.df_raw['diam_m'] = self.df_raw['diameter'] / 1000
        self.df_raw['diam_m^2'] = self.df_raw['diam_m'] ** 2

    def FitRawData(self):
        """ 
        Fit line using diam_m^2 as x and length as y
        JDL Feb 18, 2025
        """
        X = self.df_raw[['diam_m^2']]
        y = self.df_raw['length']
        model = LinearRegression().fit(X, y)

        # Set model attributes based on the fit
        self.slope = model.coef_[0]
        self.intcpt = model.intercept_
        self.R_squared = model.score(X, y)

    def CalculateCaliper(self):
        """ 
        Calculate the caliper attribute
        JDL Feb 18, 2025
        """
        caliper_m = math.pi / (4 * self.slope)
        caliper_mm = caliper_m * 1000
        self.caliper = round(caliper_mm, 4)

    """
    =========================================================================
    PlotRawAndTransformedData Procedure
    =========================================================================
    """
    def PlotRawAndTransformedData(self):
        text = 'Diameter (mm)', 'Length (m)', 'Length vs. Diameter'
        self.XYDataPlot(self.df_raw['diameter'], self.df_raw['length'], 
                        text[0],  text[1], text[2])

        text = 'Diameter Squared (m^2)', 'Length (m)', 'Length vs. Diameter Squared'
        self.XYDataPlot(self.df_raw['diam_m^2'], self.df_raw['length'], 
                        text[0],  text[1], text[2]) 


    """
    =========================================================================
    CalculateRollLength Procedure - Length calculation given caliper, diam 
    and diam_core inputs. 

    All inputs in units of mm. Length output in meters
    =========================================================================
    """
    @property
    def Length(self):
        self.CalculateLengthProcedure()
        return self.length
    
    def CalculateLengthProcedure(self):
        """
        Calculate roll length in meters
        JDL 4/27/23; modified 5/1/23
        """
        mm_m = 1000.
        numerator = math.pi * ((self.diam_roll / mm_m) ** 2 - 
                               (self.diam_core / mm_m) ** 2)
        denom = (4 * (self.caliper / mm_m))
        self.length = round(numerator / denom, 1)

    """
    =========================================================================
    Utility methods
    =========================================================================
    """
    @staticmethod
    def XYDataPlot(X, Y, x_label, y_label, plot_title):
        """
        XY Plot of raw and transformed data
        """
        plt.scatter(X, Y)
        plt.xlabel(x_label), plt.ylabel(y_label)
        plt.title(plot_title)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.show()