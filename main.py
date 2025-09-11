import pandas as pd
from je_tran import create_journal_from_transactions
from income_statement import create_income_statement
from load_excel import load_tran_data, load_yardi_data
from yardi_norm import normalize_raw_yardi

tran_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/gv_tran_prod.xlsx'
yardi_filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Test/yardi_tran_test.xlsx'



# Combine tenant and expense entries into one journal
def create_general_journal(yardi_df, transactions_df):
    journal_transactions = create_journal_from_transactions(transactions_df)
    journal_transactions["gl_code"] = journal_transactions["gl_code"].astype(int)
    yardi_entries = normalize_raw_yardi(yardi_df)
    df = pd.concat([yardi_entries, journal_transactions], ignore_index=True)
    df = df.drop(['date','tenant'],axis = 1)
    return df


# GL Ledger
def create_gl_ledgers(general_journal):
    return general_journal

# Trial Balance
def create_trial_balance(general_journal):
    tb = general_journal.groupby(['gl_code','account']).agg(
        total_debit=('debit', 'sum'),
        total_credit=('credit', 'sum')
    ).reset_index()
    tb['Net D/C'] = tb['total_debit'] - tb['total_credit']
    return tb

# Save to Excel
def save_to_excel(general_journal, gl_ledgers, trial_balance, income_statement, output_file):
    with pd.ExcelWriter(output_file) as writer:
        general_journal.to_excel(writer, sheet_name='General Journal', index=False)
        gl_ledgers.to_excel(writer, sheet_name='GL Ledgers', index=False)
        trial_balance.to_excel(writer, sheet_name='Trial Balance', index=False)
        income_statement.to_excel(writer,sheet_name='Income Statement',index=False)

# Run full accounting pipeline
def run_accounting_pipeline(excel_input, yardi_input, output_file):
    transactions_df = load_tran_data(excel_input)
    yardi_df = load_yardi_data(yardi_input)
    general_journal = create_general_journal(yardi_df, transactions_df)
    gl_ledgers = create_gl_ledgers(general_journal)
    trial_balance = create_trial_balance(general_journal)
    income_statement = create_income_statement(trial_balance)
    save_to_excel(general_journal, gl_ledgers, trial_balance, income_statement, output_file)

# Example run:
run_accounting_pipeline(excel_input = tran_filepath, yardi_input= yardi_filepath,output_file = '/Users/mattray/Desktop/GV Accouting/Outputs/accounting_output_5.xlsx')
