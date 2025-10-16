
import s3fs
import pandas as pd

BUCKET = "published-reports"
prefix = 'locked'
fs = s3fs.S3FileSystem()



def publish_reports(general_journal, trial_balance, income_statement, operating_cf, balance_sheet,period):
    period = period.replace("/", ".")

    key = f"{prefix}/period={period}.xlsx"
    s3_uri = f"s3://{BUCKET}/{key}"

    with fs.open(s3_uri, "wb") as f:
        with pd.ExcelWriter(f, engine="xlsxwriter") as writer:
            general_journal.to_excel(writer, sheet_name='General Journal', index=False)
            trial_balance.to_excel(writer, sheet_name='Trial Balance', index=False)
            income_statement.to_excel(writer, sheet_name='Income Statement', index=False)
            balance_sheet.to_excel(writer, sheet_name='Balance Sheet', index=False)
            operating_cf.to_excel(writer, sheet_name='Operating CF', index=False)

            workbook = writer.book
            worksheet = writer.sheets["Trial Balance"]

            for i, col in enumerate(trial_balance.columns):
                max_len = max(
                    trial_balance[col].astype(str).map(len).max() if not trial_balance.empty else 0,
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)

            money_fmt = workbook.add_format({'num_format': '#,##0.00'})
            worksheet.set_column(4, 8, None, money_fmt)

            print("Reports successfully published")
