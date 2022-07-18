# coding=utf-8
"""
# --------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------------------
"""
import pandas as pd
import numpy as np
from typing import Tuple
import os
from sklearn.preprocessing import OrdinalEncoder
import time
import pygsheets
from bancor_research.bancor_etl.src.constants import *
import pyspark
from pyspark.sql import SparkSession

# Initialization of dbutils to avoid linting errors during developing in vscode/pycharm/IDE


def get_dbutils(spark):
    """Return dbutils for databricks."""
    if spark.conf.get("spark.databricks.service.client.enabled") == "true":
        from pyspark.dbutils import DBUtils

        return DBUtils(spark)
    else:
        import IPython

        return IPython.get_ipython().user_ns["dbutils"]


spark = SparkSession.builder.appName("Pipeline").getOrCreate()
dbutils = get_dbutils(spark)

# MAGIC %md
# MAGIC ## Functions

# COMMAND ----------

def get_pandas_df(table_name: str) -> pd.DataFrame:
    """
    Load spark table and convert to pandas.
    """
    # Gets the latest Databricks table refresh
    spark.sql(f'refresh table {table_name}')

    # Load into a dataframe via spark and convert to pandas.
    df = spark.sql(f'select * from {table_name}')
    pdf = df.toPandas()
    return pdf


def split_dataframe(df: pd.DataFrame,
                    chunk_size: int = TABLEAU_MANAGEABLE_ROWS
                    ) -> pd.DataFrame:
    """
    Splits dataframe into chunks where each chunk has a specified size (in rows).
    """
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        chunks.append(df[i * chunk_size:(i + 1) * chunk_size])
    return chunks


def clean_google_sheets_name(name: str
                             ) -> str:
    """
    Cleans the google sheets name for clarity.
    """
    return name.replace('_csv', '').replace('events_', '')


def handle_google_sheets_auth():
    """
    Connect to google sheets via API, then uploads and overwrites worksheets by name.
    """
    gc = pygsheets.authorize(service_file=GOOGLE_SHEETS_CREDENTIALS)
    return gc


def delete_unused_google_sheets(num_chunks: list, max_search: int = 100):
    """
    Connect to google sheets via API, then delete any old google sheets not currently used.
    """

    gc = handle_google_sheets_auth()

    # Try to open the Google sheet based on its title and if it fails, create it
    sheet_titles = ['all_events_' + str(n) for n in range(num_chunks, max_search)]
    for title in sheet_titles:
        try:
            # sheet = gc.delete(title)
            res = gc.sheet.get(title)
            sheet_id = res['spreadsheetId']
            gc.drive.delete(sheet_id)
            print(f"Deleted spreadsheet with title:{title}")

        except:
            # Can't find it to delete it
            pass


def handle_google_sheets(clean_table_name: str,
                         clean_table_name_chunk: str,
                         pdf_chunk: pd.DataFrame
                         ):
    """
    Connect to google sheets via API, then uploads and overwrites worksheets by name.
    """
    gc = handle_google_sheets_auth()

    # print for troubleshooting
    print(clean_table_name_chunk)

    # resize the sheet dynamically
    num_rows = len(pdf_chunk)
    num_cols = len(list(pdf_chunk.columns))

    # Try to open the Google sheet based on its title and if it fails, create it
    sheet_title = clean_table_name_chunk
    try:
        wb = gc.open(sheet_title)
        sheet = wb.worksheet_by_title(sheet_title)
        print(f"Opened spreadsheet with id:{sheet_title}")

    except pygsheets.SpreadsheetNotFound as error:
        # Can't find it and so create it
        res = gc.sheet.create(sheet_title)
        sheet_id = res['spreadsheetId']
        sheet = gc.open_by_key(sheet_id)
        print(f"Created spreadsheet with id:{sheet.id} and url:{sheet.url}")

        # Share with self to allow to write to it
        if FORCE_RATE_THROTTLE:
            time.sleep(SLEEP_TIME)
        sheet.share(ROBOT_EMAIL, role='writer', type='user')

        if FORCE_RATE_THROTTLE:
            time.sleep(SLEEP_TIME)
        sheet.share(USER_EMAIL, role='writer', type='user')

        # Share to all for reading
        sheet.share('', role='reader', type='anyone')
        sheet.add_worksheet(sheet_title,
                            rows=num_rows,
                            cols=num_cols)
        # open the sheet by name
        wb = gc.open(sheet_title)
        sheet = wb.worksheet_by_title(sheet_title)

    sheet.resize(num_rows, num_cols)

    # Write dataframe into it
    sheet.set_dataframe(pdf_chunk, (1, 1))


def add_event_name_column(pdf: pd.DataFrame, clean_table_name: str) -> pd.DataFrame:
    """
    Create a new column with the event name
    """
    pdf['event_name'] = [clean_table_name for _ in range(len(pdf))]
    return pdf


def add_unique_columns(pdf: pd.DataFrame,
                       unique_col_mapping: dict,
                       default_value_map: dict) -> dict:
    """
    Appends newly found unique columns to dictionary along with types.
    """
    for col in pdf.columns:
        if col not in unique_col_mapping:
            if col in default_value_map:
                unique_col_mapping[col] = default_value_map[col]
            else:
                unique_col_mapping[col] = np.nan
    return unique_col_mapping


def get_event_mapping(all_columns: list,
                      default_value_map: dict,
                      unique_col_mapping: dict = {},
                      combined_df: dict = {}) -> dict:
    """
    Finds unique column names and their type for all event tables.
    """
    # Loops through each table.
    for table_name in LIST_OF_SPARK_TABLES:
        # Cleans the google sheets name for clarity.
        clean_table_name = clean_google_sheets_name(table_name)
        pdf = get_pandas_df(table_name)
        pdf = add_event_name_column(pdf, clean_table_name)
        unique_col_mapping = add_unique_columns(pdf, unique_col_mapping, default_value_map)

    unique_col_mapping_cp = {}
    for col in all_columns:
        unique_col_mapping_cp[col] = unique_col_mapping[col]

    for col in unique_col_mapping_cp:
        combined_df[col] = []

    return unique_col_mapping_cp, pd.DataFrame(combined_df)


def add_missing_columns(pdf: pd.DataFrame,
                        unique_col_mapping: dict,
                        all_columns: list) -> pd.DataFrame:
    """
    Creates a consistent set of columns and their types across all event tables.
    """
    # Create new columns with default missing values per the correct data type
    missing_cols = [col for col in all_columns if col not in pdf.columns]
    for col in missing_cols:
        default_value = unique_col_mapping[col]
        pdf[col] = [default_value for _ in range(len(pdf))]
    pdf = pdf[all_columns]
    return pdf


def concat_dataframes(pdf: pd.DataFrame, combined_df: pd.DataFrame):
    """
    Joins the event table to the combined events table.
    """
    combined_df = combined_df.reset_index().drop('index', axis=1)
    pdf = pdf.reset_index().drop('index', axis=1)

    # Concatenate the dataframes
    return pd.concat([combined_df, pdf])


def handle_types_and_missing_values(pdf: pd.DataFrame,
                                    default_value_map: dict,
                                    all_columns: list,
                                    type_map: dict,
                                    data_dictionary: pd.DataFrame
                                    ) -> pd.DataFrame:
    """
    Final cleanup to fill-in NA values before splitting the df.
    """

    for col in default_value_map:
        if col in pdf.columns:
            default_value = default_value_map[col]
            pdf[col] = pdf[col].fillna(default_value)
            col_type = type_map[
                data_dictionary[data_dictionary['Column'] == col
                                ]['Type'].values[0]]['type']
            if col_type == 'decimal':
                for err in REPLACE_WITH_NA:
                    pdf[col] = pdf[col].replace(err, default_value)
            pdf[col] = pdf[col].astype(col_type)

    return pdf[all_columns]


def get_index_df(combined_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Creates a new df with all index values to rejoin in Tableau.
    """
    combined_df = combined_df.reset_index()
    combined_df = combined_df.drop('index', axis=1)
    combined_df = combined_df.reset_index()
    index_df = combined_df[['index']]
    return combined_df, index_df


def is_file_size_compatible(pdf_chunks: list,
                            is_file_size_compatible: bool = True,
                            filepath: str = '/dbfs/FileStore/tables/sizecheck.csv',
                            size_limit: int = 10000000
                            ) -> bool:
    """
    Checks that csv filesize < 10MB.
    """
    for chunk in pdf_chunks:
        chunk.to_csv(filepath, index=False)
        sz = os.path.getsize(filepath)
        if sz > size_limit:
            is_file_size_compatible = False
            break
    return is_file_size_compatible


def encode_address_columns(combined_df: pd.DataFrame, address_columns: list) -> pd.DataFrame:
    """
    Encodes the Ethereum address column values with an integer id to improve performance for tableau.
    """
    enc = OrdinalEncoder()
    X = combined_df[address_columns]
    X = X.fillna('NA')
    X_t = enc.fit_transform(X)
    combined_df[address_columns] = X_t
    return combined_df


def get_data_dictionary() -> pd.DataFrame:
    """
    Gets the latest data dictionary from google sheets and converts to a pandas dataframe.
    """
    gc = handle_google_sheets_auth()

    # open the sheet data dictionary by name
    wb = gc.open('data_dictionary')
    data_dictionary = wb.worksheet_by_title('data_dictionary').get_as_df()
    return data_dictionary


def remove_unused_events(combined_df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes unused events from the combined dataframe.
    """
    keep_events = combined_df['event_name'].unique()
    keep_events = [
        clean_google_sheets_name(event) for event in keep_events if event not in UNUSED_EVENTS
    ]
    combined_df = combined_df[
        combined_df['event_name'].isin(keep_events)
    ]
    return combined_df
