import pandas as pd


def create_bs_statement(trial_balance,beg_re,income_statement):
    if beg_re is None or beg_re.empty or beg_re.isna().all().all():
        beg_re = pd.DataFrame({
            'Account': ['Retained Earnings'],
            'Amount': [0.0]
        })
    else:
        beg_re = beg_re

    tb = trial_balance

    current_ni = income_statement[income_statement['account'] == 'Net Income']
    concat = pd.concat([beg_re,current_ni])

    #### Calculate Retained Earnings
    total_re = concat['Amount'].sum()
    retained_earnings = pd.DataFrame({'account': 'Retained Earnings','Amount': [float(total_re)]})

    #### Calculate different account types
    asset_accounts = ['Cash','Accounts Receivable', 'PP&E']
    liability_accounts = ['Unearned Rent','Credit Card']
    equity_accounts = ['capital-pt','capital-rc','Suspense','Retained Earnings']


    assets = tb[tb['account'].isin(asset_accounts)].copy()
    assets.loc[:, 'ending_balance'] = assets['ending_balance'].apply(lambda x: abs(x))
    total_assets = assets['ending_balance'].sum()

    liabilities = tb[tb['account'].isin(liability_accounts)].copy()
    liabilities.loc[:, 'ending_balance'] = liabilities['ending_balance'].apply(lambda x: abs(x))
    total_liabilities = liabilities['ending_balance'].sum()

    equity = tb[tb['account'].isin(equity_accounts)].copy()
    equity.loc[:, 'ending_balance'] = equity['ending_balance'].apply(lambda x: abs(x))
    total_equity = equity['ending_balance'].sum()


    #### create and organize dataframes
    asset_data = assets[['account', 'ending_balance']].rename(columns={'ending_balance': 'Amount'})
    liability_data = liabilities[['account', 'ending_balance']].rename(columns={'ending_balance': 'Amount'})
    equity_data = equity[['account', 'ending_balance']].rename(columns={'ending_balance': 'Amount'})

    ### concat with Retained Earnings

    equity_all = pd.concat([equity_data,retained_earnings])
    equity_all = equity_all.reset_index(drop=True)



    num_empty_rows = 4
    empty_rows = pd.DataFrame(
        {'account': [None] * num_empty_rows, 'Amount': [None] * num_empty_rows, 'Type': [None] * num_empty_rows})




    def add_type_column(df, label):
        df = df.copy()
        df.insert(0, 'type', '')  # Add empty column on far left
        df.loc[df.index[0], 'type'] = label  # Assign label to top row only
        return df

    # Apply to each section
    asset_data = add_type_column(asset_data, 'Assets')
    liability_data = add_type_column(liability_data, 'Liabilities')
    equity_all = add_type_column(equity_all, 'Equity')


    merged_df = pd.concat([asset_data,empty_rows,liability_data,empty_rows,equity_all,empty_rows])

    return merged_df

