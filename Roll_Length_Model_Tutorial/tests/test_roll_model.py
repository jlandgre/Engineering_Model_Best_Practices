import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add the project folder to sys.path and import project class modules
s = os.path.join(os.path.dirname(__file__), '..', 'libs')
sys.path.insert(0, os.path.abspath(s))

from roll_model import RollLength

"""
===============================================================================
RollLength Class Tests
===============================================================================
"""
# Path to mockup data used in the tests
@pytest.fixture
def pfTestData(tmpdir):
    pf_test_data = os.path.join(tmpdir, "data_roll_model_tests.csv")
    df = pd.DataFrame({
        'length': [0, 20],
        'diameter': [40, 120]
    })
    df.to_csv(pf_test_data, index=False)
    return pf_test_data

# Instance of RollLength class with test data from *.csv file
@pytest.fixture
def rl(pfTestData):
    return RollLength(file_raw=pfTestData, diam_roll=None, diam_core=None, caliper=None)

def test_rl_fixture(pfTestData):
    # Check if the CSV file exists
    assert os.path.exists(pfTestData), "CSV file does not exist"

    # Load the CSV file into a DataFrame
    df = pd.read_csv(pfTestData)

    # Check if the DataFrame has two rows
    assert len(df) == 2, "DataFrame does not have two rows"

    # Check the content of the DataFrame
    assert df['length'].tolist() == [0, 20], "Length column does not match expected values"
    assert df['diameter'].tolist() == [40, 120], "Diameter column does not match expected values"

"""
Test - Initialize RollLength with required and optional arguments
JDL 18/2/2025
"""
def test_init():
    # Case where diam_core is specified as 50
    rl_with_core = RollLength(file_raw="dummy_path.csv", diam_core=50)
    assert rl_with_core.file_raw == "dummy_path.csv"
    assert rl_with_core.diam_core == 50
    assert rl_with_core.diam_roll is None
    assert rl_with_core.caliper is None
    assert rl_with_core.df_raw.empty

    # Case where optional args are not specified
    rl_without_optional = RollLength(file_raw="dummy_path.csv")
    assert rl_without_optional.file_raw == "dummy_path.csv"
    assert rl_without_optional.diam_core is None
    assert rl_without_optional.diam_roll is None
    assert rl_without_optional.caliper is None

    assert rl_without_optional.df_raw.empty

"""
===============================================================================
CaliperFromRawData Procedure Tests
===============================================================================
"""
def test_ReadRawData(rl):
    """
    Test - Read raw data from the file and store it in the df_raw attribute
    JDL 18/2/2025
    """
    rl.ReadRawData()

    # Check if the df has two rows and check col names
    assert len(rl.df_raw) == 2
    assert list(rl.df_raw.columns) == ['length', 'diameter']

    # Check the content of the DataFrame
    assert rl.df_raw['length'].tolist() == [0, 20]
    assert rl.df_raw['diameter'].tolist() == [40, 120]

def test_AddCalculatedRawCols(rl):
    """
    Test - Add calculated columns to the df_raw attribute
    JDL 18/2/2025
    """
    rl.ReadRawData()
    rl.AddCalculatedRawCols()
    
    # Check if the df has the new columns
    assert 'diam_m' in rl.df_raw.columns
    assert 'diam_m^2' in rl.df_raw.columns

    # Check the content of the new columns
    assert rl.df_raw['diam_m'].tolist() == [0.04, 0.12]
    assert rl.df_raw['diam_m^2'].tolist() == [0.0016, 0.0144]

def test_FitRawData(rl):
    """
    Test - Fit line using diam_m^2 as x and length as y
    JDL 18/2/2025
    """
    rl.ReadRawData()
    rl.AddCalculatedRawCols()
    rl.FitRawData()

    #Numpy arrays for manual calculations
    x, y = rl.df_raw['diam_m^2'].values, rl.df_raw['length'].values

    slope_expected = (y[1] - y[0]) / (x[1] - x[0])
    intercept_expected = y[1] - slope_expected * x[1]

    # Check expected calcs versus hand calculations
    assert np.isclose(slope_expected, 1562.5, atol=0.001)
    assert np.isclose(intercept_expected, -2.5, atol=0.001)

    # Check attributes from FitRawData method
    assert np.isclose(rl.slope, slope_expected, atol=0.001)
    assert np.isclose(rl.intcpt, intercept_expected, atol=0.001)
    assert np.isclose(rl.R_squared, 1.0, atol=0.001)

def test_CalculateCaliper(rl):
    """
    Test - Calculate the caliper attribute
    JDL 18/2/2025
    """
    rl.ReadRawData()
    rl.AddCalculatedRawCols()
    rl.FitRawData()
    rl.CalculateCaliper()

    # Use known slope (1562.5) and hand-calc caliper (0.5027) to check
    caliper_expected = round((np.pi / (4 * 1562.5)) * 1000, 4)
    assert np.isclose(caliper_expected, 0.5027, atol=0.0001)
    assert np.isclose(rl.caliper, caliper_expected, atol=0.0001)