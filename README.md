# Don't know? Ask Jim

AskJim an all-knowing creature. You can ask (almost) any question and he will answer with source.

## Requirements
- Python 3.12
- Jupyter Notebook or JupyterLab
- Have [ollama](https://ollama.com) installed
- Nvidia GPU is heavily prefered (as everything is runned locally)

## Quick start
Create a virtual environment(optional) and install required library
```sh
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
And install llama3.2:3b if you don't have it install already
```sh
ollama pull llama3.2:3b
```
Next, create your .env file example as follow (.env.example):
```
CROSSREF_EMAIL=your-email@example.com
SCOPUS_DATA_PATH=data/scopus_data/
SQLITE_DB_PATH=data/extracted/paper_data.db
DELIMITER=+
```
Download the data and model from [here](https://drive.google.com/drive/folders/1ixVU1ppU8cEqo1MPZhWjdbu2--qASPCO?usp=sharing) and put the files in the project directory

To ask Jim, enter streamlit_visual directory and run askjim.py
```sh
cd streamlit_visuals
streamlit run askjim.py
```

## Project Structure
Each directory contain each module of the project inclduing
- `data_preparation` contain Data Extraction, Preparation and Exploratory Data Analysis
- `model_creation` contain creating embedding of FAISS and clustering topics
- `streamlit_visual` askjim and papers cluster topic visualization
