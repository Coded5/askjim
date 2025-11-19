import pandas as pd
import numpy as np

from sklearn.manifold import TSNE

DATA_FILE = "../data/processed_data/scopus_data_doi_cleaned.csv"
PROJECTION_FILE = "../models/scopus_tsne_projections.npy"
VECTORS_FILE = "../models/scopus_embeddings.npy"

df = pd.read_csv(DATA_FILE)
vectors = np.load(VECTORS_FILE)

tsne = TSNE(
    n_components=2,
    init='pca',
    learning_rate='auto'
)

projection = tsne.fit_transform(vectors)
projection_df = pd.DataFrame(projection, columns=['x', 'y']) #type: ignore
projection_df.to_csv(PROJECTION_FILE, index=False)

df['x'] = projection[:, 0]
df['y'] = projection[:, 1]
df.to_csv("../data/processed_data/scopus_data_doi_cleaned_with_projections.csv", index=False)
