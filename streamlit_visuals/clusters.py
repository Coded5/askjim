import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data() -> pd.DataFrame:
    cluster_label = pd.read_csv("../data/processed_data/cluster_clear_labels.csv", index_col=0)
    scopus = pd.read_csv('../data/processed_data/scopus_data_cleansed_clusters.csv')
    
    #merge
    scopus = scopus.merge(cluster_label, left_on='cluster', right_index=True, how='left')
    return scopus

scopus = load_data()

#plot clusters with labels
fig = px.scatter(
    scopus, 
    x='x', 
    y='y',
    hover_name='title', # Show title on hover
    hover_data={'x': False, 'y': False, 'doi': True, 'clear_label': True},
    title="Semantic Clusters of Research Papers with Labels",
    color='clear_label',
    opacity=0.5
)

fig.update_layout(
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
)

st.set_page_config(page_title="Clustered Map of Science", layout="wide")
st.title("🗺️ The Clustered Map of Engineering Science")
st.plotly_chart(fig, use_container_width=True)

