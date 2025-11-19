import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer

import ollama

import faiss

@st.cache_data
def load_index():
    return faiss.read_index("../models/faiss_scopus_index.idx")

@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed_data/scopus_data_doi_cleaned_with_projections.csv")
    return df

@st.cache_data
def load_model():
    model = SentenceTransformer('all-mpnet-base-v2')
    return model

def ask_ollama(sources, question):
    prompt = "You are Jim, an AI research assistant. Use the following sources to answer the question.\n\n"
    for i, source in enumerate(sources):
        prompt += f"Source {i+1}:\nTitle: {source['title']}\nAbstract: {source['abstract']}\n\n"
    prompt += f"Question: {question}\n\nAnswer the question based on the above sources. If the information is not available, respond with 'Information not available in the provided sources.'"

    response = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

model = load_model()
index = load_index()
df = load_data()

st.set_page_config(page_title="AskJim", layout="wide")
st.title("AskJim: The All-knowing")

user_query = st.text_input("Enter your research question or topic:", "")
ask = st.button("Ask Jim")



if ask and user_query:
    with st.spinner("Jim is thinking..."):
        query_vector = model.encode([user_query]).astype('float32')
        k = 5  # number of nearest neighbors
        distances, indices = index.search(query_vector, k)

        sources = []

        for rank, idx in enumerate(indices[0]):
            paper = df.iloc[idx]
            sources.append({
                "title": paper['title'],
                "DOI": paper['doi'],
                "abstract": paper['abstract']
            })

        answer = ask_ollama(sources, user_query)
        st.subheader("Jim's Answer:")
        st.markdown(answer)

        st.subheader("Sources")
        for i, source in enumerate(sources):
            st.markdown(f"**Source {i+1}: {source['title']}**")
            # st.markdown(f"- DOI: {source['DOI']}")
            #DOI link
            st.markdown(f"- https://doi.org/{source['DOI']}")

            st.markdown(f"- Abstract: {source['abstract']}")
            st.markdown("---")
