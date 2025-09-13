import pandas as pd
from je_tran import create_journal_from_transactions
from income_statement import create_income_statement
from operating_cf import create_op_cf
from load_excel import load_tran_data, load_yardi_data
from yardi_norm import normalize_raw_yardi

tran_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/transactions/8.25_transactions.xlsx'
yardi_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/transactions/8.25_yardi_tran.xlsx'
cash_bal_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/cash_balances/cash_balances.xlsx'

from_period = '08-2025'
to_period = '08-2025'

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
def create_trial_balance(general_journal):
    tb = general_journal.groupby(['period','gl_code','account']).agg(
        total_debit=('debit', 'sum'),
        total_credit=('credit', 'sum')
    ).reset_index()
    tb['Net D/C'] = tb['total_debit'] - tb['total_credit']
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
    transactions_df = load_tran_data(excel_input)
    yardi_df = load_yardi_data(yardi_input)
    general_journal = create_general_journal(yardi_df, transactions_df)
    gl_ledgers = create_gl_ledgers(general_journal)
    trial_balance = create_trial_balance(general_journal)
    income_statement = create_income_statement(trial_balance)
    operating_cf = create_op_cf(trial_balance=trial_balance,income_statement=income_statement)
    save_to_excel(general_journal, gl_ledgers, trial_balance, income_statement, operating_cf, output_file)


# Example run:
run_accounting_pipeline(excel_input = tran_filepath, yardi_input= yardi_filepath,output_file = '/Users/mattray/Desktop/GV Accouting/Outputs/accounting_output_5.xlsx')
