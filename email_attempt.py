from datetime import date

from jinja2 import FileSystemLoader, Environment

from services.send_email import send_email
from budget import init_logging

def draft_html_message(month, summary_df=None, trans_df=None):

    y, m = month.split('-')

    month = date(int(y), int(m), 1)

    env = Environment(
        loader = FileSystemLoader('templates')
    )
    
    template = env.get_template('email_template.html')
    
    html_message = template.render(
        date=date.today().strftime('%B %Y'),
        main_message_header=...,
        main_message=...,
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
    init_logging('logs/test_email.log')
    msg = draft_html_message('2018-11')
    send_email(msg)