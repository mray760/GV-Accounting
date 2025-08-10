import pandas as pd
from je_charge import create_journal_from_charges
from je_tran import create_journal_from_transactions

filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Production/gv_tran_prod.xlsx'


# Load both sheets from Excel
def load_data(excel_file):
    charges_df = pd.read_excel(excel_file, sheet_name='charges_and_payments', parse_dates=['date'])
    transactions_df = pd.read_excel(excel_file, sheet_name='transactions', parse_dates=['date'])
    transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce')
    charges_df['date'] = pd.to_datetime(charges_df['date'], errors='coerce')
    return charges_df, transactions_df


# Combine tenant and expense entries into one journal
def create_general_journal(charges_df, transactions_df):
    journal_charges = create_journal_from_charges(charges_df)
    journal_transactions = create_journal_from_transactions(transactions_df)
    return pd.concat([journal_charges, journal_transactions], ignore_index=True).sort_values(by='date')

# Create tenant ledgers
def create_tenant_ledgers(transactions):
    ledger = []

    for _, row in transactions.iterrows():
        ledger.append({
            'tenant': row['tenant_name'],
            'unit_number': row['unit_number'],
            'date': row['date'],
            'description': row['description'],
            'charge': row['charge'],
            'payment': row['cash_payment']
        })

    df = pd.DataFrame(ledger)
    df['balance'] = df.groupby('tenant')[['charge', 'payment']].cumsum().eval('charge - payment')
    return df

# GL Ledger
def create_gl_ledgers(general_journal):
    return general_journal.sort_values(by=['gl_code', 'date'])

# Trial Balance
def create_trial_balance(general_journal):
    tb = general_journal.groupby(['gl_code', 'account']).agg(
        total_debit=('debit', 'sum'),
        total_credit=('credit', 'sum')
    ).reset_index()
    tb['Net D/C'] = tb['total_debit'] - tb['total_credit']
    return tb

# Save to Excel
def save_to_excel(general_journal, tenant_ledgers, gl_ledgers, trial_balance, output_file):
    with pd.ExcelWriter(output_file) as writer:
        general_journal.to_excel(writer, sheet_name='General Journal', index=False)
        tenant_ledgers.to_excel(writer, sheet_name='Tenant Ledgers', index=False)
        gl_ledgers.to_excel(writer, sheet_name='GL Ledgers', index=False)
        trial_balance.to_excel(writer, sheet_name='Trial Balance', index=False)

# Run full accounting pipeline
def run_accounting_pipeline(excel_input, output_file):
    charges_df, transactions_df = load_data(excel_input)
    general_journal = create_general_journal(charges_df, transactions_df)
    tenant_ledgers = create_tenant_ledgers(charges_df)
    gl_ledgers = create_gl_ledgers(general_journal)
    trial_balance = create_trial_balance(general_journal)
    save_to_excel(general_journal, tenant_ledgers, gl_ledgers, trial_balance, output_file)

# Example run:
run_accounting_pipeline(excel_input = filepath,output_file = '/Users/mattray/Desktop/GV Accouting/Outputs/accounting_output_5.xlsx')
