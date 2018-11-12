import pandas as pd
import os

from jinja2 import Environment, PackageLoader, select_autoescape

from services.send_email import create_message
from services.budget_tools import load_budget_workbook, save_transactions, identify_new_txns, convert_txn_headers, combine_transactions
from services.mint_tools import download_detailed_transactions

month = '2018-10'
budget_file = '2018-2019'


def numify(num):
    try:
        return int(num.replace('$','').replace(',',''))
    except ValueError:
        return 0


def get_summary_df(budget_file: str=budget_file, month: str=month) -> pd.DataFrame:
    sum_df, trans_df = load_budget_workbook(filename=f'{budget_file} Monthly budget', month=month)

    sum_df_l = sum_df.iloc[:,:5].copy()
    sum_df_l['Projected_left'] = sum_df_l['Projected_left'].map(numify)
    sum_df_l['Actual_left'] = sum_df_l['Actual_left'].map(numify)
    sum_df_l['Diff_left'] = sum_df_l['Diff_left'].map(numify)
    sum_df_l = sum_df_l[(sum_df_l['Projected_left'] > 0) & (sum_df_l['Subtitle_left'] != 'Total')]

    sum_df_l.columns = ['Title', 'Subtitle', 'Projected', 'Actual', 'Diff'] 

    sum_df_r = sum_df.iloc[:,5:].copy()
    sum_df_r['Projected_right'] = sum_df_r['Projected_right'].map(numify)
    sum_df_r['Actual_right'] = sum_df_r['Actual_right'].map(numify)
    sum_df_r['Diff_right'] = sum_df_r['Diff_right'].map(numify)
    sum_df_r = sum_df_r[(sum_df_r['Projected_right'] > 0) & (sum_df_r['Subtitle_right'] != 'Total')]

    sum_df_r.columns = ['Title', 'Subtitle', 'Projected', 'Actual', 'Diff'] 

    full_df = pd.concat([sum_df_l, sum_df_r])

    return full_df

def draft_message(full_df):
    projected, actual, diff = full_df[['Projected', 'Actual', 'Diff']].sum()
    food = full_df[full_df.Title.isin(['FOOD | GROCERIES', 'FOOD | RESTAURANTS'])]

    msg = f'''
            <h2>Total budgeted vs actual expenses:</h2>
            <ul>
            <li>Projected expenses are {projected}</li>
            <li>Actual expenses are {actual}</li>
            <li>Difference is {diff}</li></ul>
            <h2>Restaurant and Grocery Expense</h2> 
            {food.to_html(index=False)}
            '''

    return msg


