import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date

import requests
import logbook

gspread_log = logbook.Logger('Google')

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "services/client_secret_gspread.json", scope
    )
except FileNotFoundError:
    msg = 'File client_secret_gspread.json not found, required for google doc connection. Please download and save in services folder and try again.'
    print(msg)
    gspread_log.warning(msg)
    raise

client = gspread.authorize(creds)

SUMMARY_COLUMNS = [
    "Title_left",
    "Subtitle_left",
    "Projected_left",
    "Actual_left",
    "Diff_left",
    "Title_right",
    "Subtitle_right",
    "Projected_right",
    "Actual_right",
    "Diff_right",
]

TXN_COLUMNS = ["Hash", "Date", "Amount", "Description", "Category"]


def load_budget_workbook(filename, month):
    try:
        sheets = client.open(filename)
        gspread_log.trace(f'Opened file {filename}')
    except Exception as e:
        gspread_log.warning(f'{type(e)} error trying to open {filename} - {e}')
        raise
    
    month = month.split("-")[1]

    # Load summary sheet
    try:
        summary = sheets.worksheet(f"Budget-{month}")
        gspread_log.trace(f'Opened tab Budget-{month}')
    except Exception as e:
        gspread_log.warning(f'{type(e)} error trying to open tab Budget-{month} - {e}')
        raise

    sum_df = pd.DataFrame(
        [row[:10] for row in summary.get_all_values()[10:]], columns=SUMMARY_COLUMNS
    )
    sum_df.head()

    # Load transactions sheet
    transactions = sheets.worksheet(f"Activity-{month}")
    trans_df = pd.DataFrame(transactions.get_all_values()[1:], columns=TXN_COLUMNS)

    trans_df["Amount"] = trans_df["Amount"].map(convert_to_float)

    try:
        trans_df["Date"] = trans_df["Date"].map(pd.to_datetime)
    except Exception as e:
        gspread_log.warning(f'{type(e)} - Error converting trans_df dates to datetime - {e}')

    gspread_log.info('') #TODO - finish this!!

    return sum_df, trans_df


def identify_new_txns(cur_df, trans_df, summary_df):
    # cur_df['category'] = cur_df
    new_hash = set(cur_df["hash"])
    cur_hash = set(trans_df["Hash"])

    new_txns = new_hash - cur_hash

    print(f"Total txns of {len(new_hash)}, new txns are {len(new_txns)}")
    new_txns_df = cur_df[cur_df["hash"].isin(new_txns)]

    return new_txns_df


def combine_transactions(trans_df, new_df):
    trans_df = trans_df[["Hash", "Date", "Amount", "Description", "Category"]]
    total_df = new_df.append(trans_df)

    try:
        total_df["Date"] = total_df["Date"].dt.date
    except Exception as e:
        print("Error - {}".format(e))

    total_df = total_df.sort_values(by="Date", ascending=False).reset_index(drop=True)

    total_df = total_df.fillna("")
    return total_df


def convert_txn_headers(new_df):

    xwalk = {
        "hash": "Hash",
        "date": "Date",
        "amount": "Amount",
        "description": "Description",
        "m_category": "Category",
    }

    new_df = pd.DataFrame(new_df[list(xwalk.keys())])

    new_df = new_df.rename(columns=xwalk)

    return new_df


def convert_to_float(amt):
    try:
        return float(amt.replace("$", "").replace(",", ""))
    except ValueError:
        return amt


def save_transactions(df, filename, month):
    month = month.split("-")[1]

    print("getting values")
    try:
        sheets = client.open(filename)
    except requests.exceptions.ConnectionError:
        gspread_log.warning(f'ConnectionError! Error accessing file {filename}')
        raise
        
    transactions = sheets.worksheet(f"Activity-{month}")
    num_rows = 2 + len(df)
    current_rows = transactions.row_count

    if current_rows < num_rows:
        print("Current rows are {}, total needed are {}".format(current_rows, num_rows))
        transactions.add_rows(num_rows - current_rows)

    cell_list = transactions.range("A2:E{}".format(num_rows))

    num = 0

    print("updating local values")

    for idx, row in df.iterrows():
        for value in row:
            if isinstance(value, date):
                cell_list[num].value = str(value)
            else:
                cell_list[num].value = value
            num += 1

    print("Updating workbook")
    transactions.update_cells(cell_list)
    print("Update complete")

