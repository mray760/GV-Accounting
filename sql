from sqlalchemy import create_engine, text
from load_data import load_data

filepath = '/Users/mattray/Desktop/GV Accouting/Inputs/Test/gv_tran_test.xlsx'

charges_df, transactions_df = load_data(filepath)

HOST = "database-1.cm3s8qw6myma.us-east-1.rds.amazonaws.com"
PORT = 3306
DB   = "mvsgv"
USER = "mattray760"              # or master user
PWD  = "Uhglbk5478!"

# Basic (no SSL)
engine = create_engine(f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB}",
                       pool_pre_ping=True)


charges_df.to_sql("monthly_balances_test", engine, if_exists="append",
          index=False, chunksize=1000, method="multi")
