import pandas as pd


def run_checks(balance_sheet,trial_balance):
    ### Balance Sheet Check

    bs = balance_sheet.copy()

    asset_accounts = ['Cash', 'Accounts Receivable', 'PP&E']
    liability_accounts = ['Unearned Rent', 'Credit Card']
    equity_accounts = ['capital-pt', 'capital-rc', 'Suspense', 'Retained Earnings','Cash Transfers']

    assets = bs[bs['account'].isin(asset_accounts)].copy()
    assets.loc[:, 'Amount'] = assets['Amount'].apply(lambda x: abs(x))
    total_assets = assets['Amount'].sum()

    liabilities = bs[bs['account'].isin(liability_accounts)].copy()
    liabilities.loc[:, 'Amount'] = liabilities['Amount'].apply(lambda x: abs(x))
    total_liabilities = liabilities['Amount'].sum()

    equity = bs[bs['account'].isin(equity_accounts)].copy()
    equity.loc[:, 'Amount'] = equity['Amount'].apply(lambda x: abs(x))
    total_equity = equity['Amount'].sum()

    # Check balance
    balanced = round(total_assets, 2) == round(total_liabilities + total_equity, 2)

    print(f"Assets total: {total_assets:,.2f}")
    print(f"Liabilities + Equity total: {(total_liabilities + total_equity):,.2f}")
    print("✅ Balance Sheet is balanced" if balanced else "❌ Not balanced")
    print()



    #### Trial Balance Net D/C Check
    tb = trial_balance.copy()


    threshold = .02

    total_diff = tb['Net D/C'].sum()

    if abs(total_diff) <= threshold:
        print(f"✅ Trial Balance is balanced (Difference: {total_diff:,.2f})")
    else:
        print(f"❌ Trial Balance not balanced — off by {total_diff:,.2f}")
