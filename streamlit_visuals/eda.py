import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced Scopus Data EDA", layout="wide", page_icon="📊")

@st.cache_data
def load_data():
    df = pd.read_csv('../data/processed_data/scopus_data_doi_cleaned.csv')
    
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['citation_count'] = pd.to_numeric(df['citation_count'], errors='coerce').fillna(0)
    df['date'] = pd.to_datetime(df['coverdate'], errors='coerce')
    df['author_count'] = df['author_names'].fillna('').apply(lambda x: len(x.split('+')) if x else 0)
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'scopus_data_doi_cleaned.csv' not found. Please ensure it is in the same directory.")
    st.stop()

st.sidebar.title("Filters")

min_year = int(df['year'].min())
max_year = int(df['year'].max())
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

df_filtered = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]

all_journals = sorted(df_filtered['publication_name'].dropna().unique())
selected_journals = st.sidebar.multiselect("Filter by Journal (Optional)", all_journals)
if selected_journals:
    df_filtered = df_filtered[df_filtered['publication_name'].isin(selected_journals)]

st.sidebar.markdown("---")
st.sidebar.info(f"Showing **{len(df_filtered)}** papers")

st.title("📊 Advanced Scopus Bibliometric Analysis")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview", 
    "👥 Authors & Affiliations", 
    "📚 Journals & Subjects", 
    "⭐ Citation Analysis",
    "💾 Data Explorer",
    "📈 Clusters Explorer"
])

with tab1:
    st.header("General Overview")
    
    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Publications", f"{len(df_filtered):,}")
    kpi2.metric("Total Citations", f"{int(df_filtered['citation_count'].sum()):,}")
    kpi3.metric("Avg Citations/Paper", f"{df_filtered['citation_count'].mean():.2f}")
    kpi4.metric("Avg Authors/Paper", f"{df_filtered['author_count'].mean():.2f}")
    
    st.markdown("---")
    
    # Publications over time
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Annual Publication Trend")
        pub_year = df_filtered.groupby('year').size().reset_index(name='Count')
        fig_year = px.area(pub_year, x='year', y='Count', markers=True, 
                           title="Number of Publications per Year")
        st.plotly_chart(fig_year, use_container_width=True)
        
    with col2:
        st.subheader("Monthly Publication Trend")
        if df_filtered['date'].notna().any():
            # Group by Month-Year
            pub_month = df_filtered.set_index('date').resample('M').size().reset_index(name='Count')
            fig_month = px.line(pub_month, x='date', y='Count', title="Monthly Publishing Volume")
            st.plotly_chart(fig_month, use_container_width=True)
        else:
            st.info("No detailed date data available for monthly trend.")

with tab2:
    st.header("Authors & Affiliations")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("Top 10 Most Productive Authors")
        authors = df_filtered['author_names'].dropna().str.split('+').explode()
        top_authors = authors.value_counts().head(10).reset_index()
        top_authors.columns = ['Author', 'Publications']
        fig_auth = px.bar(top_authors, x='Publications', y='Author', orientation='h', 
                          color='Publications', color_continuous_scale='Viridis')
        fig_auth.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_auth, use_container_width=True)

    with col_a2:
        st.subheader("Top 10 Affiliated Countries")
        countries = df_filtered['countries'].dropna().str.split('+').explode()
        top_countries = countries.value_counts().head(10).reset_index()
        top_countries.columns = ['Country', 'Publications']
        fig_country = px.bar(top_countries, x='Publications', y='Country', orientation='h',
                             color='Publications', color_continuous_scale='Plasma')
        fig_country.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_country, use_container_width=True)
        
    col_a3, col_a4 = st.columns(2)
    
    with col_a3:
        st.subheader("Top 10 Affiliations")
        affils = df_filtered['affiliations'].dropna().str.split('+').explode()
        top_affils = affils.value_counts().head(10).reset_index()
        top_affils.columns = ['Affiliation', 'Publications']
        fig_affil = px.bar(top_affils, x='Publications', y='Affiliation', orientation='h',
                           color='Publications', color_continuous_scale='Magma')
        fig_affil.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_affil, use_container_width=True)
        
    with col_a4:
        st.subheader("Authors per Paper Distribution")
        fig_auth_hist = px.histogram(df_filtered, x='author_count', nbins=20, 
                                     title="Distribution of Team Sizes")
        fig_auth_hist.update_layout(xaxis_title="Number of Authors", yaxis_title="Number of Papers")
        st.plotly_chart(fig_auth_hist, use_container_width=True)

with tab3:
    st.header("Journals and Subject Areas")
    
    col_j1, col_j2 = st.columns(2)
    
    top_k = st.slider("Select Top Journals to Display", min_value=5, max_value=20, value=10)

    with col_j1:
        st.subheader("Top Journals by Volume")
        top_journals = df_filtered['publication_name'].value_counts().head(top_k).reset_index()
        top_journals.columns = ['Journal', 'Publications']
        fig_j_vol = px.bar(top_journals, x='Publications', y='Journal', orientation='h')
        fig_j_vol.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_j_vol, use_container_width=True)
        
    with col_j2:
        st.subheader("Top Journals by Total Citations")
        journal_cit = df_filtered.groupby('publication_name')['citation_count'].sum().sort_values(ascending=False).head(top_k).reset_index()
        journal_cit.columns = ['Journal', 'Total Citations']
        fig_j_cit = px.bar(journal_cit, x='Total Citations', y='Journal', orientation='h', color='Total Citations')
        fig_j_cit.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_j_cit, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Evolution of Top Subject Areas")
    
    df_subjects = df_filtered[['year', 'subject_areas']].dropna()
    df_subjects['subject'] = df_subjects['subject_areas'].str.split('+')
    df_exploded = df_subjects.explode('subject')
    
    top_5_subjects = df_exploded['subject'].value_counts().head(5).index.tolist()
    
    df_evolution = df_exploded[df_exploded['subject'].isin(top_5_subjects)]
    df_evolution_grouped = df_evolution.groupby(['year', 'subject']).size().reset_index(name='Count')
    
    fig_evol = px.line(df_evolution_grouped, x='year', y='Count', color='subject', 
                       markers=True, title="Growth of Top 5 Subject Areas")
    st.plotly_chart(fig_evol, use_container_width=True)
    
    st.subheader("Subject Area Word Cloud")
    text = " ".join(df_exploded['subject'].dropna())
    if text:
        wordcloud = WordCloud(width=1200, height=400, background_color='white').generate(text)
        fig_wc, ax = plt.subplots(figsize=(12, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig_wc)

with tab4:
    st.header("Citation Impact Analysis")
    
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        st.subheader("Citations vs. Year (Impact over time)")
        fig_scatter = px.scatter(df_filtered, x='year', y='citation_count', 
                                 size='citation_count', hover_data=['title', 'publication_name'],
                                 color='citation_count', title="Papers: Year vs. Citations")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_c2:
        st.subheader("Citation Distribution")
        fig_hist_cit = px.histogram(df_filtered, x='citation_count', nbins=50, log_y=True,
                                    title="Log Distribution of Citations")
        st.plotly_chart(fig_hist_cit, use_container_width=True)
        
    st.subheader("Citation Variance in Top Journals")
    top_10_journals_list = df_filtered['publication_name'].value_counts().head(10).index
    df_top_journals = df_filtered[df_filtered['publication_name'].isin(top_10_journals_list)]
    
    fig_box = px.box(df_top_journals, x='publication_name', y='citation_count', 
                     title="Citation Distribution by Top Journals")
    fig_box.update_layout(xaxis_title="Journal", yaxis_title="Citations")
    st.plotly_chart(fig_box, use_container_width=True)

with tab5:
    st.header("Raw Data")
    st.write("Filter and download the processed data.")
    
    st.dataframe(df_filtered)
    
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered CSV",
        data=csv,
        file_name='scopus_data_filtered.csv',
        mime='text/csv',
    )

@st.cache_data
def load_scattterd_projection() -> pd.DataFrame:
    cluster_label = pd.read_csv("../data/processed_data/cluster_clear_labels.csv", index_col=0)
    scopus = pd.read_csv('../data/processed_data/scopus_data_cleansed_clusters.csv')
    
    scopus = scopus.merge(cluster_label, left_on='cluster', right_index=True, how='left')
    return scopus

with tab6:
    cluster = load_scattterd_projection()

    fig = px.scatter(
        cluster, 
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

    st.title("Topic Clusters of Research Papers")
    st.plotly_chart(fig, use_container_width=True)
