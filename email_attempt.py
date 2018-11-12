from datetime import date
import os

from jinja2 import FileSystemLoader, Environment

from services.budget_tools import load_budget_workbook
from services.send_email import send_email
from services.craft_email import get_summary_df


base_folder = os.path.dirname(__file__)

def draft_html_message(month, summary_df=None, trans_df=None):

    y, m = month.split('-')

    month = date(int(y), int(m), 1)

    env = Environment(
        loader = FileSystemLoader(os.path.join(base_folder, 'templates'))
    )
    
    template = env.get_template('email_template.html')
    
    df = get_summary_df('2018-2019', '2018-11')
    df.index = df.Title

    html_message = template.render(
        name='Shorstein',
        date=date.today().strftime('%B %Y'),
        main_message_header='Budget Highlights',
        main_message='Remaining balances in restaurants and groceries',
        budget_categories=[{'name': 'FOOD | GROCERIES', 'amt': df.loc['FOOD | GROCERIES',:].Diff},
                           {'name': 'FOOD | RESTAURANTS', 'amt':  df.loc['FOOD | RESTAURANTS',:].Diff}],
        current_cash_balance=...,
        current_credit_card_balance=...,
        remaining_restaurant_budget=...,
        remaining_grocery_budget=...,
        number_of_new_txns=...,
        new_txns_list=...,
        numer_of_amazon_txns=...,
        amount_of_amazon_txns=...
        )

    return html_message

if __name__ == '__main__':
    from budget import init_logging
    init_logging('logs/test_email.log')
    summary_df = get_summary_df('2018-2019', '2018-11')

    msg = draft_html_message('2018-11')
    send_email(msg)