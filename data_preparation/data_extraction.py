import json
import os
import sqlite3
from dotenv import load_dotenv, find_dotenv

load_dotenv()

def extract_data(data_path):
    with(open(data_path, 'r') as file):
        data = json.load(file)

    paper_data = data['abstracts-retrieval-response']

    title = paper_data['coredata'].get('dc:title', '')
    description = paper_data['coredata'].get('dc:description', '')
    coverdate = paper_data['coredata'].get('prism:coverDate', '')
    publication_name = paper_data['coredata'].get('prism:publicationName', '')
    citation_count = paper_data['coredata'].get('citedby-count', '')

    subject_areas = []
    for subject in paper_data['subject-areas']['subject-area']:
        subject_areas.append(subject['$'])


    author_names = []
    for author in paper_data['authors']['author']:
        author_names.append(author['ce:indexed-name'])

    affiliations = []

    if isinstance(paper_data['affiliation'], dict):
        # paper_data['affiliation'] = [paper_data['affiliation']['affilname']]
        affiliations.append(paper_data['affiliation']['affilname'])
    else:
        for affiliation in paper_data['affiliation']:
            affiliations.append(affiliation['affilname'])

    countries = set()

    if isinstance(paper_data['affiliation'], dict):
        country = paper_data['affiliation'].get('affiliation-country', '')
        if country:
            countries.add(country)
    else:
        for affiliation in paper_data['affiliation']:
            country = affiliation.get('affiliation-country', '')
            if country:
                countries.add(country)

    doi = paper_data['coredata'].get('prism:doi', '')

    return {
        "title": title,
        "description": description,
        "coverdate": coverdate,
        "publication_name": publication_name,
        "citation_count": citation_count,
        "subject_areas": subject_areas,
        "author_names": author_names,
        "affiliations": affiliations,
        "countries": list(countries),
        "doi": doi
    }

COLUMNS = ['title', 'description', 'year', 'coverdate', 'publication_name', 'citation_count', 'subject_areas', 'author_names', 'affiliations', 'countries', 'doi', 'file_name']

SCHEMA = f'''
CREATE TABLE paper_data (
        title VARCHAR(300),
        description VARCHAR(10000),
        year INT,
        coverdate VARCHAR(10),
        publication_name VARCHAR(300),
        citation_count INT,
        subject_areas VARCHAR(2000),
        author_names VARCHAR(5000),
        affiliations VARCHAR(10000),
        countries VARCHAR(1000),
        file_name VARCHAR(50),
        doi varchar(30))
'''

def main():
    root = find_dotenv()

    db_path = os.getenv("SQLITE_DB_PATH", "")

    if not db_path:
        print("Please set SQLITE_DB_PATH in your .env file")
        return

    db_path = os.path.join(os.path.dirname(root), db_path)

    con = sqlite3.connect(db_path)

    #Check if table doesn't exist then create it
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paper_data';")
    if not cur.fetchone():
        cur.execute(SCHEMA)
        con.commit()
    
    DATA_PATH = os.getenv("SCOPUS_DATA_PATH", "")
    DELIMITER = os.getenv("DATA_DELIMITER", "+")

    data_path = os.path.join(os.path.dirname(root), DATA_PATH)

    print("Starting data extraction... ")
    count = 0
    for year in os.listdir(data_path):
        year_path = os.path.join(data_path, year)
        if not os.path.isdir(year_path):
            continue

        data = []
        for file_name in os.listdir(year_path):
            extract_data_path = os.path.join(year_path, file_name)
            paper_info = extract_data(extract_data_path)
            row = (
                paper_info['title'],
                paper_info['description'],
                year,
                paper_info['coverdate'],
                paper_info['publication_name'],
                str(paper_info['citation_count']),
                DELIMITER.join(paper_info['subject_areas']),
                DELIMITER.join(paper_info['author_names']),
                DELIMITER.join(paper_info['affiliations']),
                DELIMITER.join(paper_info['countries']),
                paper_info['doi'],
                file_name #For debugging purposes
            )
            print(f"{file_name}\tExtracted data for paper:", paper_info['title'])
            count += 1

            data.append(row)
        cur.executemany(f"INSERT INTO paper_data ({', '.join(COLUMNS)}) VALUES ({', '.join(['?']*len(COLUMNS))})", data)
        con.commit()
    con.close()
    print("Data extraction completed. Total papers processed:", count)

if __name__ == '__main__':
    main()
