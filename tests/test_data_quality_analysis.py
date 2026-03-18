import pytest
import pandas as pd
import numpy as np
import os

from data_quality_analysis import prepare_data


def test_data_preparation_logic():
    test_data = {
        'station': ['ЮУАЕС', 'ЗАЕС'],
        'irg': ['10,5', np.nan],
        'index_dump': ['<0,01', '0,5']
    }
    df = pd.DataFrame(test_data)

    cleaned_df = prepare_data(df)

    assert 'ПАЕС' in cleaned_df['station'].values
    assert 'ЮУАЕС' not in cleaned_df['station'].values

    assert cleaned_df.iloc[0]['irg'] == 10.5

    assert cleaned_df.iloc[0]['index_dump'] == 0.01 - 0.001


def test_paths_integrity():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(BASE_DIR, 'data', 'raw')

    assert os.path.exists(BASE_DIR)