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


def update_budget(month, budget_file):
    summary_df, trans_df = load_budget_workbook(
        filename=f"{budget_file} Monthly budget", month=month
    )

    cur_df = download_detailed_transactions(month=month, use_local=False)

    new_trans_df = identify_new_txns(cur_df, trans_df, summary_df)
    new_trans_df = convert_txn_headers(new_trans_df)
    new_df = combine_transactions(new_trans_df, trans_df)
    save_transactions(new_df, filename=f"{budget_file} Monthly budget", month=month)

    summary_df, trans_df = load_budget_workbook(
        filename=f"{budget_file} Monthly budget", month=month
    )
    return summary_df, trans_df


if (
    __name__ == "__main__"
):  # TODO Update craft_email.py to include info on NEW TRANSACTIONS and assignments. Also include any budget items NEGATIVE and LIST TOP 5 txns!!
    # month = '2018-10'
    # budget_file = '2018-2019'
    # summary_df, trans_df = update_budget(month, budget_file)
    df = get_summary_df()
    msg = draft_message(df)
    print(msg)
    send_email(msg)
