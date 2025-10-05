import pandas as pd




def _parse_mdy_mixed(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip().replace({"": pd.NA, "NaN": pd.NA, "nan": pd.NA})
    # pass 1: mm/dd/YYYY
    out = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")
    # pass 2: mm/dd/YY
    m = out.isna()
    if m.any():
        out.loc[m] = pd.to_datetime(s[m], format="%m/%d/%y", errors="coerce")
    return out
