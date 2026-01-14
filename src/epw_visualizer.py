# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots # Import make_subplots
import plotly.colors # Import colors module
import plotly.exceptions # For catching PlotlyError specifically
import io
import datetime
import numpy as np
import calendar
import logging # For better logging

# --- Constants ---
UNIFIED_YEAR = 2000
DEFAULT_PLOT_HEIGHT = 550 # <-- Set Default Plot Height Here
DEFAULT_COLORBAR_THICKNESS = 15 # <-- Set Default Colorbar Thickness Here
DEFAULT_3D_ASPECT_X = 2.0 # <-- Set Default 3D X-axis aspect ratio

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit App Configuration ---
st.set_page_config(layout="wide")

# Add custom CSS to reduce top margin
st.markdown("""
    <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
        }
        h2 {
            margin-top: 0;
        }
        /* Ensure Streamlit buttons don't inherit link styling if embedded */
        .stButton>button {
           color: inherit;
           text-decoration: none;
        }
    </style>
    """, unsafe_allow_html=True)

# Use markdown for smaller title
st.markdown("#### EPW Data Visualizer (Scatter Plot / Heatmap / 3D Surface / Monthly Profile / Yearly Hourly Averages)")


# --- Validator's List of Recognized Named Colorscales (from Plotly internal error message) ---
VALIDATOR_NAMED_SCALES = [
    'aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance', 'blackbody',
    'bluered', 'blues', 'blugrn', 'bluyl', 'brbg', 'brwnyl', 'bugn', 'bupu',
    'burg', 'burgyl', 'cividis', 'curl', 'darkmint', 'deep', 'delta', 'dense',
    'earth', 'edge', 'electric', 'emrld', 'fall', 'geyser', 'gnbu', 'gray',
    'greens', 'greys', 'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno',
    'jet', 'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
    'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl', 'piyg',
    'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn', 'puor', 'purd',
    'purp', 'purples', 'purpor', 'rainbow', 'rdbu', 'rdgy', 'rdpu', 'rdylbu',
    'rdylgn', 'redor', 'reds', 'solar', 'spectral', 'speed', 'sunset',
    'sunsetdark', 'teal', 'tealgrn', 'tealrose', 'tempo', 'temps', 'thermal',
    'tropic', 'turbid', 'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu',
    'ylorbr', 'ylorrd'
]

# --- Helper function to resolve colorscale strings to lists if needed ---
def resolve_plotly_colorscale(scale_name_str):
    """
    Resolves a colorscale name string for use with Plotly Express and Graph Objects.
    - If the base name is in VALIDATOR_NAMED_SCALES, returns the string itself
      (e.g., "viridis", "viridis_r"), as Plotly's make_figure handles these.
    - Otherwise, attempts to convert to a list definition.
    - Handles '_r' suffix for reversal if a list definition is constructed.
    """
    if not isinstance(scale_name_str, str):
        return scale_name_str  # Already a list/tuple, pass through

    is_reversed = scale_name_str.endswith('_r')
    base_name = scale_name_str[:-2] if is_reversed else scale_name_str

    # Path 1: Base name is directly recognized by the low-level validator.
    if base_name in VALIDATOR_NAMED_SCALES:
        return scale_name_str

    # Path 2: Base name is not in VALIDATOR_NAMED_SCALES. Must get/create a list definition.
    list_definition = None
    potential_def_source = None # To store what was found before conversion

    # Attempt 2a: Try px.colors.get_colorscale(base_name).
    try:
        list_definition = px.colors.get_colorscale(base_name) # Should return [[v,c],...]
        potential_def_source = list_definition # Store it as it's already in desired format (or close)
    except (ValueError, plotly.exceptions.PlotlyError):
        # Attempt 2b: If get_colorscale fails, try direct lookups.
        # Check plotly.colors.PLOTLY_SCALES (dictionary, e.g., PLOTLY_SCALES['cool'])
        if base_name in plotly.colors.PLOTLY_SCALES:
            potential_def_source = plotly.colors.PLOTLY_SCALES[base_name]
        else:
            # Check sequential, diverging, cyclical, colorbrewer modules
            for p_module_name in ['sequential', 'diverging', 'cyclical', 'colorbrewer']:
                p_module = getattr(plotly.colors, p_module_name)
                cap_name = base_name.capitalize()
                if hasattr(p_module, cap_name):
                    potential_def_source = getattr(p_module, cap_name)
                    break
                elif hasattr(p_module, base_name): # Try lowercase too
                    potential_def_source = getattr(p_module, base_name)
                    break
            if potential_def_source is None: # Still not found
                 logging.warning(f"Colorscale '{scale_name_str}' (base: '{base_name}') completely unknown. Passing as string.")
                 return scale_name_str # Fallback

    # Process potential_def_source into a list_definition of [[v,c],...] format
    if potential_def_source:
        if isinstance(potential_def_source, (list, tuple)) and \
           all(isinstance(c, str) for c in potential_def_source):
            # It's a flat list/tuple of color strings, convert to [[v,c],...]
            num_colors = len(potential_def_source)
            if num_colors > 0:
                list_definition = [
                    [i / (num_colors - 1 if num_colors > 1 else 1), str(potential_def_source[i])]
                    for i in range(num_colors)
                ]
            else: # Empty list/tuple of colors
                list_definition = []
        elif isinstance(potential_def_source, (list, tuple)) and \
             all(isinstance(item, (list, tuple)) and len(item) == 2 for item in potential_def_source):
            # It's already in [[v,c],...] or ((v,c),...) format
            list_definition = [list(item) for item in potential_def_source] # Ensure list of lists
        else:
            logging.warning(f"Colorscale '{scale_name_str}' (base: '{base_name}') found but in unexpected format: {type(potential_def_source)}. Passing as string.")
            return scale_name_str


    if list_definition is None or not list_definition: # If conversion failed or resulted in empty
        logging.warning(f"Colorscale '{scale_name_str}' (base: '{base_name}') could not be resolved to a valid list definition. Passing as string.")
        return scale_name_str

    # Validate final structure: should be list of [numeric, string] pairs
    if not (isinstance(list_definition, list) and
            all(isinstance(item, list) and len(item) == 2 and \
                isinstance(item[0], (int, float)) and isinstance(item[1], str)
                for item in list_definition)):
        logging.warning(f"Processed colorscale '{scale_name_str}' has unexpected final structure: {list_definition}. Passing original string.")
        return scale_name_str

    if is_reversed:
        reversed_def = []
        num_items = len(list_definition)
        for i in range(num_items):
            original_anchor = list_definition[i][0]
            color_from_opposite_end = list_definition[num_items - 1 - i][1]
            reversed_def.append([original_anchor, color_from_opposite_end])
        return reversed_def
    else:
        return list_definition


# --- Revised Function to load EPW data using Pandas with Caching and Status Return ---
@st.cache_data # Cache the result based on the input bytes
def load_epw_data_flexible_cached(uploaded_file_content_bytes):
    """
    Reads EPW data robustly using pandas.read_csv, handling variable column counts.
    Maps data columns according to the EPW standard. Returns data, metadata, and status messages.

    Args:
        uploaded_file_content_bytes (bytes): The raw byte content of the EPW file.

    Returns:
        tuple: (pd.DataFrame or None, dict, list) containing:
               - DataFrame with parsed EPW data (index set to DatetimeIndex).
               - Dictionary with parsed metadata.
               - List of status messages (tuples of level, message).
    """
    epw_data = None
    status_messages = []
    metadata = {
        'city': 'Unknown', 'state-province': 'N/A', 'country': 'N/A', 'data_type': 'N/A',
        'WMO': 'N/A', 'latitude': None, 'longitude': None, 'TZ': None, 'altitude': None, 'year': None
    }

    try:
        epw_file = io.BytesIO(uploaded_file_content_bytes)

        # Parse metadata (LOCATION line) more robustly
        try:
            epw_file.seek(0)
            header_lines = [epw_file.readline().decode(errors='ignore').strip() for _ in range(8)] # Read first 8 lines
            if header_lines and header_lines[0].startswith("LOCATION"):
                parts = header_lines[0].split(',')
                if len(parts) >= 10:
                    metadata['city'] = parts[1].strip() if len(parts) > 1 else 'Unknown'
                    metadata['state-province'] = parts[2].strip() if len(parts) > 2 else 'N/A'
                    metadata['country'] = parts[3].strip() if len(parts) > 3 else 'N/A'
                    metadata['data_type'] = parts[4].strip() if len(parts) > 4 else 'N/A'
                    metadata['WMO'] = parts[5].strip() if len(parts) > 5 else 'N/A'
                    try:
                        metadata['latitude'] = float(parts[6]) if len(parts) > 6 and parts[6] else None
                    except (ValueError, TypeError):
                        status_messages.append(('warning', f"Could not parse Latitude: '{parts[6]}'"))
                    try:
                        metadata['longitude'] = float(parts[7]) if len(parts) > 7 and parts[7] else None
                    except (ValueError, TypeError):
                         status_messages.append(('warning', f"Could not parse Longitude: '{parts[7]}'"))
                    try:
                        # Time Zone (hours relative to GMT, West negative)
                        metadata['TZ'] = float(parts[8]) if len(parts) > 8 and parts[8] else None
                    except (ValueError, TypeError):
                         status_messages.append(('warning', f"Could not parse Time Zone (TZ): '{parts[8]}'"))
                    try:
                        metadata['altitude'] = float(parts[9]) if len(parts) > 9 and parts[9] else None
                    except (ValueError, TypeError):
                         status_messages.append(('warning', f"Could not parse Altitude: '{parts[9]}'"))
                else:
                     status_messages.append(('warning', "LOCATION line has fewer than 10 fields."))
            else:
                status_messages.append(('warning', "Could not find LOCATION line in EPW header."))

        except Exception as meta_err:
            status_messages.append(('warning', f"Error parsing EPW metadata header: {meta_err}"))
            logging.warning(f"Metadata parsing error: {meta_err}", exc_info=True)


        # --- Parse data ---
        epw_file.seek(0)
        # Define column names for the raw EPW file
        raw_col_names = [f'col_{i}' for i in range(100)]  # Assume max 100 columns

        # Read the raw data
        raw_epw_data = pd.read_csv(epw_file, skiprows=8, header=None, names=raw_col_names, low_memory=False)

        # --- Check minimum expected columns ---
        min_required_raw_cols = 23 # Standard EPW has 35 fields, but some might be less. Day/hour is col 22 (0-indexed).
        if raw_epw_data.shape[1] < min_required_raw_cols:
             status_messages.append(('warning', f"EPW data has only {raw_epw_data.shape[1]} columns, expected at least {min_required_raw_cols}. Some data may be missing."))
             if raw_epw_data.shape[1] < 5: # year, month, day, hour, minute
                  status_messages.append(('error', "Core time columns (0-4) missing. Cannot proceed."))
                  return None, metadata, status_messages

        epw_data = pd.DataFrame()

        # Helper function to safely get numeric column
        def get_numeric_col(df, raw_col_name, target_col_name, epw_col_num):
            try:
                if raw_col_name in df.columns:
                    numeric_series = pd.to_numeric(df[raw_col_name], errors='coerce')
                    if numeric_series.isnull().all():
                         if epw_col_num <= 34: # Only log for standard EPW fields
                            status_messages.append(('info', f"Column '{target_col_name}' (EPW Col {epw_col_num}) contains no valid numeric data."))
                         return numeric_series # Return all-NaN series
                    return numeric_series
                else:
                    if epw_col_num <= 34: # Only log for standard EPW fields
                         status_messages.append(('warning', f"Raw column '{raw_col_name}' (for {target_col_name}, EPW Col {epw_col_num}) not found."))
                    return pd.Series(np.nan, index=df.index) # Return NaN series of correct length
            except Exception as e:
                 status_messages.append(('error', f"Error processing column '{target_col_name}' (EPW Col {epw_col_num}): {e}"))
                 logging.error(f"Error processing {target_col_name}: {e}", exc_info=True)
                 return pd.Series(np.nan, index=df.index)

        # Map time columns (essential)
        epw_data['year'] = get_numeric_col(raw_epw_data, 'col_0', 'year', 1)
        epw_data['month'] = get_numeric_col(raw_epw_data, 'col_1', 'month', 2)
        epw_data['day'] = get_numeric_col(raw_epw_data, 'col_2', 'day', 3)
        epw_data['hour'] = get_numeric_col(raw_epw_data, 'col_3', 'hour', 4)
        epw_data['minute'] = get_numeric_col(raw_epw_data, 'col_4', 'minute', 5)

        # Map the data columns according to the standard EPW format
        epw_data['temp_air'] = get_numeric_col(raw_epw_data, 'col_6', 'temp_air', 7)        # Dry Bulb [C]
        epw_data['temp_dew'] = get_numeric_col(raw_epw_data, 'col_7', 'temp_dew', 8)        # Dew Point [C]
        epw_data['rh'] = get_numeric_col(raw_epw_data, 'col_8', 'rh', 9)                    # Rel Hum [%]
        epw_data['atmospheric_pressure'] = get_numeric_col(raw_epw_data, 'col_9', 'atmospheric_pressure', 10) # Pressure [Pa]
        epw_data['horizontal_infrared_radiation'] = get_numeric_col(raw_epw_data, 'col_12', 'horizontal_infrared_radiation', 13) # Horiz IR [Wh/m2]
        epw_data['ghi'] = get_numeric_col(raw_epw_data, 'col_13', 'ghi', 14)               # Glob Hor Rad [Wh/m2]
        epw_data['dni'] = get_numeric_col(raw_epw_data, 'col_14', 'dni', 15)               # Dir Norm Rad [Wh/m2]
        epw_data['dhi'] = get_numeric_col(raw_epw_data, 'col_15', 'dhi', 16)               # Diff Hor Rad [Wh/m2]
        epw_data['global_horizontal_illuminance'] = get_numeric_col(raw_epw_data, 'col_16', 'global_horizontal_illuminance', 17) # Glob Hor Illum [lux]
        epw_data['direct_normal_illuminance'] = get_numeric_col(raw_epw_data, 'col_17', 'direct_normal_illuminance', 18) # Dir Norm Illum [lux]
        epw_data['diffuse_horizontal_illuminance'] = get_numeric_col(raw_epw_data, 'col_18', 'diffuse_horizontal_illuminance', 19) # Diff Hor Illum [lux]
        epw_data['wind_direction'] = get_numeric_col(raw_epw_data, 'col_20', 'wind_direction', 21) # Wind Dir [deg]
        epw_data['wind_speed'] = get_numeric_col(raw_epw_data, 'col_21', 'wind_speed', 22)    # Wind Speed [m/s]
        epw_data['total_sky_cover'] = get_numeric_col(raw_epw_data, 'col_22', 'total_sky_cover', 23) # Total Sky Cover [tenths]

        initial_rows = len(epw_data)
        epw_data.dropna(subset=['year', 'month', 'day', 'hour', 'minute'], inplace=True)
        dropped_rows = initial_rows - len(epw_data)
        if dropped_rows > 0:
            status_messages.append(('info', f"Removed {dropped_rows} rows with missing time information."))

        if epw_data.empty:
             status_messages.append(('error', "No valid data rows remaining after cleaning time information."))
             return None, metadata, status_messages

        try:
            for t_col in ['year', 'month', 'day', 'hour', 'minute']:
                epw_data[t_col] = epw_data[t_col].astype(int)
        except ValueError as e:
             status_messages.append(('error', f"Could not convert time columns to integers: {e}. Check data validity."))
             return None, metadata, status_messages


        if 'year' in epw_data.columns and not epw_data.empty:
             metadata['year'] = int(epw_data['year'].iloc[0]) if metadata.get('year') is None else metadata.get('year')
        else:
            metadata['year'] = metadata.get('year') or datetime.datetime.now().year


        # EPW convention: hour in [1..24], minute usually 0 or 60
        epw_data['hour'] = epw_data['hour'] - 1 # Initial shift to 0-23 range
        hour_increment = epw_data['minute'] // 60
        epw_data['hour'] = (epw_data['hour'] + hour_increment) # Add hour if minute was 60
        epw_data['minute'] = epw_data['minute'] % 60 # Reset minute to 0 if it was 60
        day_increment = epw_data['hour'] // 24
        epw_data['hour'] = epw_data['hour'] % 24

        pd.options.mode.chained_assignment = None
        try:
            # Create a temporary date series for incrementing day/month/year
            epw_data['temp_date'] = pd.to_datetime(epw_data[['year', 'month', 'day']], errors='coerce')
            
            # Identify rows where day_increment occurred and temp_date is valid
            valid_increment_mask = (day_increment > 0) & epw_data['temp_date'].notna()
            
            if valid_increment_mask.any():
                # Increment the date for these rows
                epw_data.loc[valid_increment_mask, 'temp_date'] = epw_data.loc[valid_increment_mask, 'temp_date'] + pd.to_timedelta(day_increment[valid_increment_mask], unit='D')
                
                # Update year, month, day from the incremented temp_date
                epw_data.loc[valid_increment_mask, 'year'] = epw_data.loc[valid_increment_mask, 'temp_date'].dt.year
                epw_data.loc[valid_increment_mask, 'month'] = epw_data.loc[valid_increment_mask, 'temp_date'].dt.month
                epw_data.loc[valid_increment_mask, 'day'] = epw_data.loc[valid_increment_mask, 'temp_date'].dt.day
            
            epw_data.drop(columns=['temp_date'], inplace=True, errors='ignore') # errors='ignore' in case it wasn't created
        except Exception as date_inc_err:
             status_messages.append(('warning', f"Could not handle date increment due to minute=60/hour=24: {date_inc_err}"))
        finally:
             pd.options.mode.chained_assignment = 'warn'


        # Create DateTimeIndex
        try:
            for t_col in ['year', 'month', 'day', 'hour', 'minute']:
                 # Check if column exists before casting
                 if t_col in epw_data.columns:
                      epw_data[t_col] = epw_data[t_col].astype(int)
            datetime_series = pd.to_datetime(epw_data[['year', 'month', 'day', 'hour', 'minute']], errors='coerce')
        except ValueError as e:
            status_messages.append(('error', f"Error creating datetime objects: {e}. Check date/time columns for invalid entries."))
            return None, metadata, status_messages

        valid_dt_mask = datetime_series.notna()
        original_len = len(epw_data)
        epw_data = epw_data[valid_dt_mask]
        datetime_series = datetime_series[valid_dt_mask]
        if len(epw_data) < original_len:
            status_messages.append(('info', f"Removed {original_len - len(epw_data)} rows with invalid date/time combinations."))

        if epw_data.empty:
            status_messages.append(('error', "No valid date/time rows found after validation."))
            return None, metadata, status_messages

        dt_index_obj = pd.DatetimeIndex(datetime_series)

        # --- Timezone handling modification: Treat EPW as naive Local Standard Time (LST) ---
        dt_index = dt_index_obj # Already naive as per pd.to_datetime default
        status_messages.append(('info', "Timezone from EPW header ignored. Displaying times as naive local standard time."))
        # --- End Timezone handling modification ---


        # UNIFY YEAR (already naive)
        dt_index_unified = dt_index.map(lambda d: d.replace(year=UNIFIED_YEAR) if pd.notnull(d) else pd.NaT)
        status_messages.append(('info', f"Unified all data points to year {UNIFIED_YEAR}."))

        epw_data.index = dt_index_unified
        if not isinstance(epw_data.index, pd.DatetimeIndex): # Should always be true after assignment
            status_messages.append(('error', "CRITICAL: Failed DatetimeIndex assignment after year unification."))
            logging.error("Failed DatetimeIndex assignment after year unification.")
            return None, metadata, status_messages

        status_messages.append(('success', f"Successfully parsed EPW data. Shape: {epw_data.shape}"))
        return epw_data, metadata, status_messages

    except pd.errors.EmptyDataError:
        status_messages.append(('error', "EPW file appears to have no data rows after the header."))
        logging.error("EmptyDataError during EPW parsing.")
        return None, metadata, status_messages
    except KeyError as ke:
        status_messages.append(('error', f"Missing expected raw column key: {ke}. Check EPW format."))
        logging.error(f"KeyError during EPW parsing: {ke}", exc_info=True)
        return None, metadata, status_messages
    except MemoryError:
         status_messages.append(('error', "Memory Error: The EPW file might be too large to process."))
         logging.error("MemoryError during EPW parsing.")
         return None, metadata, status_messages
    except Exception as data_err:
        status_messages.append(('error', f"Fatal error reading EPW data: {data_err}"))
        logging.error(f"Fatal EPW parsing error: {data_err}", exc_info=True)
        if "IndexError" in str(data_err) or "Length mismatch" in str(data_err): # Common pandas errors
            status_messages.append(('warning', "Possible issue with unexpected column structure/count in data section."))
        return None, metadata, status_messages


# --- Define Desired Columns and Categories ---
desired_columns_map = {
    'Dry Bulb Temperature': 'temp_air', 'Dew Point Temperature': 'temp_dew', 'Relative Humidity': 'rh',
    'Wind Speed': 'wind_speed', 'Wind Direction': 'wind_direction',
    'Direct Normal Radiation': 'dni', 'Diffuse Horizontal Radiation': 'dhi', 'Global Horizontal Radiation': 'ghi',
    'Horizontal Infrared Radiation': 'horizontal_infrared_radiation',
    'Direct Normal Illuminance': 'direct_normal_illuminance', 'Diffuse Horizontal Illuminance': 'diffuse_horizontal_illuminance',
    'Global Horizontal Illuminance': 'global_horizontal_illuminance',
    'Total Sky Cover': 'total_sky_cover', 'Barometric Pressure': 'atmospheric_pressure',
}
data_columns_to_plot = list(desired_columns_map.values())
humidity_cols = ['rh']
radiation_cols = ['dni', 'dhi', 'ghi', 'horizontal_infrared_radiation'] # Exclude illuminance for now
illuminance_cols = ['direct_normal_illuminance', 'diffuse_horizontal_illuminance', 'global_horizontal_illuminance']


# --- Default Color Scales (Lowercase) ---
DEFAULT_SCALE = 'viridis'
TEMP_SCALE = 'rdylbu_r'
HUMIDITY_SCALE = 'ylgnbu_r'
RADIATION_SCALE = 'inferno'
WIND_SPEED_SCALE = 'blues'
WIND_DIR_SCALE = 'hsv'
PRESSURE_SCALE = 'plasma'
ILLUMINANCE_SCALE = 'ylorrd'
SKY_COVER_SCALE = 'greys'

# Function to get the default scale for a given column (returns lowercase)
def get_default_colorscale(column_name):
    if column_name in ['temp_air', 'temp_dew']:
        return TEMP_SCALE
    elif column_name in humidity_cols:
        return HUMIDITY_SCALE
    elif column_name in radiation_cols: # Check radiation first
        return RADIATION_SCALE
    elif column_name in illuminance_cols: # Then illuminance
         return ILLUMINANCE_SCALE
    elif column_name == 'wind_speed':
         return WIND_SPEED_SCALE
    elif column_name == 'wind_direction':
        return WIND_DIR_SCALE
    elif column_name == 'atmospheric_pressure':
        return PRESSURE_SCALE
    elif column_name == 'total_sky_cover':
         return SKY_COVER_SCALE
    else:
        return DEFAULT_SCALE

# --- Curated List of Recommended Color Scales ---
# (Using Plotly's lowercase names)
RECOMMENDED_COLORSCALES = [
    # Sequential (Good for magnitude: temperature, radiation, humidity, wind speed)
    'viridis', 'plasma', 'inferno', 'magma', 'cividis', # Perceptually uniform
    'ylgnbu', 'ylgnbu_r', 'blues', 'blues_r', 'greens', 'reds', # Single Hue
    'ylorrd', 'ylorrd_r', 'orrd', 'pubu', 'purd', 'rdpu', # Multi Hue
    'hot', 'hot_r', 'cool', 'cool_r', 'deep', 'dense', 'ice', 'greys', 'greys_r', # Misc Sequential (Added cool, cool_r)

    # Diverging (Good for differences from a midpoint, e.g., temperature deviation)
    'rdylbu', 'rdylbu_r', # Red-Yellow-Blue (Good for temp)
    'spectral', 'spectral_r',
    'coolwarm', 'bwr', 'bwr_r', # Blue-White-Red (Added coolwarm, bwr, bwr_r)
    'plotly3', # (Less common for weather)

    # Cyclical (Good for cyclical data like wind direction)
    'hsv', 'hsv_r', 'twilight', 'phase', 'mrybm', 'icefire'
]
# Ensure default scales are in the list (handle _r suffix)
for scale in [DEFAULT_SCALE, TEMP_SCALE, HUMIDITY_SCALE, RADIATION_SCALE, WIND_SPEED_SCALE, WIND_DIR_SCALE, PRESSURE_SCALE, ILLUMINANCE_SCALE, SKY_COVER_SCALE]:
     if scale not in RECOMMENDED_COLORSCALES:
         RECOMMENDED_COLORSCALES.append(scale)
     # Also add the non-reversed version if the default is reversed, and vice-versa, if not already present
     if scale.endswith('_r'):
          base_scale = scale[:-2]
          if base_scale not in RECOMMENDED_COLORSCALES:
               RECOMMENDED_COLORSCALES.append(base_scale)
     elif not scale.endswith('_r'): # Check elif to avoid adding _r_r
          reversed_scale = f"{scale}_r"
          if reversed_scale not in RECOMMENDED_COLORSCALES:
               RECOMMENDED_COLORSCALES.append(reversed_scale)

# Sort the final list for the dropdown
RECOMMENDED_COLORSCALES = sorted(list(set(RECOMMENDED_COLORSCALES)))


# --- Function to create 3D surface plot ---
# Modified to accept aspect_x/y arguments and DST flag
def create_3d_surface_plot(df, column, start_datetime_naive, end_datetime_naive, y_min, y_max,
                          bg_color, font_color, font_size, transparent_bg, colorscale, # colorscale here is ALREADY RESOLVED
                          plot_width, plot_height, colorbar_len=0.8, colorbar_thickness=15,
                          aspect_x=2.0, aspect_y=1.0, # <-- Added aspect_y
                          apply_dst_approx=False, # Added DST flag
                          title=None, custom_title=""):
    """Creates a 3D surface plot with month names on X-axis and controllable aspect ratio."""
    # Treat input df index as LST (should be naive after loader changes)
    df_to_plot = df

    try:
        # Ensure index is DatetimeIndex before comparison
        if not isinstance(df_to_plot.index, pd.DatetimeIndex):
            st.error("3D Plot: Input DataFrame index is not DatetimeIndex.")
            return None, None
        mask_date = (df_to_plot.index >= start_datetime_naive) & (df_to_plot.index <= end_datetime_naive)
        # Keep all columns needed for pivot initially
        filtered_df_date = df_to_plot.loc[mask_date].copy()
    except Exception as filter_err_3d:
        st.error(f"Error filtering data by date for 3D plot: {filter_err_3d}")
        return None, None

    if filtered_df_date.empty: # Check after initial date filter
        st.warning("No data available for the selected date range for 3D plot.")
        return None, None

    # Ensure index is DatetimeIndex before accessing .hour
    if not isinstance(filtered_df_date.index, pd.DatetimeIndex):
        st.error("3D Plot: Filtered DataFrame index is not DatetimeIndex before hour extraction.")
        return None, None
        
    start_hour = start_datetime_naive.time().hour
    end_hour = end_datetime_naive.time().hour # Selected end hour (e.g. 23 for 23:00-23:59)
    
    filtered_df_date['hour_of_day'] = filtered_df_date.index.hour

    # --- Apply HOUR Filtering (based on LST selection) ---
    if start_hour <= end_hour:
        hour_mask = (filtered_df_date['hour_of_day'] >= start_hour) & (filtered_df_date['hour_of_day'] <= end_hour)
    else: # Wraps around midnight (e.g., 22:00 to 02:00)
        hour_mask = (filtered_df_date['hour_of_day'] >= start_hour) | (filtered_df_date['hour_of_day'] <= end_hour)
    filtered_df_hour = filtered_df_date[hour_mask]
    # --- End HOUR Filtering ---


    if filtered_df_hour.empty:
        st.warning("No data available for the selected date AND hour range for 3D plot.")
        return None, None

    # --- DST Adjustment for Plotting Hour ---
    if apply_dst_approx:
        DST_START_MONTH = 4
        DST_END_MONTH = 10
        # Ensure index is DatetimeIndex before accessing .month
        if isinstance(filtered_df_hour.index, pd.DatetimeIndex):
            dst_mask = (filtered_df_hour.index.month >= DST_START_MONTH) & (filtered_df_hour.index.month <= DST_END_MONTH)
            filtered_df_hour['hour_for_pivot'] = filtered_df_hour['hour_of_day']
            # Use .loc for assignment to avoid SettingWithCopyWarning
            filtered_df_hour.loc[dst_mask, 'hour_for_pivot'] = (filtered_df_hour.loc[dst_mask, 'hour_of_day'] + 1) % 24
        else: # Should not happen if data loading is correct
            # If index isn't DatetimeIndex, can't apply DST based on month. Log warning and proceed without shift.
            logging.warning("3D Plot DST: Index not DatetimeIndex, cannot apply DST shift.")
            # dst_mask = pd.Series(False, index=filtered_df_hour.index) # No DST adjustment
            filtered_df_hour['hour_for_pivot'] = filtered_df_hour['hour_of_day']

        hour_col_for_pivot = 'hour_for_pivot'
        y_axis_title = "Approx. Clock Hour" # Define title here
    else:
        filtered_df_hour['hour_for_pivot'] = filtered_df_hour['hour_of_day'] # No shift
        hour_col_for_pivot = 'hour_for_pivot' # Use the same column name
        y_axis_title = "Hour of Day (LST)" # Define title here
    # --- End DST Adjustment ---

    # Need day_of_year after filtering
    filtered_df_final = filtered_df_hour.copy() # Work with the potentially adjusted df
    if isinstance(filtered_df_final.index, pd.DatetimeIndex):
        filtered_df_final['day_of_year'] = filtered_df_final.index.dayofyear
    else: # Should not happen
        st.error("3D Plot: Index is not DatetimeIndex before day_of_year calculation.")
        return None, None


    if column not in filtered_df_final.columns:
         st.error(f"Selected column '{column}' not found in data for 3D plot pivot.")
         return None, None

    filtered_df_final.dropna(subset=[column], inplace=True)
    if filtered_df_final.empty:
         st.warning(f"No non-NaN data for '{column}' in selected range for 3D plot.")
         return None, None


    try:
        pivot_data = filtered_df_final.pivot_table(
            values=column,
            index=hour_col_for_pivot, # Use the (potentially shifted) hour for pivot index
            columns='day_of_year',
            aggfunc='mean'
        ).fillna(0) # Fill missing combinations (e.g. night hours with no radiation)
    except Exception as e:
        st.error(f"Could not create pivot table for 3D plot: {e}")
        logging.error(f"Pivot table error (3D): {e}", exc_info=True)
        return None, None

    if pivot_data.empty:
        st.error("Pivot table for 3D plot is empty after filtering and cleaning.")
        return None, None

    # --- Calculate Month Ticks ---
    month_tick_vals = []
    month_tick_text = []
    if not pivot_data.columns.empty:
        try:
            available_days = sorted(pivot_data.columns.astype(int)) # Ensure days are integers
            first_days_of_month = {}
            for day_of_yr_val in available_days:
                 # Ensure day_of_yr_val is within valid range (1-366)
                 if not (1 <= day_of_yr_val <= 366):
                     continue
                 is_leap = calendar.isleap(UNIFIED_YEAR)
                 if day_of_yr_val == 366 and not is_leap: continue # Skip day 366 in non-leap year

                 try:
                      # Create date object assuming UNIFIED_YEAR for month abbr.
                      date_obj = datetime.datetime(UNIFIED_YEAR, 1, 1) + datetime.timedelta(days=day_of_yr_val - 1)
                      month = date_obj.month
                      if month not in first_days_of_month: first_days_of_month[month] = day_of_yr_val
                 except ValueError: continue # Handles cases like day 366 in non-leap year implicitly by timedelta
            month_tick_vals = sorted(first_days_of_month.values())
            month_tick_text = [calendar.month_abbr[m] for m in sorted(first_days_of_month.keys())]
        except Exception as tick_err:
            st.warning(f"Could not generate month ticks for 3D plot: {tick_err}")
            month_tick_vals = [] # Reset on error
            month_tick_text = []
    # --- End Calculate Month Ticks ---


    plot_title_text = custom_title if custom_title else f'3D Surface Plot: {title if title else column}'

    fig = go.Figure(data=[go.Surface(
        z=pivot_data.values, x=pivot_data.columns, y=pivot_data.index,
        colorscale=colorscale, # This is the pre-resolved colorscale
        cmin=y_min, cmax=y_max,
        colorbar=dict(
            title=dict(text=title if title else column, font=dict(color=font_color, size=font_size)),
            tickfont=dict(color=font_color, size=font_size),
            len=colorbar_len,
            thickness=colorbar_thickness # Use argument value
        )
    )])

    scene_xaxis_config = dict(
            title='Month', # Default title, overridden by ticktext if available
            color=font_color,
            backgroundcolor=bg_color
        )
    if month_tick_vals and month_tick_text:
        scene_xaxis_config['tickmode'] = 'array'
        scene_xaxis_config['tickvals'] = month_tick_vals
        scene_xaxis_config['ticktext'] = month_tick_text
    else: # Fallback if month ticks could not be generated
         scene_xaxis_config['title'] = 'Day of Year'

    # --- UPDATE LAYOUT ---
    fig.update_layout(
        title=dict(text=plot_title_text, font=dict(color=font_color, size=font_size+4)),
        scene=dict(
            xaxis_title=None, # Title set via scene_xaxis_config['title'] or implied by ticktext
            yaxis_title=y_axis_title, # Use the defined y_axis_title
            zaxis_title=title if title else column,
            xaxis=scene_xaxis_config,
            yaxis=dict(color=font_color, backgroundcolor=bg_color),
            zaxis=dict(color=font_color, backgroundcolor=bg_color, range=[y_min, y_max]),
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1)), # Default camera view
            aspectmode='manual', # Crucial for aspectratio to take effect
            aspectratio=dict(x=aspect_x, y=aspect_y, z=1) # Use argument values
        ),
        font=dict(family="Arial, sans-serif", size=font_size, color=font_color),
        paper_bgcolor='rgba(0,0,0,0)' if transparent_bg else bg_color,
        plot_bgcolor='rgba(0,0,0,0)' if transparent_bg else bg_color, # Often same as paper for 3D
        margin=dict(l=65, r=50, b=65, t=90), width=plot_width, height=plot_height
    )
    # --- END UPDATE LAYOUT ---

    return fig, pivot_data

# --- Sidebar: File Upload and Data Selection ---
st.sidebar.header("File Selection & Data")
uploaded_file = st.sidebar.file_uploader("Choose an EPW file", type="epw", key="epw_uploader")

if 'last_file_id' not in st.session_state: st.session_state.last_file_id = None
if 'df_weather' not in st.session_state: st.session_state.df_weather = None
if 'metadata' not in st.session_state: st.session_state.metadata = {}
if 'load_status_messages' not in st.session_state: st.session_state.load_status_messages = []

if uploaded_file is not None:
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    force_reset = False

    if st.session_state.last_file_id != current_file_id:
        force_reset = True
        st.session_state.last_file_id = current_file_id
        st.session_state.df_weather = None
        st.session_state.metadata = {}
        st.session_state.load_status_messages = []
        # Add aspect_ratio_y_3d to keys_to_reset
        keys_to_reset = [
            'current_column', 'y_min_limit', 'y_max_limit', 'y_slider_range',
            'start_date', 'end_date', 'start_time', 'end_time', 'plot_key',
            'y_override_toggle', 'plot_width', 'plot_height', 'download_scale',
            'colorbar_length', 'colorbar_thickness', 'custom_plot_title',
            'aspect_ratio_x_3d', 'aspect_ratio_y_3d', # Added y ratio
            'selected_colorscale_widget', # Reset selected colorscale
            'dst_toggle' # Reset DST toggle
        ]
        for key in keys_to_reset:
            if key in st.session_state: del st.session_state[key]

        epw_content_bytes = uploaded_file.getvalue()
        df_weather, metadata, status_messages = load_epw_data_flexible_cached(epw_content_bytes)
        st.session_state.df_weather = df_weather
        st.session_state.metadata = metadata
        st.session_state.load_status_messages = status_messages
        st.session_state.data_loaded_successfully = (df_weather is not None and not df_weather.empty)

    with st.sidebar.expander("File Info & Status", expanded=True):
        if 'load_status_messages' in st.session_state:
            for level, message in st.session_state.load_status_messages:
                if level == 'success': st.success(message)
                elif level == 'info': st.info(message)
                elif level == 'warning': st.warning(message)
                elif level == 'error': st.error(message)

        if st.session_state.get('data_loaded_successfully', False):
            metadata = st.session_state.metadata
            st.write("---"); st.write("##### Location Details")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**City:** {metadata.get('city', 'N/A')}")
                st.write(f"**State/Prov:** {metadata.get('state-province', 'N/A')}")
                st.write(f"**Country:** {metadata.get('country', 'N/A')}")
                st.write(f"**Data Type:** {metadata.get('data_type', 'N/A')}")
            with col2:
                lat = metadata.get('latitude'); lon = metadata.get('longitude')
                alt = metadata.get('altitude'); tz = metadata.get('TZ')
                st.write(f"**Latitude:** {f'{lat:.4f}' if lat is not None else 'N/A'}")
                st.write(f"**Longitude:** {f'{lon:.4f}' if lon is not None else 'N/A'}")
                st.write(f"**Altitude:** {f'{alt:.1f} m' if alt is not None else 'N/A'}")
                st.write(f"**Timezone (Header):** {'GMT ' + f'{tz:+.1f}' if tz is not None else 'N/A'}") # Label clearly
                st.write(f"**WMO Station:** {metadata.get('WMO', 'N/A')}")
        elif uploaded_file is not None: # Only show if a file was uploaded but failed
             if not st.session_state.get('data_loaded_successfully', False): # Check explicit flag
                st.error("Failed to load or process EPW data. Check status messages above.")


    if st.session_state.get('data_loaded_successfully', False):
        df_weather = st.session_state.df_weather
        metadata = st.session_state.metadata

        if not isinstance(df_weather.index, pd.DatetimeIndex):
             st.error("Internal Error: Dataframe index is not DatetimeIndex.")
             st.stop()

        try:
            min_datetime = df_weather.index.min(); max_datetime = df_weather.index.max()
            # Ensure min_datetime and max_datetime are valid before extracting .date()
            if pd.isna(min_datetime) or pd.isna(max_datetime):
                st.error("Error: Could not determine valid date range from EPW data (min/max dates are NaT).")
                st.stop()
            min_date = min_datetime.date(); max_date = max_datetime.date()
        except Exception as e:
            st.error(f"Error determining date range: {e}"); st.stop()

        st.sidebar.divider(); st.sidebar.subheader("Data & Plot Type")

        all_loaded_columns = df_weather.columns.tolist()
        valid_columns_for_plotting = []; display_options = {}
        for display_label, internal_name in desired_columns_map.items():
            if internal_name in all_loaded_columns:
                try:
                    # Ensure column is numeric or can be coerced, and has at least one non-NA value
                    if pd.api.types.is_numeric_dtype(df_weather[internal_name]):
                        if df_weather[internal_name].notna().any():
                            valid_columns_for_plotting.append(internal_name)
                            display_options[display_label] = internal_name
                    else: # Try to convert
                         converted_col = pd.to_numeric(df_weather[internal_name], errors='coerce')
                         if pd.api.types.is_numeric_dtype(converted_col) and converted_col.notna().any():
                             st.session_state.df_weather[internal_name] = converted_col # Update in state
                             df_weather = st.session_state.df_weather # Ensure local df_weather is updated
                             valid_columns_for_plotting.append(internal_name)
                             display_options[display_label] = internal_name
                         # else: # If conversion fails or results in all NaNs, don't add it
                         #    logging.info(f"Column '{display_label}' ({internal_name}) could not be converted to numeric or is all NaN after conversion.")
                except Exception as e:
                    st.sidebar.warning(f"Validate column '{display_label}' error: {e}")
                    logging.warning(f"Column validation error for {internal_name}: {e}", exc_info=True)

        if not display_options:
            st.sidebar.error("No plottable numeric columns found in the EPW file."); st.stop()

        available_labels = list(display_options.keys())
        default_data_idx = available_labels.index('Dry Bulb Temperature') if 'Dry Bulb Temperature' in available_labels else 0
        selected_display_label = st.sidebar.selectbox("Select Data Series:", options=available_labels, index=default_data_idx, key='data_select')
        selected_column = display_options[selected_display_label]

        if ('current_column' not in st.session_state or st.session_state.current_column != selected_column):
            st.session_state.current_column = selected_column; force_reset = True
            if 'custom_plot_title' in st.session_state: st.session_state.custom_plot_title = ""
            if 'selected_colorscale_widget' in st.session_state: del st.session_state['selected_colorscale_widget']


        # --- Plot Type Selection ---
        plot_type = st.sidebar.radio(
            "Select Plot Type:",
            ('Scatter Plot', 'Heatmap', '3D Surface', 'Monthly Daily Profile', 'Monthly Diurnal Averages'), # Renamed option
            horizontal=True, index=0, key='plot_type_radio'
        )
        # --- End Add ---

        # --- Add DST Toggle ---
        apply_dst_approx = False # Default value
        if plot_type in ['Heatmap', '3D Surface']: # Only show for these plots
            apply_dst_approx = st.sidebar.toggle(
                "Apply Approx. DST Shift (Apr-Oct)",
                key="dst_toggle",
                value=st.session_state.get("dst_toggle", False), # Persist toggle state
                help="APPROXIMATION ONLY: Shifts hour axis +1 hr from April to October for Heatmap/3D plots. Assumes Northern Hemisphere DST rules. May be inaccurate for specific locations/years."
            )
        elif "dst_toggle" in st.session_state: # Clear toggle state if plot type changes
             st.session_state.dst_toggle = False
        # --- End Add DST Toggle ---

        st.sidebar.divider()

        # --- Include 3D aspect ratio and DST in plot key ---
        current_key_init_base = f"{selected_column}_{plot_type}"
        if plot_type == '3D Surface':
            aspect_x_key = st.session_state.get('aspect_ratio_x_3d', DEFAULT_3D_ASPECT_X)
            aspect_y_key = st.session_state.get('aspect_ratio_y_3d', 1.0)
            dst_key = "_dst" if apply_dst_approx else "_lst"
            current_key_init = f"{current_key_init_base}_aspX{aspect_x_key:.1f}_aspY{aspect_y_key:.1f}{dst_key}"
        elif plot_type == 'Heatmap':
             dst_key = "_dst" if apply_dst_approx else "_lst"
             current_key_init = f"{current_key_init_base}{dst_key}"
        else:
             current_key_init = current_key_init_base
        # --- End key mod ---

        if (force_reset or 'plot_key' not in st.session_state or st.session_state.plot_key != current_key_init):
            st.session_state.plot_key = current_key_init
            if (selected_column in df_weather.columns and pd.api.types.is_numeric_dtype(df_weather[selected_column]) and df_weather[selected_column].notna().any()):
                try:
                    y_min_overall = float(df_weather[selected_column].min())
                    y_max_overall = float(df_weather[selected_column].max())
                except Exception: y_min_overall, y_max_overall = 0.0, 10.0 # Fallback
                
                if np.isclose(y_min_overall, y_max_overall): # Handle cases with constant value
                    y_buffer_overall = 0.5 
                else: # Normal case
                    y_buffer_overall = max(abs(y_max_overall - y_min_overall) * 0.05, 0.1) # Ensure buffer is not zero if range is tiny
                
                st.session_state.y_min_limit_default = float(round(y_min_overall - y_buffer_overall, 2))
                st.session_state.y_max_limit_default = float(round(y_max_overall + y_buffer_overall, 2))
                st.session_state.y_min_limit = st.session_state.y_min_limit_default
                st.session_state.y_max_limit = st.session_state.y_max_limit_default
                # Ensure min_limit is less than max_limit after buffering
                if st.session_state.y_min_limit >= st.session_state.y_max_limit:
                    st.session_state.y_max_limit = st.session_state.y_min_limit + 0.2 # Add a bit more buffer
                st.session_state.y_slider_range = (st.session_state.y_min_limit, st.session_state.y_max_limit)
            else:
                st.sidebar.warning(f"Cannot initialize Y-axis limits for '{selected_display_label}'. Data might be non-numeric or all NaN.")
                st.session_state.y_min_limit_default = 0.0; st.session_state.y_max_limit_default = 10.0
                st.session_state.y_min_limit = 0.0; st.session_state.y_max_limit = 10.0
                st.session_state.y_slider_range = (0.0, 10.0)

            st.session_state.start_date = min_date
            st.session_state.start_time = datetime.time.min
            st.session_state.end_date = max_date
            st.session_state.end_time = datetime.time(23, 0) # Default to full day

            # Reset plot dimensions and appearance defaults (only if not set by user previously for this session)
            if 'plot_width' not in st.session_state: st.session_state.plot_width = 1000
            if 'plot_height' not in st.session_state: st.session_state.plot_height = DEFAULT_PLOT_HEIGHT
            if 'download_scale' not in st.session_state: st.session_state.download_scale = 2.0
            if 'colorbar_length' not in st.session_state: st.session_state.colorbar_length = 0.8
            if 'colorbar_thickness' not in st.session_state: st.session_state.colorbar_thickness = DEFAULT_COLORBAR_THICKNESS
            if 'y_override_toggle' not in st.session_state: st.session_state.y_override_toggle = False
            if 'custom_plot_title' not in st.session_state: st.session_state.custom_plot_title = ""
            if 'aspect_ratio_x_3d' not in st.session_state: st.session_state.aspect_ratio_x_3d = DEFAULT_3D_ASPECT_X
            if 'aspect_ratio_y_3d' not in st.session_state: st.session_state.aspect_ratio_y_3d = 1.0 # Default Y ratio


        # --- Callback Functions ---
        def update_y_axis_limits_from_slider():
            st.session_state.y_min_limit = st.session_state.y_slider_key[0]
            st.session_state.y_max_limit = st.session_state.y_slider_key[1]
        def update_y_axis_limits_from_input():
             min_val = st.session_state.y_min_limit; max_val = st.session_state.y_max_limit
             st.session_state.y_slider_range = (min_val, max(min_val + 0.1, max_val)) # Ensure min < max for slider
        def reset_time_range():
            if 'df_weather' in st.session_state and st.session_state.df_weather is not None:
                 try:
                     min_dt_reset = st.session_state.df_weather.index.min()
                     max_dt_reset = st.session_state.df_weather.index.max()
                     if pd.isna(min_dt_reset) or pd.isna(max_dt_reset):
                         st.sidebar.error("Cannot reset time: Invalid date range in data.")
                         return
                     st.session_state.start_date = min_dt_reset.date()
                     st.session_state.start_time = datetime.time.min
                     st.session_state.end_date = max_dt_reset.date()
                     st.session_state.end_time = datetime.time(23, 0) # Full day
                 except Exception as e: st.sidebar.error(f"Error resetting time range: {e}")
        def reset_value_range():
            if 'current_column' in st.session_state and 'df_weather' in st.session_state:
                col = st.session_state.current_column; df = st.session_state.df_weather
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().any():
                    try:
                        y_min_overall = float(df[col].min()); y_max_overall = float(df[col].max())
                        if np.isclose(y_min_overall, y_max_overall): y_buffer_overall = 0.5
                        else: y_buffer_overall = max(abs(y_max_overall - y_min_overall) * 0.05, 0.1)
                        
                        new_min = float(round(y_min_overall - y_buffer_overall, 2))
                        new_max = float(round(y_max_overall + y_buffer_overall, 2))
                        if new_min >= new_max: new_max = new_min + 0.2

                        st.session_state.y_min_limit = new_min
                        st.session_state.y_max_limit = new_max
                        st.session_state.y_slider_range = (new_min, new_max)
                    except Exception as e: st.sidebar.warning(f"Could not reset value range for {col}: {e}")
                else: st.sidebar.warning(f"Cannot reset range: Column '{selected_display_label}' not valid or no data.")
        def reset_colorscale():
            """Resets the colorscale selection to the data-appropriate default."""
            if 'current_column' in st.session_state:
                default_scale = get_default_colorscale(st.session_state.current_column)
                if 'selected_colorscale_widget' in st.session_state:
                    st.session_state.selected_colorscale_widget = default_scale
                # If the widget is not yet in session_state (e.g. first run for this column)
                # it will pick up this default when it's created.
            else:
                st.warning("Cannot reset colorscale: No data column selected.")

        # --- Sidebar Controls: Plot Customization ---
        st.sidebar.header("Plot Customization")

        with st.sidebar.expander("Time & Date Range", expanded=False):
            st.markdown("**Date Range**")
            col_d1, col_d2 = st.columns(2)
            with col_d1: st.date_input(f"Start Date (Year {UNIFIED_YEAR})", key="start_date", min_value=min_date, max_value=max_date)
            with col_d2: st.date_input(f"End Date (Year {UNIFIED_YEAR})", key="end_date", min_value=min_date, max_value=max_date)
            st.divider()
            st.markdown("**Time of Day Range**")
            col_t1, col_t2 = st.columns(2)
            # Using time(0,0) and time(23,0) as limits for selection, actual data uses 0-23 for hours
            with col_t1: st.time_input("Start Hour", step=3600, key="start_time", value=st.session_state.get("start_time", datetime.time.min))
            with col_t2: st.time_input("End Hour (Inclusive)", step=3600, key="end_time", value=st.session_state.get("end_time", datetime.time(23,0)))
            st.button("Reset to Full Range", on_click=reset_time_range, key="reset_time_btn", use_container_width=True)

        with st.sidebar.expander("Value Axis / Color Range", expanded=False):
            # Adjust label based on plot type
            if plot_type == 'Scatter Plot': axis_label = "Y-Axis Range (Scatter)"
            elif plot_type in ['Monthly Daily Profile', 'Monthly Diurnal Averages']: axis_label = "Y-Axis Range"
            else: axis_label = f"{selected_display_label} Color Range" # Heatmap/3D
            st.markdown(f"**{axis_label}**")

            # Determine overall min/max for slider bounds for the selected column
            slider_y_min_bound, slider_y_max_bound = st.session_state.y_min_limit_default - 5, st.session_state.y_max_limit_default + 5 # Wider bounds for slider
            if (selected_column in df_weather.columns and
                pd.api.types.is_numeric_dtype(df_weather[selected_column]) and
                df_weather[selected_column].notna().any()):
                try:
                    y_min_overall_col = float(df_weather[selected_column].min())
                    y_max_overall_col = float(df_weather[selected_column].max())
                    range_span = abs(y_max_overall_col - y_min_overall_col)
                    if np.isclose(range_span, 0): # Constant value
                        buffer = 1.0
                    else: # Dynamic buffer
                        buffer = max(range_span * 0.2, 0.5) # 20% buffer or 0.5, whichever is larger
                    slider_y_min_bound = float(round(y_min_overall_col - buffer, 2))
                    slider_y_max_bound = float(round(y_max_overall_col + buffer, 2))
                    if slider_y_min_bound >= slider_y_max_bound: slider_y_max_bound = slider_y_min_bound + 1.0 # Ensure max > min
                except Exception as e:
                    # Use default bounds on error (already set in line 955)
                    logging.warning(f"Could not calculate slider bounds for {selected_column}: {e}. Using defaults.")

            # Determine if override controls are active/disabled
            disable_value_controls = True # Default to disabled (for Y-axis of Scatter/Profile unless override is on)
            enable_y_axis_override_widget = False # Default override toggle state

            if plot_type in ['Scatter Plot', 'Monthly Daily Profile', 'Monthly Diurnal Averages']:
                enable_y_axis_override_widget = st.toggle("Override Auto Y-Axis", value=st.session_state.get("y_override_toggle", False), key="y_override_toggle")
                disable_value_controls = not enable_y_axis_override_widget
            elif plot_type in ['Heatmap', '3D Surface']: # Color range is always controllable for these plots
                disable_value_controls = False


            # Ensure current slider values (from y_min_limit, y_max_limit) are within the calculated slider bounds
            current_slider_min_val = max(slider_y_min_bound, st.session_state.y_min_limit)
            current_slider_max_val = min(slider_y_max_bound, st.session_state.y_max_limit)
            # Ensure min <= max after clamping, and there's some range for the slider
            if current_slider_min_val >= current_slider_max_val:
                current_slider_max_val = current_slider_min_val + 0.1 
            clamped_slider_val_tuple = (current_slider_min_val, current_slider_max_val)


            st.slider(f"{selected_display_label} Range - Drag",
                      min_value=slider_y_min_bound, max_value=slider_y_max_bound,
                      value=clamped_slider_val_tuple, # Use the clamped tuple from session state limits
                      step=0.1, key="y_slider_key", on_change=update_y_axis_limits_from_slider, disabled=disable_value_controls)
            col1y, col2y = st.columns(2)
            with col1y: st.number_input(f"{selected_display_label} Min", step=0.1, format="%.2f", key="y_min_limit", on_change=update_y_axis_limits_from_input, disabled=disable_value_controls)
            with col2y: st.number_input(f"{selected_display_label} Max", step=0.1, format="%.2f", key="y_max_limit", on_change=update_y_axis_limits_from_input, disabled=disable_value_controls)
            st.button("Reset Value Range", on_click=reset_value_range, key="reset_value_range_btn", use_container_width=True, disabled=disable_value_controls)

        with st.sidebar.expander("General Appearance", expanded=False):
            st.text_input("Custom Plot Title (Optional)", key="custom_plot_title", placeholder="Leave blank for default title", help="Enter a custom title to override the default plot title.")
            st.divider()
            selected_chart_bg_color = st.color_picker("Chart Background Color", value=st.session_state.get('bg_color_picker_gen_val', '#FFFFFF'), key="bg_color_picker_gen", help="Select background color. Ignored if transparent.")
            st.session_state.bg_color_picker_gen_val = selected_chart_bg_color # Persist color picker value
            selected_font_color = st.color_picker("Text/Font Color", value=st.session_state.get('font_color_picker_gen_val', '#000000'), key="font_color_picker_gen", help="Select color for axis labels/titles, ticks.")
            st.session_state.font_color_picker_gen_val = selected_font_color # Persist color picker value
            selected_font_size = st.slider("Font Size", min_value=6, max_value=24, value=st.session_state.get('font_size_slider_gen', 10), step=1, key="font_size_slider_gen", help="Adjust size for axis labels, ticks, titles.")
            transparent_bg = st.toggle("Make Background Transparent", value=st.session_state.get("transp_bg_toggle_gen", False), key="transp_bg_toggle_gen", help="Make plot background transparent (overrides color picker).")

            # --- Initialize plot_style and marker_color with defaults ---
            plot_style = st.session_state.get('plot_style_radio', 'Color Scale Markers') # Persist selection
            marker_color = st.session_state.get('marker_color_picker_val', '#1f77b4') # Persist color
            # --- End Initialization ---

            st.divider() # Divider before plot-specific options

            # --- Plot-specific appearance options ---
            if plot_type == 'Scatter Plot':
                st.markdown("**Scatter Plot Specific**")
                plot_style = st.radio("Plot Style:", ('Color Scale Markers', 'Single Color Markers'), 
                                      index=0 if plot_style == 'Color Scale Markers' else 1, 
                                      key="plot_style_radio", horizontal=True)
                marker_size = st.slider("Marker Size", min_value=1, max_value=15, value=st.session_state.get('marker_size_slider', 4), step=1, key="marker_size_slider", help="Adjust the size of the scatter plot markers.")
                if plot_style == 'Single Color Markers':
                    marker_color = st.color_picker("Marker Color", value=marker_color, key="marker_color_picker", help="Select the color for the markers.")
                    st.session_state.marker_color_picker_val = marker_color # Persist

            # --- Color Bar & Color Scale Options (Conditional) ---
            uses_colorscale = (
                plot_type in ['Heatmap', '3D Surface'] or
                (plot_type == 'Scatter Plot' and plot_style == 'Color Scale Markers')
            )

            if uses_colorscale:
                st.markdown("**Color Scale & Bar**")
                # Determine default scale for selectbox based on current data
                target_default_scale = get_default_colorscale(selected_column)
                try:
                    # Use previously selected scale from state if available, else use default
                    last_scale_in_state = st.session_state.get('selected_colorscale_widget', target_default_scale)
                    # Ensure last_scale_in_state is valid, fallback to target_default_scale or absolute default
                    if last_scale_in_state not in RECOMMENDED_COLORSCALES:
                        last_scale_in_state = target_default_scale
                    if last_scale_in_state not in RECOMMENDED_COLORSCALES: # If target_default also not in list
                        last_scale_in_state = DEFAULT_SCALE

                    default_scale_index = RECOMMENDED_COLORSCALES.index(last_scale_in_state)

                except ValueError: # Fallback if default isn't in recommended list
                    try: default_scale_index = RECOMMENDED_COLORSCALES.index(DEFAULT_SCALE)
                    except ValueError: default_scale_index = 0 # Ultimate fallback

                # Selectbox for choosing the scale
                selected_colorscale_widget_str = st.selectbox(
                    "Select Color Scale:",
                    options=RECOMMENDED_COLORSCALES,
                    index=default_scale_index,
                    key='selected_colorscale_widget', # State key for this widget
                    help="Select the color map for plots using continuous color."
                )

                # --- Add Reset Button ---
                st.button("Reset Color Scale to Default", on_click=reset_colorscale, key="reset_colorscale_btn", use_container_width=True)
                # --- End Reset Button ---

                # Color Bar Sliders (now nested under the condition)
                colorbar_length = st.slider("Color Bar Length", min_value=0.2, max_value=1.0, value=st.session_state.get('colorbar_length', 0.8), step=0.1, key="colorbar_length_slider", help="Adjust the relative length of the color bar/legend.")
                colorbar_thickness = st.slider("Color Bar Thickness (pixels)", min_value=5, max_value=50, value=st.session_state.get('colorbar_thickness', DEFAULT_COLORBAR_THICKNESS), step=1, key="colorbar_thickness_slider", help="Adjust the width (thickness) of the color bar in pixels.")
            else:
                 # Assign default values if sliders/selectbox are hidden so variables exist later
                 colorbar_length = st.session_state.get('colorbar_length', 0.8)
                 colorbar_thickness = st.session_state.get('colorbar_thickness', DEFAULT_COLORBAR_THICKNESS)
                 selected_colorscale_widget_str = None # Indicate no scale selected (string name)
            # --- End Color Bar & Scale Section ---


        with st.sidebar.expander("Plot Dimensions & Export", expanded=False):
            st.markdown("**Plot Size**")
            plot_width = st.slider("Plot Width (pixels)", min_value=400, max_value=2000, value=st.session_state.get('plot_width', 1000), step=50, key="plot_width_slider", help="Adjust the width of the plot.")
            plot_height = st.slider("Plot Height (pixels)", min_value=300, max_value=1500, value=st.session_state.get('plot_height', DEFAULT_PLOT_HEIGHT), step=50, key="plot_height_slider", help="Adjust the height of the plot.")

            # --- Add Conditional Slider for 3D Aspect Ratio ---
            if plot_type == '3D Surface':
                st.divider() # Separator
                st.markdown("**3D Plot Aspect Ratio**")
                st.slider(
                    "X-Axis (Month/Day) Visual Length Ratio",
                    min_value=0.5, max_value=5.0,
                    value=st.session_state.get('aspect_ratio_x_3d', DEFAULT_3D_ASPECT_X),
                    step=0.1, key="aspect_ratio_x_3d",
                    help="Adjusts the visual length of the X-axis relative to Y/Z axes (Default=2)."
                )
                st.slider(
                    "Y-Axis (Hour) Visual Length Ratio",
                    min_value=0.5, max_value=5.0,
                    value=st.session_state.get('aspect_ratio_y_3d', 1.0), # Default Y ratio = 1
                    step=0.1, key="aspect_ratio_y_3d", # Use the state key
                    help="Adjusts the visual length of the Y-axis relative to X/Z axes (Default=1)."
                )
            # --- End Conditional Sliders ---

            st.divider()
            st.markdown("**Export Settings**")
            download_scale = st.slider("Download Image Scale Factor", min_value=1.0, max_value=5.0, value=st.session_state.get('download_scale', 2.0), step=0.5, key="download_scale_slider", help="Scale factor for downloaded PNG images (higher = higher resolution).")


        # --- Prepare Plotting Data ---
        try:
             start_dt_val = datetime.datetime.combine(st.session_state.start_date, st.session_state.start_time)
             # For end_datetime, since EPW data is typically hourly and represents the *start* of the hour,
             # if user selects "End Hour (Inclusive)" as e.g., 23:00, we want data *up to* 23:59:59.
             # So, combine date with selected end_time, then add 59 minutes and 59 seconds.
             end_dt_val = datetime.datetime.combine(st.session_state.end_date, st.session_state.end_time) + datetime.timedelta(minutes=59, seconds=59)


             if start_dt_val > end_dt_val: # Check if start is after end
                  st.warning("Start date/time is after end date/time. Swapping them for filtering.")
                  start_dt_val, end_dt_val = end_dt_val, start_dt_val # Swap
        except Exception as e:
             st.error(f"Error combining date/time for filtering: {e}"); st.stop()

        # --- Timezone handling: df_weather.index is already naive LST ---
        df_weather_filtered_base = df_weather # Base is already naive LST after loader changes
        
        # Naive start_datetime_naive and end_datetime_naive for create_3d_surface_plot and other potential uses
        # These represent the user's selection boundary more directly for functions expecting start/end of hour ranges.
        start_datetime_naive_for_functions = datetime.datetime.combine(st.session_state.start_date, st.session_state.start_time)
        end_datetime_naive_for_functions = datetime.datetime.combine(st.session_state.end_date, st.session_state.end_time)


        try:
            # Ensure index is DatetimeIndex before filtering
            if not isinstance(df_weather_filtered_base.index, pd.DatetimeIndex):
                st.error("Internal error: DataFrame index is not DatetimeIndex before filtering.")
                st.stop()

            mask_date = (df_weather_filtered_base.index >= start_dt_val) & \
                        (df_weather_filtered_base.index <= end_dt_val)

            if plot_type == 'Scatter Plot':
                 # For scatter, only selected column is needed early.
                 # Validate column exists before accessing
                 if selected_column not in df_weather_filtered_base.columns:
                     st.error(f"Selected column '{selected_column}' not found in data.")
                     logging.error(f"Column '{selected_column}' missing from DataFrame with columns: {df_weather_filtered_base.columns.tolist()}")
                     st.stop()
                 filtered_df_date = df_weather_filtered_base.loc[mask_date, [selected_column]].copy()
            else:
                 # For other plots, might need all columns initially for pivoting, DST adj etc.
                 filtered_df_date = df_weather_filtered_base.loc[mask_date].copy()
        except TypeError as te: # Usually related to timezone-aware/naive issues if not handled properly earlier
             st.error(f"Time-based filtering error: {te}. This may indicate an issue with DatetimeIndex properties. Please report this bug."); logging.error(f"Time filtering error (TypeError): {te}", exc_info=True); st.stop()
        except Exception as filter_err:
             st.error(f"Error filtering data by date: {filter_err}"); logging.error(f"Data filtering error: {filter_err}", exc_info=True); st.stop()


        # --- Main Area: Plotting ---
        if filtered_df_date.empty:
            st.warning("No data available for the selected date and time range.")
        else:
            fig = None; table_data = None
            custom_title = st.session_state.get("custom_plot_title", "") # Get custom title

            # --- Scatter Plot ---
            if plot_type == 'Scatter Plot':
                filtered_df = filtered_df_date # Already filtered by date and has the selected_column
                if not filtered_df.empty and selected_column in filtered_df.columns and filtered_df[selected_column].notna().any():
                    default_plot_title = f'{selected_display_label} - {metadata.get("city", "Location Unknown")}'
                    plot_title_text = custom_title if custom_title else default_plot_title

                    common_marker_settings = dict(size=marker_size)
                    common_layout_settings = dict(
                         xaxis_title='Date / Time', yaxis_title=selected_display_label,
                         font=dict(family="Arial, sans-serif", size=selected_font_size, color=selected_font_color),
                         title=dict(text=plot_title_text, font=dict(size=selected_font_size + 4, color=selected_font_color)),
                         paper_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                         plot_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                         margin=dict(l=65, r=50, b=65, t=90), width=plot_width, height=plot_height,
                         legend=dict(font=dict(color=selected_font_color, size=selected_font_size))
                    )
                    if plot_style == 'Color Scale Markers':
                        # Resolve the selected/default colorscale string
                        scatter_colorscale_str_to_resolve = selected_colorscale_widget_str if selected_colorscale_widget_str else get_default_colorscale(selected_column)
                        final_scatter_colorscale = resolve_plotly_colorscale(scatter_colorscale_str_to_resolve)

                        fig = px.scatter(filtered_df, x=filtered_df.index, y=selected_column, color=selected_column,
                                         color_continuous_scale=final_scatter_colorscale, # Use resolved scale
                                         labels={'x': 'Date / Time', selected_column: selected_display_label}, title=None)
                        fig.update_traces(marker=common_marker_settings)
                        fig.update_layout(**common_layout_settings)
                        fig.update_coloraxes(
                            colorbar=dict(
                                title=dict(text=selected_display_label, font=dict(color=selected_font_color, size=selected_font_size)),
                                tickfont=dict(color=selected_font_color, size=selected_font_size),
                                len=colorbar_length,
                                thickness=colorbar_thickness # Apply thickness
                            )
                        )
                    else: # Single Color Markers
                        fig = px.scatter(filtered_df, x=filtered_df.index, y=selected_column, labels={'x': 'Date / Time', 'y': selected_display_label}, title=None)
                        fig.update_traces(marker=dict(**common_marker_settings, color=marker_color))
                        fig.update_layout(**common_layout_settings)

                    # X-axis tick formatting
                    tickformat = None; dtick = None; tickvals = None; ticktext = None # Initialize
                    if not filtered_df.index.empty and isinstance(filtered_df.index, pd.DatetimeIndex):
                        time_range_days = (filtered_df.index.max() - filtered_df.index.min()).days
                        if time_range_days <= 3: tickformat = '%H:%M\n%d-%b' # Hour, minute, day-month
                        elif time_range_days <= 60: tickformat = '%d-%b' # Day-month
                        else: # More than 60 days, try monthly ticks
                            try:
                                idx_min = filtered_df.index.min(); idx_max = filtered_df.index.max()
                                # Ensure start/end for date_range are valid
                                if pd.notna(idx_min) and pd.notna(idx_max):
                                    start_month_floor = idx_min.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                                    end_month_ceil = (idx_max.replace(day=1) + pd.DateOffset(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                                    all_ticks = pd.date_range(start=start_month_floor, end=end_month_ceil, freq='MS') # 'MS' for month start
                                    tickvals_candidate = all_ticks[(all_ticks >= idx_min) & (all_ticks <= idx_max)]
                                    if not tickvals_candidate.empty:
                                        tickvals = tickvals_candidate
                                        ticktext = [calendar.month_abbr[i.month] for i in tickvals]
                                    else: tickformat = '%b %Y' # Fallback if no suitable month start ticks
                                else: tickformat = '%b %Y' # Fallback if min/max index is NaT
                            except Exception: tickformat = '%b %Y' # General fallback
                    
                    fig.update_xaxes(tickformat=tickformat, dtick=dtick, tickvals=tickvals, ticktext=ticktext, tickangle=0, tickfont=dict(size=selected_font_size, color=selected_font_color), title_font=dict(size=selected_font_size + 2, color=selected_font_color), color=selected_font_color, gridcolor='lightgrey')

                    if enable_y_axis_override_widget: # Check if the toggle widget is active for this plot type
                         fig.update_yaxes(range=[st.session_state.y_min_limit, st.session_state.y_max_limit], gridcolor='lightgrey', tickfont=dict(size=selected_font_size, color=selected_font_color), title_font=dict(size=selected_font_size + 2, color=selected_font_color), color=selected_font_color)
                    else: # Auto-range Y-axis
                         fig.update_yaxes(tickfont=dict(size=selected_font_size, color=selected_font_color), title_font=dict(size=selected_font_size + 2, color=selected_font_color), color=selected_font_color, gridcolor='lightgrey')


                    table_data = filtered_df[[selected_column]].copy(); table_data.columns = [selected_display_label]; table_data.index.name = 'Date/Time'
                else: st.warning("No data available for scatter plot after filtering (or selected column is empty/all NaN).")


            # --- Heatmap ---
            elif plot_type == 'Heatmap':
                df_for_heatmap_base = filtered_df_date.copy() # Start with date-filtered data
                
                if not isinstance(df_for_heatmap_base.index, pd.DatetimeIndex):
                    st.error("Heatmap: Data index is not DatetimeIndex. Cannot proceed.")
                    st.stop()

                df_for_heatmap_base['hour_of_day'] = df_for_heatmap_base.index.hour

                start_hour_filter = st.session_state.start_time.hour
                end_hour_filter = st.session_state.end_time.hour
                
                if start_hour_filter <= end_hour_filter:
                    hour_mask_hm = (df_for_heatmap_base['hour_of_day'] >= start_hour_filter) & (df_for_heatmap_base['hour_of_day'] <= end_hour_filter)
                else: 
                    hour_mask_hm = (df_for_heatmap_base['hour_of_day'] >= start_hour_filter) | (df_for_heatmap_base['hour_of_day'] <= end_hour_filter)
                df_for_heatmap_hour_filtered = df_for_heatmap_base[hour_mask_hm]
                
                if df_for_heatmap_hour_filtered.empty or selected_column not in df_for_heatmap_hour_filtered or df_for_heatmap_hour_filtered[selected_column].notna().sum() == 0 :
                    st.warning("No data for selected date AND hour range for Heatmap (or selected column is empty/all NaN).")
                else:
                    # --- DST Adjustment for Plotting Hour ---
                    df_hm_pivot_ready = df_for_heatmap_hour_filtered.copy() # Work on a copy
                    if apply_dst_approx:
                        DST_START_MONTH = 4; DST_END_MONTH = 10
                        if isinstance(df_hm_pivot_ready.index, pd.DatetimeIndex):
                            dst_mask_hm = (df_hm_pivot_ready.index.month >= DST_START_MONTH) & (df_hm_pivot_ready.index.month <= DST_END_MONTH)
                            df_hm_pivot_ready['hour_for_pivot'] = df_hm_pivot_ready['hour_of_day']
                            df_hm_pivot_ready.loc[dst_mask_hm, 'hour_for_pivot'] = (df_hm_pivot_ready.loc[dst_mask_hm, 'hour_of_day'] + 1) % 24
                        else: # Should not happen
                            logging.warning("Heatmap DST: Index not DatetimeIndex.")
                            df_hm_pivot_ready['hour_for_pivot'] = df_hm_pivot_ready['hour_of_day']
                        hour_col_for_pivot_hm = 'hour_for_pivot'
                        y_axis_title_hm = "Approx. Clock Hour"
                    else:
                        df_hm_pivot_ready['hour_for_pivot'] = df_hm_pivot_ready['hour_of_day']
                        hour_col_for_pivot_hm = 'hour_for_pivot'
                        y_axis_title_hm = "Hour of Day (LST)"
                    
                    df_hm_pivot_ready['month'] = df_hm_pivot_ready.index.month
                    df_hm_pivot_ready['day_of_year'] = df_hm_pivot_ready.index.dayofyear

                    heatmap_type = st.radio("Heatmap Type:", ('Monthly Average', 'Full Year (Day x Hour)'), index=1, key="heatmap_type_radio", horizontal=True)
                    pivot_data = None; x_labels_hm = None 
                    try:
                        if heatmap_type == 'Monthly Average':
                            pivot_data = df_hm_pivot_ready.pivot_table(
                                values=selected_column, index=hour_col_for_pivot_hm, columns='month', aggfunc='mean'
                            )
                            if not pivot_data.empty:
                                x_labels_hm = [calendar.month_abbr[int(i)] for i in pivot_data.columns]; x_axis_title_hm = "Month"
                                default_plot_title = f'Monthly Avg Heatmap: {selected_display_label} - {metadata.get("city", "Loc")}'
                            else: st.warning("No data for monthly avg heatmap after pivot.")
                        else: # Full Year
                            pivot_data = df_hm_pivot_ready.pivot_table(
                                values=selected_column, index=hour_col_for_pivot_hm, columns='day_of_year', aggfunc='mean'
                            )
                            if not pivot_data.empty:
                                month_tick_vals_hm = []; month_tick_text_hm = []
                                available_days_hm = sorted(pivot_data.columns.astype(int)); first_days_of_month_hm = {}
                                for day_val in available_days_hm:
                                    if not (1 <= day_val <= 366): continue
                                    is_leap_yr = calendar.isleap(UNIFIED_YEAR)
                                    if day_val == 366 and not is_leap_yr: continue
                                    try:
                                        date_obj_hm = datetime.datetime(UNIFIED_YEAR, 1, 1) + datetime.timedelta(days=day_val - 1)
                                        month_num_hm = date_obj_hm.month
                                        if month_num_hm not in first_days_of_month_hm: first_days_of_month_hm[month_num_hm] = day_val
                                    except ValueError: continue
                                month_tick_vals_hm = sorted(first_days_of_month_hm.values())
                                month_tick_text_hm = [calendar.month_abbr[m] for m in sorted(first_days_of_month_hm.keys())]
                                x_labels_hm = pivot_data.columns # For imshow, x is the direct column values
                                x_axis_title_hm = "Day of Year (Monthly Ticks)"
                                default_plot_title = f'Daily Heatmap: {selected_display_label} - {metadata.get("city", "Loc")}'
                            else: st.warning("No data for daily heatmap after pivot.")

                        if pivot_data is not None and not pivot_data.empty:
                            plot_title_text = custom_title if custom_title else default_plot_title
                            heatmap_colorscale_str_to_resolve = selected_colorscale_widget_str if selected_colorscale_widget_str else get_default_colorscale(selected_column)
                            final_heatmap_colorscale = resolve_plotly_colorscale(heatmap_colorscale_str_to_resolve)

                            fig = px.imshow(pivot_data,
                                            labels=dict(x=x_axis_title_hm, y=y_axis_title_hm, color=selected_display_label),
                                            x=x_labels_hm if heatmap_type == 'Monthly Average' else pivot_data.columns,
                                            y=pivot_data.index,
                                            color_continuous_scale=final_heatmap_colorscale,
                                            zmin=st.session_state.y_min_limit, zmax=st.session_state.y_max_limit, aspect="auto")
                            fig.update_layout(
                                title=dict(text=plot_title_text, font=dict(size=selected_font_size + 4, color=selected_font_color)),
                                xaxis=dict(title=x_axis_title_hm, tickfont=dict(size=selected_font_size, color=selected_font_color), title_font=dict(size=selected_font_size + 2, color=selected_font_color), color=selected_font_color, gridcolor='lightgrey'),
                                yaxis=dict(title=y_axis_title_hm, range=[-0.5, 23.5], autorange=False, dtick=2, tickfont=dict(size=selected_font_size, color=selected_font_color), title_font=dict(size=selected_font_size + 2, color=selected_font_color), color=selected_font_color, gridcolor='lightgrey'),
                                font=dict(family="Arial, sans-serif", size=selected_font_size, color=selected_font_color),
                                coloraxis=dict(colorbar=dict(title=dict(text=selected_display_label, font=dict(color=selected_font_color, size=selected_font_size)), tickfont=dict(color=selected_font_color, size=selected_font_size), len=colorbar_length, thickness=colorbar_thickness)),
                                paper_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                                plot_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                                margin=dict(l=65, r=50, b=65, t=90), width=plot_width, height=plot_height
                            )
                            if heatmap_type == 'Full Year (Day x Hour)' and month_tick_vals_hm and month_tick_text_hm:
                                 fig.update_xaxes(tickmode='array', tickvals=month_tick_vals_hm, ticktext=month_tick_text_hm)
                            table_data = pivot_data
                    except Exception as hm_err: st.error(f"Error creating heatmap: {hm_err}"); logging.error(f"Heatmap creation error: {hm_err}", exc_info=True)


            # --- 3D Surface Plot ---
            elif plot_type == '3D Surface':
                 df_for_3d = filtered_df_date # Use date-filtered df (filtered by master date/time range)
                 if df_for_3d.empty or selected_column not in df_for_3d or df_for_3d[selected_column].notna().sum() == 0:
                     st.warning("No data for 3D plot in selected date range (or selected column is empty/all NaN).")
                 else:
                    colorbar_thickness_val = colorbar_thickness 
                    aspect_x_val = st.session_state.get('aspect_ratio_x_3d', DEFAULT_3D_ASPECT_X)
                    aspect_y_val = st.session_state.get('aspect_ratio_y_3d', 1.0) 

                    surface_3d_colorscale_str_to_resolve = selected_colorscale_widget_str if selected_colorscale_widget_str else get_default_colorscale(selected_column)
                    final_surface_3d_colorscale = resolve_plotly_colorscale(surface_3d_colorscale_str_to_resolve)

                    fig, pivot_data_3d = create_3d_surface_plot(
                        df_for_3d, # Pass the already date-filtered DataFrame
                        selected_column,
                        start_datetime_naive_for_functions, # Naive start for internal hour filtering
                        end_datetime_naive_for_functions,   # Naive end for internal hour filtering
                        st.session_state.y_min_limit,
                        st.session_state.y_max_limit,
                        selected_chart_bg_color,
                        selected_font_color,
                        selected_font_size,
                        transparent_bg,
                        colorscale=final_surface_3d_colorscale, # Pass resolved scale
                        plot_width=plot_width,
                        plot_height=plot_height,
                        colorbar_len=colorbar_length,
                        colorbar_thickness=colorbar_thickness_val,
                        aspect_x=aspect_x_val,
                        aspect_y=aspect_y_val,
                        apply_dst_approx=apply_dst_approx,
                        title=selected_display_label,
                        custom_title=custom_title
                    )
                    if fig: st.info("Tip: Click/drag to rotate 3D view. Scroll to zoom."); table_data = pivot_data_3d


      
# --- Monthly Daily Profile ---
            elif plot_type == 'Monthly Daily Profile':
                df_for_profile_base = filtered_df_date.copy()

                if not isinstance(df_for_profile_base.index, pd.DatetimeIndex):
                    st.error("Monthly Profile: Data index is not DatetimeIndex.")
                    st.stop()

                # Add 'hour' and 'month' if not present (should be from loader, but defensive)
                if 'hour' not in df_for_profile_base.columns: df_for_profile_base['hour'] = df_for_profile_base.index.hour
                if 'month' not in df_for_profile_base.columns: df_for_profile_base['month'] = df_for_profile_base.index.month

                start_hour_prof_filter = st.session_state.start_time.hour
                end_hour_prof_filter = st.session_state.end_time.hour
                if start_hour_prof_filter <= end_hour_prof_filter:
                    hour_mask_prof = (df_for_profile_base['hour'] >= start_hour_prof_filter) & (df_for_profile_base['hour'] <= end_hour_prof_filter)
                else:
                    hour_mask_prof = (df_for_profile_base['hour'] >= start_hour_prof_filter) | (df_for_profile_base['hour'] <= end_hour_prof_filter)
                df_for_profile = df_for_profile_base[hour_mask_prof]

                if df_for_profile.empty or selected_column not in df_for_profile.columns or df_for_profile[selected_column].notna().sum() == 0:
                     st.warning("No data available for the selected date AND hour range for Monthly Profile (or selected column is empty/all NaN).")
                else:
                    try:
                        month_abbr = [calendar.month_abbr[i] for i in range(1, 13)]
                        fig = make_subplots(rows=2, cols=6, subplot_titles=month_abbr, shared_yaxes=True, vertical_spacing=0.20)

                        y_min_prof_auto, y_max_prof_auto = None, None
                        if df_for_profile[selected_column].notna().any():
                            y_min_prof_auto = df_for_profile[selected_column].min()
                            y_max_prof_auto = df_for_profile[selected_column].max()

                        y_range_to_use_auto = None
                        if y_min_prof_auto is not None and y_max_prof_auto is not None:
                            if np.isclose(y_min_prof_auto, y_max_prof_auto):
                                 y_range_to_use_auto = [y_min_prof_auto - 0.5, y_max_prof_auto + 0.5]
                            else:
                                 y_buffer_prof = abs(y_max_prof_auto - y_min_prof_auto) * 0.05
                                 y_range_to_use_auto = [y_min_prof_auto - y_buffer_prof, y_max_prof_auto + y_buffer_prof]

                        all_avg_data = pd.DataFrame(index=range(24))

                        for i, month_num in enumerate(range(1, 13)):
                            row_idx, col_idx = (1 if i < 6 else 2), ((i % 6) + 1)
                            month_data_filtered = df_for_profile[df_for_profile['month'] == month_num]

                            if not month_data_filtered.empty and month_data_filtered[selected_column].notna().any():
                                fig.add_trace(go.Scatter(
                                    x=month_data_filtered['hour'], y=month_data_filtered[selected_column],
                                    mode='markers', marker=dict(color='rgba(100, 149, 237, 0.5)', size=3),
                                    name=f'Data {month_abbr[month_num-1]}', showlegend=False
                                ), row=row_idx, col=col_idx)

                                avg_data_for_month = month_data_filtered.groupby('hour')[selected_column].mean().reindex(range(24))
                                fig.add_trace(go.Scatter(
                                    x=avg_data_for_month.index, y=avg_data_for_month.values,
                                    mode='lines', line=dict(color='red', width=2),
                                    name=f'Avg {month_abbr[month_num-1]}', showlegend=False
                                ), row=row_idx, col=col_idx)
                                all_avg_data[month_abbr[month_num-1]] = avg_data_for_month

                        default_plot_title = f'Monthly Average Daily Profile: {selected_display_label} - {metadata.get("city", "Loc")}'
                        plot_title_text = custom_title if custom_title else default_plot_title
                        fig.update_layout(
                            title=dict(text=plot_title_text, font=dict(size=selected_font_size + 4, color=selected_font_color)),
                            font=dict(family="Arial, sans-serif", size=selected_font_size, color=selected_font_color),
                            paper_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                            plot_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                            margin=dict(l=60, r=40, b=50, t=100), showlegend=False, height=plot_height, width=plot_width
                        )
                        fig.update_xaxes(title_text='Hour of Day', range=[-1, 24], dtick=6, gridcolor='lightgrey', showline=True, linewidth=1, linecolor='lightgrey', mirror=True, tickfont=dict(color=selected_font_color, size=selected_font_size), title_font=dict(color=selected_font_color, size=selected_font_size+1))

                        # --- Corrected Y-Axes Styling ---
                        y_range_setting = y_range_to_use_auto
                        if enable_y_axis_override_widget:
                            y_range_setting = [st.session_state.y_min_limit, st.session_state.y_max_limit]

                        for r_idx_loop in [1, 2]:
                            # Apply styling with title to column 1
                            fig.update_yaxes(
                                title_text=selected_display_label, # Always set title for col 1
                                row=r_idx_loop, col=1,
                                title_font=dict(color=selected_font_color, size=selected_font_size+1),
                                gridcolor='lightgrey', showline=True, linewidth=1, linecolor='lightgrey', mirror=True,
                                tickfont=dict(color=selected_font_color, size=selected_font_size), range=y_range_setting
                            )
                            # Apply styling without title to columns 2-6
                            for c_idx_loop in range(2, 7): # c_idx_loop is defined here
                                fig.update_yaxes(
                                    title_text="", # No title for subsequent columns
                                    row=r_idx_loop, col=c_idx_loop,
                                    title_font=dict(color=selected_font_color, size=selected_font_size+1), # Keep consistent font properties even if text is empty
                                    gridcolor='lightgrey', showline=True, linewidth=1, linecolor='lightgrey', mirror=True,
                                    tickfont=dict(color=selected_font_color, size=selected_font_size), range=y_range_setting
                                )
                        # --- End Corrected Y-Axes Styling ---

                        # Update subplot titles font
                        for annotation in fig.layout.annotations:
                            annotation.font.size = selected_font_size + 1; annotation.font.color = selected_font_color

                        table_data = all_avg_data
                        if table_data is not None and not table_data.empty:
                             table_data.index.name = 'Hour'; table_data.columns.name = 'Month'
                    except Exception as profile_err:
                        # Ensure the specific error is included for debugging
                        st.error(f"Error creating Monthly Profile plot: {profile_err}")
                        logging.error(f"Monthly Profile plot error: {profile_err}", exc_info=True) # Log full traceback


            # --- Monthly Diurnal Averages Plot ---
            elif plot_type == 'Monthly Diurnal Averages': 
                df_for_avg_base = filtered_df_date.copy()

                if not isinstance(df_for_avg_base.index, pd.DatetimeIndex):
                    st.error("Monthly Diurnal Averages: Data index is not DatetimeIndex.")
                    st.stop()

                required_cols_diurnal = ['temp_air', 'ghi', 'dni'] 
                if df_for_avg_base.empty or not all(c in df_for_avg_base for c in required_cols_diurnal) or \
                   not all(df_for_avg_base[c].notna().any() for c in required_cols_diurnal):
                    st.warning(f"Required data ({', '.join(required_cols_diurnal)}) not available or all NaN for the selected range for Monthly Diurnal Averages.")
                else:
                    try:
                        COMFORT_LOW = 21.0; COMFORT_HIGH = 24.0
                        df_for_avg = df_for_avg_base.copy() 
                        if 'hour' not in df_for_avg.columns: df_for_avg['hour'] = df_for_avg.index.hour
                        if 'day_of_year' not in df_for_avg.columns: df_for_avg['day_of_year'] = df_for_avg.index.dayofyear
                        df_for_avg['date_only'] = df_for_avg.index.date 

                        hourly_avg_calc = df_for_avg.groupby(['day_of_year', 'hour'])[required_cols_diurnal].mean().reset_index()
                        full_hourly_idx_year = pd.date_range(start=f'{UNIFIED_YEAR}-01-01 00:00:00', end=f'{UNIFIED_YEAR}-12-31 23:00:00', freq='h')
                        try:
                            hourly_avg_calc['datetime'] = hourly_avg_calc.apply(
                                lambda row: datetime.datetime(UNIFIED_YEAR, 1, 1, int(row['hour'])) + datetime.timedelta(days=int(row['day_of_year']) - 1), axis=1
                            )
                            hourly_avg_calc = hourly_avg_calc.set_index('datetime').drop(['day_of_year', 'hour'], axis=1)
                            hourly_avg_reindexed = hourly_avg_calc.reindex(full_hourly_idx_year).ffill().bfill()
                        except ValueError as time_conv_err:
                             st.error(f"Error converting day/hour to datetime for aggregation: {time_conv_err}"); logging.error(f"Datetime conversion error: {time_conv_err}", exc_info=True); raise

                        daily_temps_calc = df_for_avg.groupby('date_only')['temp_air'].agg(['min', 'max'])
                        daily_temps_calc.index = pd.to_datetime(daily_temps_calc.index).map(lambda d: d.replace(year=UNIFIED_YEAR))
                        daily_idx_year = pd.date_range(start=f'{UNIFIED_YEAR}-01-01', end=f'{UNIFIED_YEAR}-12-31', freq='D')
                        daily_temps_reindexed = daily_temps_calc.reindex(daily_idx_year).ffill().bfill()
                        hourly_max_temp_plot = daily_temps_reindexed['max'].reindex(full_hourly_idx_year).ffill()
                        hourly_min_temp_plot = daily_temps_reindexed['min'].reindex(full_hourly_idx_year).ffill()

                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        temp_color = 'darkolivegreen'; temp_range_fill_color = 'rgba(255, 192, 203, 0.3)'
                        ghi_color = 'darkorange'; dni_color = 'gold'; comfort_fill_color = 'rgba(144, 238, 144, 0.3)'
                        plot_idx = hourly_avg_reindexed.index

                        fig.add_trace(go.Scatter(x=plot_idx, y=[COMFORT_LOW] * len(plot_idx), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='none'), secondary_y=False)
                        fig.add_trace(go.Scatter(x=plot_idx, y=[COMFORT_HIGH] * len(plot_idx), mode='lines', line=dict(width=0), fillcolor=comfort_fill_color, fill='tonexty', name=f'Comfort ({COMFORT_LOW:.0f}-{COMFORT_HIGH:.0f}°C)', showlegend=True, hoverinfo='skip'), secondary_y=False)
                        fig.add_trace(go.Scatter(x=hourly_min_temp_plot.index, y=hourly_min_temp_plot, mode='lines', line=dict(width=0, color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='none'), secondary_y=False)
                        fig.add_trace(go.Scatter(x=hourly_max_temp_plot.index, y=hourly_max_temp_plot, mode='lines', line=dict(width=0, color='rgba(0,0,0,0)'), fillcolor=temp_range_fill_color, fill='tonexty', name='Avg Daily Temp Range', showlegend=True, hoverinfo='skip'), secondary_y=False)
                        fig.add_trace(go.Scatter(x=hourly_avg_reindexed.index, y=hourly_avg_reindexed['temp_air'], mode='lines', name='Avg Temp (°C)', line=dict(color=temp_color, width=1.5)), secondary_y=False)
                        fig.add_trace(go.Scatter(x=hourly_avg_reindexed.index, y=hourly_avg_reindexed['ghi'], mode='lines', name='Avg GHI (Wh/m²)', line=dict(color=ghi_color, width=1.5)), secondary_y=True)
                        fig.add_trace(go.Scatter(x=hourly_avg_reindexed.index, y=hourly_avg_reindexed['dni'], mode='lines', name='Avg DNI (Wh/m²)', line=dict(color=dni_color, width=1.0)), secondary_y=True)

                        default_plot_title = f'Monthly Diurnal Averages - {metadata.get("city", "Location")}'
                        plot_title_text = custom_title if custom_title else default_plot_title
                        fig.update_layout(
                            title=dict(text=plot_title_text, font=dict(size=selected_font_size + 4, color=selected_font_color)),
                            font=dict(family="Arial, sans-serif", size=selected_font_size, color=selected_font_color),
                            paper_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                            plot_bgcolor='rgba(0,0,0,0)' if transparent_bg else selected_chart_bg_color,
                            margin=dict(l=60, r=70, b=50, t=100), width=plot_width, height=plot_height,
                            hovermode="x unified",
                            legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="right", x=0.99, bgcolor='rgba(255,255,255,0.7)', bordercolor=selected_font_color, borderwidth=1)
                        )
                        fig.update_xaxes(title_text=None, tickformat="%b", dtick="M1", gridcolor='darkgrey', showline=True, linewidth=1, linecolor='black', mirror=True, tickfont=dict(color=selected_font_color, size=selected_font_size), title_font=dict(color=selected_font_color, size=selected_font_size+1))
                        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False, gridcolor='darkgrey', showline=True, linewidth=1, linecolor='black', mirror=True, tickfont=dict(color=selected_font_color, size=selected_font_size), title_font=dict(color=selected_font_color, size=selected_font_size+2))
                        fig.update_yaxes(title_text="Radiation (Wh/m²)", secondary_y=True, showgrid=False, showline=True, linewidth=1, linecolor='black', mirror=True, tickfont=dict(color=selected_font_color, size=selected_font_size), title_font=dict(color=selected_font_color, size=selected_font_size+2))

                        if enable_y_axis_override_widget: 
                             fig.update_yaxes(range=[st.session_state.y_min_limit, st.session_state.y_max_limit], secondary_y=False)
                        table_data = None 
                    except Exception as overview_err:
                        st.error(f"Error creating Monthly Diurnal Averages plot: {overview_err}"); logging.error(f"Monthly Diurnal Averages plot error: {overview_err}", exc_info=True)


            # --- Display Plot and Data Table ---
            if fig:
                 # --- Create a unique key for the plot ---
                 chart_key_parts = [
                     "plotly_chart", plot_type, selected_column,
                     f"w{plot_width}h{plot_height}",
                     f"sd{st.session_state.start_date}st{st.session_state.start_time.strftime('%H%M')}", # Format time
                     f"ed{st.session_state.end_date}et{st.session_state.end_time.strftime('%H%M')}",   # Format time
                     f"bg{selected_chart_bg_color}font{selected_font_color}size{selected_font_size}transp{transparent_bg}"
                 ]
                 if custom_title: chart_key_parts.append(f"title{hash(custom_title)}") # Hash long titles

                 if uses_colorscale and selected_colorscale_widget_str:
                     chart_key_parts.append(f"cs{selected_colorscale_widget_str}")
                     chart_key_parts.append(f"cblen{colorbar_length}cbthick{colorbar_thickness}")
                     chart_key_parts.append(f"valmin{st.session_state.y_min_limit:.1f}valmax{st.session_state.y_max_limit:.1f}")


                 if plot_type == 'Scatter Plot':
                     chart_key_parts.append(f"style{plot_style}msize{marker_size}")
                     if plot_style == 'Single Color Markers': chart_key_parts.append(f"mcolor{marker_color}")
                     if enable_y_axis_override_widget: chart_key_parts.append(f"yovr{st.session_state.y_min_limit:.1f}{st.session_state.y_max_limit:.1f}")

                 elif plot_type == 'Heatmap':
                     chart_key_parts.append(f"hmtype{heatmap_type}")
                     if apply_dst_approx: chart_key_parts.append("dstTRUE")

                 elif plot_type == '3D Surface':
                     aspect_x_val_key = st.session_state.get('aspect_ratio_x_3d', DEFAULT_3D_ASPECT_X)
                     aspect_y_val_key = st.session_state.get('aspect_ratio_y_3d', 1.0)
                     chart_key_parts.append(f"aspX{aspect_x_val_key:.1f}aspY{aspect_y_val_key:.1f}")
                     if apply_dst_approx: chart_key_parts.append("dstTRUE")

                 elif plot_type in ['Monthly Daily Profile', 'Monthly Diurnal Averages']:
                     if enable_y_axis_override_widget: chart_key_parts.append(f"yovr{st.session_state.y_min_limit:.1f}{st.session_state.y_max_limit:.1f}")
                 
                 chart_key = "_".join(map(str, chart_key_parts)).replace("#", "") # Remove # from color hex in key


                 st.plotly_chart(
                     fig,
                     key=chart_key, # Use the more detailed key
                     use_container_width=False, # Respect plot_width/height from sliders
                     config={'toImageButtonOptions': {'scale': download_scale}}
                 )

            if table_data is not None and not table_data.empty:
                with st.expander("View Plotted Data Table", expanded=False):
                    st.write(f"##### Data for {selected_display_label} ({plot_type})")
                    display_table = table_data.copy()
                    # Formatting for table view
                    if isinstance(display_table.index, pd.DatetimeIndex):
                         try: display_table.index = display_table.index.strftime('%Y-%m-%d %H:%M')
                         except Exception as e:
                             # Keep original index format if strftime fails
                             logging.warning(f"Could not format DatetimeIndex for table display: {e}")
                    
                    # Round numeric data for display
                    for col_to_round in display_table.columns:
                        if pd.api.types.is_numeric_dtype(display_table[col_to_round]):
                            try:
                                display_table[col_to_round] = display_table[col_to_round].round(2)
                            except TypeError: # Handle potential errors if column contains non-numeric mixed types after all
                                pass


                    if plot_type in ['Heatmap', '3D Surface', 'Monthly Daily Profile']:
                         if plot_type not in ['Monthly Daily Profile']: # Already formatted index/cols
                             if display_table.index.name != 'Hour' and pd.api.types.is_integer_dtype(display_table.index):
                                display_table.index.name = 'Hour' # Assuming integer index is hour for heatmap/3D
                             if plot_type == 'Heatmap' and heatmap_type == 'Monthly Average':
                                  try:
                                      # Ensure column names are convertible to int for month_abbr
                                      display_table.columns = [calendar.month_abbr[int(month_num)] for month_num in display_table.columns]
                                      display_table.columns.name = 'Month'
                                  except (ValueError, TypeError): display_table.columns.name = 'Month_Number' # Fallback
                             elif (plot_type == 'Heatmap' and heatmap_type == 'Full Year (Day x Hour)') or plot_type == '3D Surface':
                                  if pd.api.types.is_integer_dtype(display_table.columns) or pd.api.types.is_float_dtype(display_table.columns): # DayOfYear can be float from pivot
                                    display_table.columns.name = 'DayOfYear'


                    st.dataframe(display_table)

                    # Download Buttons
                    try: csv_data_bytes = display_table.to_csv().encode('utf-8')
                    except Exception: csv_data_bytes = None
                    try:
                        excel_buffer_io = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer_io, engine='xlsxwriter') as writer_excel: display_table.to_excel(writer_excel, sheet_name='Data')
                        excel_data_bytes = excel_buffer_io.getvalue()
                    except Exception: excel_data_bytes = None

                    # Sanitize filename
                    safe_city_fname = "".join(c for c in metadata.get('city','data') if c.isalnum() or c in (' ', '_')).rstrip()
                    safe_col_fname = "".join(c for c in selected_display_label if c.isalnum() or c in (' ', '_')).rstrip()
                    safe_plot_fname = "".join(c for c in plot_type if c.isalnum() or c in (' ', '_')).rstrip()
                    fname_base_dl = f"{safe_city_fname}_{safe_col_fname}_{safe_plot_fname}".replace(' ', '_')


                    col_btn1_dl, col_btn2_dl = st.columns(2)
                    with col_btn1_dl:
                        if csv_data_bytes: st.download_button(label="Download Table as CSV", data=csv_data_bytes, file_name=f"{fname_base_dl}.csv", mime="text/csv", key=f"csv_dl_{plot_type}_{selected_column}", use_container_width=True)
                    with col_btn2_dl:
                         if excel_data_bytes: st.download_button(label="Download Table as Excel", data=excel_data_bytes, file_name=f"{fname_base_dl}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"xlsx_dl_{plot_type}_{selected_column}", use_container_width=True)
            # Show message if plot type doesn't have a table view (like Monthly Diurnal Averages)
            elif fig and plot_type in ['Monthly Diurnal Averages']:
                 with st.expander("View Plotted Data Table", expanded=False):
                      st.info(f"A summarized data table view is not available for the {plot_type} plot type due to its aggregated nature.")


elif not st.session_state.get('data_loaded_successfully', False) and uploaded_file is None:
    st.info("⬅️ Please upload an EPW file using the sidebar to begin.")