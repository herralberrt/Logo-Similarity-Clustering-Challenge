import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

embeddings_df = pd.read_csv('logo_embeddings.csv')
print(f"logo_embeddings.csv loaded with {embeddings_df.shape[0]} logos and {embeddings_df.shape[1] - 1} features.")
embedding_vectors = embeddings_df.drop('domain', axis=1).values

num_clusters = 10  # Adjust this based on your analysis
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
embeddings_df['cluster'] = kmeans.fit_predict(embedding_vectors)
embeddings_df[['domain', 'cluster']].to_csv('clustered_logos.csv', index=False)
print("Clustering completed and saved to clustered_logos.csv")

print("\nCluster distribution:")
print(embeddings_df['cluster'].value_counts().sort_index())
plt.figure(figsize=(8, 4))
embeddings_df['cluster'].value_counts().sort_index().plot(kind='bar')
plt.title('Logo Distribution per Cluster')
plt.xlabel('Cluster')
plt.ylabel('Number of Logos')
plt.tight_layout()
plt.savefig('cluster_distribution.png')
print("\nCluster distribution plot saved as cluster_distribution.png")
