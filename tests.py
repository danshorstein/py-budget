import pytest
from gspread.exceptions import SpreadsheetNotFound
import pandas as pd

from budget import update_budget
from services.budget_tools import convert_to_float, convert_txn_headers
from services.craft_email import numify
from services.send_email import create_message

def test_update_budget():
    with pytest.raises(ValueError):
        update_budget('12-2015', None)
    
    with pytest.raises(SpreadsheetNotFound):
        update_budget('2015-12', None)

def test_numify():
    assert numify('$5,530') == 5530
    assert numify('hello') == 0

def test_convert_to_float():
    assert convert_to_float('$5,530.50') == 5530.5
    assert convert_to_float('hello') == 'hello'

def test_create_message():
    assert create_message('me', 'you', 'hello', 'hi this is a message!')['raw'].startswith('Q29udGVudC1U')

def test_convert_txn_headers():
    df = pd.DataFrame([[0, 0, 0, 0, 0]], columns=['hash', 'date', 'amount', 'description', 'm_category'])
    assert list(convert_txn_headers(df).columns) == ['Hash', 'Date', 'Amount', 'Description', 'Category']


if __name__ == '__main__':
    update_budget('2015-12', None)