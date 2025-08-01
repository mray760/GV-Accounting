import pandas as pd

filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Test/combined_input_with_expenses.xlsx'

# Define GL Codes
GL_CODE_MAP = {
    'Cash': '15110',
    'Storage Revenue': '15120',
    'Accounts Receivable': '16110',
    'Expenses': '17105',
    'Unearned Rent': '16578'
}

# Load both sheets from Excel
def load_data(excel_file):
    charges_df = pd.read_excel(excel_file, sheet_name='charges_and_payments', parse_dates=['date'])
    expenses_df = pd.read_excel(excel_file, sheet_name='transactions', parse_dates=['date'])
    return charges_df, expenses_df

# Generate General Journal entries from charges/payments
def create_journal_from_charges(transactions):
    journal = []

    for _, row in transactions.iterrows():
        # Revenue from charge
        if row['charge'] > 0:
            journal.append({
                'date': row['date'],
                'account': 'Storage Revenue',
                'gl_code': GL_CODE_MAP['Storage Revenue'],
                'debit': 0,
                'credit': row['charge'],
                'description': f"Charge - {row['description']}",
                'tenant': row['tenant_name']
            })

        # Cash payment
        if row['cash_payment'] > 0:
            journal.append({
                'date': row['date'],
                'account': 'Cash',
                'gl_code': GL_CODE_MAP['Cash'],
                'debit': row['cash_payment'],
                'credit': 0,
                'description': f"Cash - {row['description']}",
                'tenant': row['tenant_name']
            })

        # A/R for unpaid charge
        if row['outstanding_charge'] > 0:
            journal.append({
                'date': row['date'],
                'account': 'Accounts Receivable',
                'gl_code': GL_CODE_MAP['Accounts Receivable'],
                'debit': row['outstanding_charge'],
                'credit': 0,
                'description': f"A/R - {row['description']}",
                'tenant': row['tenant_name']
            })

        # Advance payment only
        if row['charge'] == 0 and row['cash_payment'] > 0:
            journal.append({
                'date': row['date'],
                'account': 'Unearned Rent',
                'gl_code': GL_CODE_MAP['Unearned Rent'],
                'debit': 0,
                'credit': row['cash_payment'],
                'description': f"Advance Payment - {row['description']}",
                'tenant': row['tenant_name']
            })

    return pd.DataFrame(journal)

# Generate journal from expenses
def create_journal_from_expenses(expenses):
    journal = []

    for _, row in expenses.iterrows():
        # Debit: Expense
        journal.append({
            'date': row['date'],
            'account': row['account'],
            'gl_code': row['gl_code'],
            'debit': row['amount'],
            'credit': 0,
            'description': f"Expense - {row['description']}",
            'tenant': None
        })
        # Credit: Cash
        journal.append({
            'date': row['date'],
            'account': 'Cash',
            'gl_code': GL_CODE_MAP['Cash'],
            'debit': 0,
            'credit': row['amount'],
            'description': f"Expense Payment - {row['description']}",
            'tenant': None
        })

    return pd.DataFrame(journal)

# Combine tenant and expense entries into one journal
def create_general_journal(charges_df, expenses_df):
    journal_charges = create_journal_from_charges(charges_df)
    journal_expenses = create_journal_from_expenses(expenses_df)
    return pd.concat([journal_charges, journal_expenses], ignore_index=True).sort_values(by='date')

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
    tb['balance'] = tb['total_debit'] - tb['total_credit']
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
    charges_df, expenses_df = load_data(excel_input)
    general_journal = create_general_journal(charges_df, expenses_df)
    tenant_ledgers = create_tenant_ledgers(charges_df)
    gl_ledgers = create_gl_ledgers(general_journal)
    trial_balance = create_trial_balance(general_journal)
    save_to_excel(general_journal, tenant_ledgers, gl_ledgers, trial_balance, output_file)

# Example run:
run_accounting_pipeline(excel_input = filepath,output_file = '/Users/mattray/Desktop/GV Accouting/Outputs/accounting_output_5.xlsx')
