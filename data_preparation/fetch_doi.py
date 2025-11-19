import sqlite3
import pandas as pd
import requests
import time
import os

from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("CROSSREF_EMAIL", "")
DELAY = 1
CROSSREF_URL = "https://api.crossref.org/works"

def fetch_doi_crossref(title) -> str | None: 
    params = {
        "query.bibliographic": title,
        "rows": 1,
        "select": "DOI,title"
    } 

    if EMAIL:
        headers = {
                "User-Agent": f"DSProject/1.0 (mailto:{EMAIL})"
        }
    else:
        headers = {}

    try:
        res = requests.get(CROSSREF_URL, params=params, headers=headers)
        if res.status_code != 200:
            print("Something went wrong with:", title)
            return None

        data = res.json()
        items = data.get("message", {}).get("items", [])
        if len(items) == 0:
            print("No paper found with title:", title)
            return None
        
        return items[0].get("DOI")
    except:
        print("Something went wrong with:", title)
        return None

con = sqlite3.connect('../data/extracted/paper_data.db')
df = pd.read_sql_query("SELECT * FROM paper_data;", con)
con.close()

missing = df['doi'].isna() | df['doi'].eq('')
missing_count = missing.sum()

found, progress = 0, 0

print(f"Found {missing_count} missing DOIs")
for index, row in df[missing].iterrows():
    title = row['title']
    doi = fetch_doi_crossref(title)

    progress += 1
    if doi is not None:
        df.at[index, 'doi'] = doi
        found += 1
        print(f"({progress}/{missing_count}) Found DOI for {title}")
    else:
        print(f"({progress}/{missing_count}) Not found DOI for {title}")
    time.sleep(DELAY)


df.to_csv("../data/processed_data/scopus_data_doi.csv")
