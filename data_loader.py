import os
from dotenv import load_dotenv
import pandas as pd
import glob

# Load environment variables from .env file
load_dotenv()

DATA_ROOT = os.getenv('DATA_ROOT')


def get_data_file_path(pair: str, timeframe: int) -> str:
    """
    Construct the file path for the given pair and timeframe.
    """
    if DATA_ROOT is None:
        raise ValueError("DATA_ROOT is not set in the environment.")
    filename = f"{pair}_{timeframe}.csv"
    return os.path.join(DATA_ROOT, filename)


def load_ohlcvt_data(pair: str, timeframe: int) -> pd.DataFrame:
    """
    Load and parse the OHLCVT CSV file for the given pair and timeframe.
    Handles files with or without headers.
    If the requested file does not exist, tries to find other available timeframes for the pair.
    Returns a pandas DataFrame with columns:
    ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']
    Performs data validation and drops rows with missing values.
    """
    file_path = get_data_file_path(pair, timeframe)
    if not os.path.isfile(file_path):
        # Search for other files for this pair
        pattern = os.path.join(DATA_ROOT, f"{pair}_*.csv")
        matches = glob.glob(pattern)
        if matches:
            # Extract available timeframes
            available_timeframes = []
            for m in matches:
                try:
                    tf = int(os.path.splitext(os.path.basename(m))[0].split('_')[1])
                    available_timeframes.append(tf)
                except Exception:
                    continue
            available_timeframes = sorted(set(available_timeframes))
            print(f"Warning: Data file not found: {file_path}")
            print(f"Available timeframes for {pair}: {available_timeframes}")
            # Load the first available file as a fallback
            fallback_file = matches[0]
            print(f"Loading fallback file: {fallback_file}")
            file_path = fallback_file
        else:
            raise FileNotFoundError(f"Data file not found: {file_path}\nNo alternative files found for pair {pair} in {DATA_ROOT}.")

    # Check if the first line is a header or data
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
    first_values = first_line.split(',')
    has_header = not all(v.replace('.', '', 1).replace('-', '', 1).isdigit() for v in first_values)

    if has_header:
        df = pd.read_csv(file_path)
        # Rename columns if needed
        expected_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']
        if list(df.columns) != expected_cols:
            df.columns = expected_cols
    else:
        df = pd.read_csv(
            file_path,
            header=None,
            names=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']
        )

    # Validation: required columns
    expected_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']
    if not all(col in df.columns for col in expected_cols):
        raise ValueError("Missing one or more required columns in data.")

    # Drop rows with missing values
    if df.isnull().any().any():
        df = df.dropna()
        print("Warning: Dropped rows with missing values.")

    # Ensure correct types
    for col in ['open', 'high', 'low', 'close', 'volume', 'trades']:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column {col} must be numeric.")

    # Ensure timestamp is integer
    if not pd.api.types.is_integer_dtype(df['timestamp']):
        df['timestamp'] = df['timestamp'].astype(int)

    # Sort by timestamp if not already sorted
    if not df['timestamp'].is_monotonic_increasing:
        df = df.sort_values('timestamp').reset_index(drop=True)

    # Check for non-negative values
    for col in ['open', 'high', 'low', 'close', 'volume', 'trades']:
        if (df[col] < 0).any():
            raise ValueError(f"Column {col} contains negative values.")

    return df 