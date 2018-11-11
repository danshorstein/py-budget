import sys
import re
import os

import logbook
from logbook import StreamHandler, TimedRotatingFileHandler

from services.budget_tools import (
    load_budget_workbook,
    save_transactions,
    identify_new_txns,
    convert_txn_headers,
    combine_transactions,
)
from services.mint_tools import download_detailed_transactions
from services.craft_email import get_summary_df, draft_message
from services.send_email import send_email
from email_attempt import draft_html_message

base_folder = os.path.dirname(__file__)

app_log = logbook.Logger('App')

def init_logging(filename=None):
    level = logbook.TRACE

    if filename:
        logbook.TimedRotatingFileHandler(filename, level=level).push_application()
    else:
        logbook.StreamHandler(sys.stdout, level=level).push_application()

    msg = 'Logging initialized; level: {}; mode: {}'.format(
        level,
        'stdout mode' if not filename else f'file mode: {filename}'
    )
    logger = logbook.Logger('Startup')
    logger.notice(msg)


def update_budget(month, budget_file):
    app_log.trace(f'Starting update_budget with month={month} and budget_file={budget_file}')

    if not re.match(r'\d{4}-\d{2}', month):
        msg = f'Input month must be a string in format "YYYY-MM". Value provided was {month}'
        app_log.error(msg)
        raise ValueError(msg)

    summary_df, trans_df = load_budget_workbook(
        filename=f"{budget_file} Monthly budget", month=month
    )

    cur_df = download_detailed_transactions(month=month, use_local=False)

    new_trans_df = identify_new_txns(cur_df, trans_df, summary_df)
    new_trans_df = convert_txn_headers(new_trans_df)
    new_df = combine_transactions(new_trans_df, trans_df)
    save_transactions(new_df, filename=f"{budget_file} Monthly budget", month=month)

    app_log.trace('Loading updated budget workbook to draft email!')

    summary_df, trans_df = load_budget_workbook(
        filename=f"{budget_file} Monthly budget", month=month
    )
    return summary_df, trans_df


if (
    __name__ == "__main__"
):  # TODO Update craft_email.py to include info on NEW TRANSACTIONS and assignments. Also include any budget items NEGATIVE and LIST TOP 5 txns!!
    init_logging(os.path.join(base_folder, 'logs/log_file.log'))
    month = '2018-11'
    budget_file = '2018-2019'
    update_budget(month, budget_file)
    send_email(draft_html_message(month, budget_file))

    # init_logging()
    # update_budget('hi', 'yo')
    # quit(0)
    # init_logging()
    # df = get_summary_df()
    # msg = draft_message(df)
    # print(msg)
    # send_email(msg)
