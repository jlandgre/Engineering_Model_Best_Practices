# .../Engineering_Model_Best_Practices/Roll_Length_Model_Tutorial/libs/tests/
#01234567890123456789012345678901234567890123456789012345678901234567890123456789
import pytest
import os, sys
import pandas as pd
import numpy as np

# Add the project folder to sys.path and import project class modules
s = os.path.join(os.path.dirname(__file__), '..', 'libs')
sys.path.insert(0, os.path.abspath(s))
from roll_model import RollLength

@pytest.fixture
def pfTestData():
    return os.path.join(os.path.dirname(__file__), "data_roll_model_tests.csv")

@pytest.fixture
def rl(pfTestData):
    # Create the CSV file with the specified data
    df = pd.DataFrame({'length': [0, 20], 'diameter': [40, 120]})
    df.to_csv(pfTestData, index=False)

    # Return an instance of RollLength with the test data
    return RollLength(file_raw=pfTestData, diam_roll=None, diam_core=None, caliper=None)

def test_init(pfTestData):
    """
    Test - Initialize RollLength with and without optional arguments
    JDL Feb 18, 2025
    """
    # Test with optional diam_core arg specified
    rl1 = RollLength(pfTestData, diam_roll=None, diam_core=50, caliper=None)
    assert rl1.file_raw == pfTestData
    assert rl1.diam_roll is None
    assert rl1.diam_core == 50
    assert rl1.caliper is None
    
    # Test without optional arguments
    rl2 = RollLength(pfTestData)
    assert rl2.file_raw == pfTestData
    assert rl2.diam_roll is None
    assert rl2.diam_core is None
    assert rl2.caliper is None

"""
=================================================================================
CaliperFromRawData Procedure
=================================================================================
"""
def test_ReadRawData(rl):
    """
    Test - Read raw data from the CSV file into the .df_raw attribute
    JDL Feb 18, 2025
    """
    rl.ReadRawData()
    assert not rl.df_raw.empty
    assert list(rl.df_raw.columns) == ['length', 'diameter']
    assert rl.df_raw.shape == (2, 2)
    assert rl.df_raw['length'].tolist() == [0, 20]
    assert rl.df_raw['diameter'].tolist() == [40, 120]

def test_AddCalculatedRawCols(rl):
    """
    Test - Add calculated columns to the .df_raw attribute
    JDL Feb 18, 2025
    """
    rl.ReadRawData()
    rl.AddCalculatedRawCols()
    
    assert 'diam_m' in rl.df_raw.columns
    assert 'diam_m^2' in rl.df_raw.columns
    assert rl.df_raw['diam_m'].tolist() == [0.04, 0.12]
    assert rl.df_raw['diam_m^2'].tolist() == [0.0016, 0.0144]

def test_FitRawData(rl):
    """
    Test - Fit a line to the df_raw data using diam_m^2 as X and length as y
    JDL Feb 18, 2025
    """
    rl.ReadRawData()
    rl.AddCalculatedRawCols()
    rl.FitRawData()
    
    x = rl.df_raw['diam_m^2'].values
    y = rl.df_raw['length'].values
    
    slope_expected = (y[1] - y[0]) / (x[1] - x[0])
    intercept_expected = y[1] - slope_expected * x[1]
    R_squared_expected = 1.0
    
    # Checks vs hand-calculated values
    assert np.isclose(rl.slope, 1562.5, atol=0.001)
    assert np.isclose(rl.intcpt, -2.5, atol=0.001)

    # Checks vs slope and intercept values calculated/set in this test 
    assert np.isclose(rl.slope, slope_expected, atol=0.001)
    assert np.isclose(rl.intcpt, intercept_expected, atol=0.001)
    assert np.isclose(rl.R_squared, R_squared_expected, atol=0.001)

def test_CalculateCaliper(rl):
    """
    Test - Calculate the caliper attribute
    JDL Feb 18, 2025
    """
    rl.ReadRawData()
    rl.AddCalculatedRawCols()
    rl.FitRawData()
    rl.CalculateCaliper()
    
    caliper_expected = round(np.pi / (4 * 1562.5) * 1000, 4)
    caliper_hand_calc = .5027
    assert np.isclose(caliper_hand_calc, caliper_expected, atol=0.0001)    
    assert np.isclose(rl.caliper, caliper_expected, atol=0.0001)