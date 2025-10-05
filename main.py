import pandas as pd
from je_tran import create_journal_from_transactions
from income_statement import create_income_statement
from operating_cf import create_cf_statement
from yardi_norm import normalize_raw_yardi
from Pull_S3_Bank import load_S3_data
from Pull_S3_Yardi import load_S3_yardi
from load_balances import write_period_bal, normalize_balances
from pull_balances import read_beg_balances
from pop_ups import confirm_run
from to_excel import save_to_excel


###Parameters
run_monthly_load_balance = False
from_period = '09/2025'
to_period = '09/2025'


### caclulate periods
all_periods = pd.date_range("2025-01-01", "2025-12-01", freq="MS").strftime("%m/%Y").tolist()
start, end = from_period, to_period
selected_periods = all_periods[all_periods.index(start): all_periods.index(end)+1]

print("Selected periods:", selected_periods)





# Combine tenant and expense entries into one journal
def create_general_journal(yardi_df, transactions_df):
    journal_transactions = create_journal_from_transactions(transactions_df)
    journal_transactions["gl_code"] = journal_transactions["gl_code"].astype(int)
    journal_transactions['period'] = (
        pd.to_datetime(journal_transactions['date'], errors='coerce')
            .dt.strftime('%m/%Y')
    )

    yardi_entries = normalize_raw_yardi(yardi_df)
    df = pd.concat([yardi_entries, journal_transactions], ignore_index=True)
    df = df.drop(['tenant'],axis = 1)

    return df


# GL Ledger
def create_gl_ledgers(general_journal):
    return general_journal

# Trial Balance
def create_trial_balance(general_journal,beg_bal,from_period,to_period):
    tb = general_journal.groupby(['gl_code','account']).agg(
        total_debit=('debit', 'sum'),
        total_credit=('credit', 'sum')
    ).reset_index()
    tb['Net D/C'] = tb['total_debit'] - tb['total_credit']


    beg = beg_bal.rename(columns={'balance': 'beginning_balance',
                                  'period': '_beg_period'})

    tb = tb.merge(beg[['gl_code', 'account', 'beginning_balance']],
                  on=['gl_code', 'account'], how='left')

    tb['beginning_balance'] = tb['beginning_balance'].fillna(0.0)

    # --- compute ending balances
    tb['ending_balance'] = tb['beginning_balance'] + tb['Net D/C']
    tb['from_period'] = from_period
    tb['to_period'] = to_period

    tb = tb[['from_period','to_period','gl_code','account','total_debit','total_credit', 'beginning_balance','Net D/C', 'ending_balance']]


    return tb


# Run full accounting pipeline
def run_accounting_pipeline(output_file):
    beg_bal = read_beg_balances(period = from_period)
    transactions_df = load_S3_data(periods= selected_periods)
    yardi_df = load_S3_yardi(periods= selected_periods)
    general_journal = create_general_journal(yardi_df, transactions_df)
    trial_balance = create_trial_balance(general_journal,beg_bal,from_period,to_period)
    income_statement = create_income_statement(trial_balance)
    operating_cf = create_cf_statement(trial_balance=trial_balance,income_statement=income_statement,cash_balances=beg_bal,general_journal=general_journal)
    save_to_excel(general_journal,trial_balance, income_statement, operating_cf, output_file)

    return trial_balance



excel_period = to_period.replace('/', '.')

tb = run_accounting_pipeline(output_file = fr'/Users/mattray/Desktop/GV Accouting/Outputs/accounting_{excel_period}.xlsx')

if run_monthly_load_balance == True:
    if confirm_run():
        print("Running monthly balances...")
        bal_df = normalize_balances(trial_balance=tb)
        write_period_bal(period=to_period, tb =bal_df)
    else:
        print("cancelled")



