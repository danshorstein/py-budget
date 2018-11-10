from datetime import datetime
import hashlib
import json
import time
import os

import pandas as pd
import mintapi
import logbook

from services.secrets import login
from services.budget_xwalks import desc_category, hash_category, mapped_category, mapped_account, first_11

email = login['username']
password = login['password']

mint_log = logbook.Logger('Mint')

base_path = os.path.dirname(__file__)
mint_data_path = os.path.join(base_path, '..', 'mint_data.json')    

def filter_by_month(row, m_filt, y_filt):
    y, m, *_ = row.date.date().timetuple()
    return True if (y == y_filt) & (m == m_filt) else False

def hash_row(row):
    tup = tuple(row[['date', 'description', 'amount', 'transaction_type', 'account_name']]) 
    # return hashlib.md5(str(tup).encode()).hexdigest()
    return str(tup)

def download_transactions(month, use_local=False):
    cur_year, cur_mon = [int(val) for val in month.split('-')]

    if not use_local:
        mint_log.trace(f'downloading transactions for {cur_mon}/{cur_year}')
        mint = mintapi.Mint(email, password, headless=True, mfa_method='sms')
        mint.initiate_account_refresh()

        df = mint.get_transactions()    
        df.to_json('mint_data.json')

    else:
        mint_log.trace(f'using local file to get transactions for {cur_mon}/{cur_year}')
        df = pd.read_json('mint_data.json')

    df['hash'] = df.apply(hash_row, axis=1)
    df['spent'] = df.apply(
        lambda x: x.amount * {'debit': 1, 'credit': -1}[x.transaction_type],
        axis=1)
    cur_df = df[df.apply(lambda x: filter_by_month(x, cur_mon, cur_year), axis=1)].copy()
    cur_df['month'] = cur_mon
    cur_df = cur_df.apply(update_categories, axis=1)
    return cur_df

def download_detailed_transactions(month, use_local=False, refresh_acct=True):
    cur_year, cur_mon = [int(val) for val in month.split('-')]

    start_date = f'{cur_mon}/01/{str(cur_year)[2:]}'
    print(start_date)

    if not use_local:
        mint_log.trace(f'downloading transactions for {cur_mon}/{cur_year}')
        mint = mintapi.Mint(email, password, headless=True, mfa_method='sms')
        if refresh_acct:
            mint_log.trace('Refreshing account')
            mint.initiate_account_refresh()

        df = mint.get_detailed_transactions(start_date=start_date, include_investment=False) 
        
        df['transaction_type'] = df['isDebit'].map(lambda x: 'debit' if x else 'credit')
        df = df[['odate', 'mmerchant', 'omerchant', 'amount', 'transaction_type', 
                 'mcategory', 'account', 'labels', 'note']]
        df.columns = ['date', 'description', 'original_description', 'amount', 'transaction_type',
                      'category', 'account_name', 'labels', 'notes']
        mint_log.trace(f'Saving data to file at {mint_data_path}')
        df.to_json(mint_data_path)
        
    else:
        mint_log.trace(f'Ising local transactions for {cur_mon}/{cur_year} from file at {mint_data_path}')
        df = pd.read_json(mint_data_path)
        
    df['hash'] = df.apply(hash_row, axis=1)
    df['category'] = df['category'].map(lambda x: x.lower())

    df['spent'] = df['amount']
    cur_df = df[df.apply(lambda x: filter_by_month(x, cur_mon, cur_year), axis=1)].copy()
    cur_df['month'] = cur_mon
    cur_df = cur_df.apply(update_categories, axis=1)
    mint_log.info(f'DataFrame created with {len(df)} records.')
    return cur_df[['date',
                     'description',
                     'original_description',
                     'amount',
                     'transaction_type',
                     'category',
                     'account_name',
                     'labels',
                     'notes',
                     'hash',
                     'spent',
                     'month',
                     'm_category']]

def update_categories(row):
    if row.hash in hash_category:
        row['m_category'] = hash_category[row.hash]
        
    elif row.original_description.startswith('DELOITTE PAYMENTS'):
        row['m_category'] = 'OTHER | DAN WORK EXPENSES'
        
    elif row.original_description.startswith('BILL PAY Millpond'):
        row['m_category'] = 'OTHER | CONDO'
        
    elif row.account_name in mapped_account:
        row['m_category'] = mapped_account[row.account_name]        
        
    elif row.original_description in desc_category:
        row['m_category'] = desc_category[row.original_description]
        
    elif row.description in desc_category:
        row['m_category'] = desc_category[row.description]
        
    elif row.category in mapped_category:
        row['m_category'] = mapped_category[row.category]
        
    elif row.original_description[:11] in first_11:
        row.m_category = first_11[row.original_description[:11]]
        
    else:
        row['m_category'] = '_UNMAPPED | {}'.format(row.category)

    return row

 