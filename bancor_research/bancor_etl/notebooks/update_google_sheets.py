# coding=utf-8
"""
# --------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------------------
"""

# COMMAND ----------
"""
Instructions:

Adding new tables:
* Ensure a spark table exists in databricks with an appropriate table name
* Add the table name to the list of tables in CMD 6 in this notebook.

Adding new columns:
* Update the data dictionary with new column and type in google sheets

Updates require 30+ minutes to complete once started.
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dependencies

# COMMAND ----------

import tempfile
import joblib
import pandas as pd
from shutil import copyfile
import decimal
import mlflow
import pygsheets
import numpy as np
from decimal import Decimal
from pandas.api.types import is_string_dtype, is_numeric_dtype
from pyspark.sql import functions as F
from typing import Tuple
import os
from sklearn.preprocessing import OrdinalEncoder
import time

# COMMAND ----------
from bancor_research.bancor_etl.src.google_sheets_utils import *

data_dictionary = get_data_dictionary()
data_dictionary

# COMMAND ----------

ALL_COLUMNS = list(data_dictionary['Column'].values)
NUM_UNIQUE_COLUMNS = len(ALL_COLUMNS)
GOOGLE_SHEETS_MAX_ROWS = int(round(GOOGLE_SHEETS_MAX_CELLS / NUM_UNIQUE_COLUMNS, 0))

for col in ALL_COLUMNS:
    col_type = data_dictionary[data_dictionary['Column'] == col]['Type'].values[0]
    DEFAULT_VALUE_MAP[col] = TYPE_MAP[col_type]['fillna']


# COMMAND ----------

# MAGIC %md
# MAGIC ## Combine Tables

# COMMAND ----------

unique_col_mapping, combined_df = get_event_mapping(
    all_columns=ALL_COLUMNS,
    default_value_map=DEFAULT_VALUE_MAP
)

# Loops through each table.
for table_name in LIST_OF_SPARK_TABLES:

    try:
        # Cleans the google sheets name for clarity.
        clean_table_name = clean_google_sheets_name(table_name)

        # Loads spark tables and converts to pandas
        pdf = get_pandas_df(table_name)

        # Adds a new column with the event name based on table name
        pdf = add_event_name_column(pdf, clean_table_name)

        # Normalizes unique columns across all tables
        pdf = add_missing_columns(pdf, unique_col_mapping, ALL_COLUMNS)

        # Combine the dataframes
        combined_df = concat_dataframes(pdf, combined_df)

    except ValueError as e:
        print(e, f'table not found {table_name}')

# COMMAND ----------

# MAGIC %md
# MAGIC ## Handle Types & Missing Values

# COMMAND ----------
for val in REPLACE_WITH_NA:
    combined_df['bntprice'] = combined_df['bntprice'].replace(val, '0.0')
    combined_df['emaRate'] = combined_df['emaRate'].replace(val, '0.0')

# COMMAND ----------

# fills in any remaining missing values for encoder
combined_df = handle_types_and_missing_values(combined_df, DEFAULT_VALUE_MAP, ALL_COLUMNS, TYPE_MAP)
combined_df

# COMMAND ----------

# MAGIC %md
# MAGIC ## Logging

# COMMAND ----------

# Log to mlflow for easy download reference
combined_df.to_csv('/dbfs/FileStore/tables/combined_df.csv', index=False)
mlflow.log_artifact('/dbfs/FileStore/tables/combined_df.csv')

# COMMAND ----------

# perform encoding if desired
if len(ADDRESS_COLUMNS) > 0:
    combined_df = encode_address_columns(combined_df, ADDRESS_COLUMNS)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Split Dataframe into chunks

# COMMAND ----------

combined_df = remove_unused_events(combined_df)

# COMMAND ----------

file_size_compatible = False

while not file_size_compatible:

    # Splits the pandas dataframe into chunks which conform to the max google sheet size.
    pdf_chunks = split_dataframe(combined_df, TABLEAU_MANAGEABLE_ROWS)

    # Store the number of chunks to upload to google sheets
    num_chunks = len(pdf_chunks)

    # Recheck if the file size is <= 10MB per tableau requirements
    file_size_compatible = is_file_size_compatible(pdf_chunks)

    # Increment size downward by 1000 and try again if not compatible
    if not file_size_compatible:
        TABLEAU_MANAGEABLE_ROWS -= 1000

# COMMAND ----------

# print expected data size for easy reference
num_chunks, len(combined_df), list(combined_df.columns), TABLEAU_MANAGEABLE_ROWS, GOOGLE_SHEETS_MAX_ROWS

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write Google Sheets

# COMMAND ----------

for i in range(num_chunks):
    handle_google_sheets(f'{EVENTS_TABLE}_{i}', f'{EVENTS_TABLE}_{i}', pdf_chunks[i])

# COMMAND ----------

delete_unused_google_sheets(num_chunks)

# COMMAND ----------

# combined_df[combined_df.event_name=='v3_historical_spotrates_emarates']

# COMMAND ----------

from collections import Counter

Counter(combined_df.event_name)
