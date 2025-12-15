from __future__ import annotations
import pandas as pd

def compute_food_desert_scores(usda_df: pd.DataFrame) -> pd.DataFrame:
    df = usda_df.copy()

    geoid_col = None
    for c in ["CensusTract", "GEOID", "geoid", "TRACTID", "CensusTractId"]:
        if c in df.columns:
            geoid_col = c
            break
    if geoid_col is None:
        raise KeyError("Could not find a GEOID/CensusTract column in USDA food access CSV.")

    df["GEOID"] = df[geoid_col].astype(str).str.zfill(11)

    candidate_flags = [c for c in df.columns if "LILA" in c.upper() or "LOWACCESS" in c.upper()]
    if not candidate_flags:
        df["desert_severity"] = 0
        df["is_food_desert"] = False
        return df[["GEOID", "is_food_desert", "desert_severity"]]

    tmp = df[candidate_flags].copy()
    for c in candidate_flags:
        tmp[c] = pd.to_numeric(tmp[c], errors="coerce").fillna(0)

    df["desert_severity"] = (tmp > 0).sum(axis=1).astype(int)
    df["is_food_desert"] = df["desert_severity"] > 0
    return df[["GEOID", "is_food_desert", "desert_severity"]]
