import pandas as pd
from je_tran import create_journal_from_transactions
from income_statement import create_income_statement
from operating_cf import create_cf_statement
from load_excel import load_tran_data, load_yardi_data, load_cash_balances
from yardi_norm import normalize_raw_yardi
from load_s3 import load_S3_data
from load_s3_Yardi import load_S3_yardi
from load_balances import write_period_bal, normalize_balances
from pull_balances import read_beg_balances
from dateutil.relativedelta import relativedelta

tran_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/transactions/8.25_transactions.xlsx'
yardi_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/transactions/8.25_yardi_tran.xlsx'
cash_bal_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/cash_balances/cash_balances.xlsx'

from_period = '08/2025'
to_period = '08/2025'

run_monthly_load_balance = False


# Combine tenant and expense entries into one journal
def create_general_journal(yardi_df, transactions_df):
    journal_transactions = create_journal_from_transactions(transactions_df)
    journal_transactions["gl_code"] = journal_transactions["gl_code"].astype(int)
    journal_transactions['period'] = (
        pd.to_datetime(journal_transactions['date'], errors='coerce')
            .dt.strftime('%m/%Y')
    )
    journal_transactions.to_excel('/Users/mattray/Desktop/GV Accouting/Outputs/Test/yardi_journal_tran.xlsx')

    yardi_entries = normalize_raw_yardi(yardi_df)
    df = pd.concat([yardi_entries, journal_transactions], ignore_index=True)
    df = df.drop(['tenant'],axis = 1)
    df.to_excel('/Users/mattray/Desktop/GV Accouting/Outputs/Test/df_concat.xlsx')

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


    beg = beg_bal.rename(columns={'ending_balance': 'beginning_balance',
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

# Save to Excel
def save_to_excel(general_journal, gl_ledgers, trial_balance, income_statement, operating_cf, output_file):
    with pd.ExcelWriter(output_file) as writer:
        general_journal.to_excel(writer, sheet_name='General Journal', index=False)
        gl_ledgers.to_excel(writer, sheet_name='GL Ledgers', index=False)
        trial_balance.to_excel(writer, sheet_name='Trial Balance', index=False)
        income_statement.to_excel(writer,sheet_name='Income Statement',index=False)
        operating_cf.to_excel(writer,sheet_name='Operating CF', index=False)

# Run full accounting pipeline
def run_accounting_pipeline(excel_input, yardi_input, output_file):
    beg_bal = read_beg_balances(period = from_period)
    transactions_df = load_S3_data(periods= ['08/2025'])
    #transactions_df = load_tran_data(excel_input,from_period,to_period)
    yardi_df = load_S3_yardi(periods= ['08/2025'])
    #yardi_df = load_yardi_data(yardi_input)
    beg_cash_bal = load_cash_balances(cash_bal_filepath,from_period)
    general_journal = create_general_journal(yardi_df, transactions_df)
    gl_ledgers = create_gl_ledgers(general_journal)
    trial_balance = create_trial_balance(general_journal,beg_bal,from_period,to_period)
    income_statement = create_income_statement(trial_balance)
    operating_cf = create_cf_statement(trial_balance=trial_balance,income_statement=income_statement,cash_balances=beg_cash_bal)
    save_to_excel(general_journal, gl_ledgers, trial_balance, income_statement, operating_cf, output_file)

    return trial_balance


# Example run:
tb = run_accounting_pipeline(excel_input = tran_filepath, yardi_input= yardi_filepath,output_file = '/Users/mattray/Desktop/GV Accouting/Outputs/accounting_output_5.xlsx')

if run_monthly_load_balance == True:
    bal_df = normalize_balances(trial_balance=tb)
    write_period_bal(period=to_period, tb =bal_df)
else:
    pass
