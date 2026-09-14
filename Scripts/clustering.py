import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.cluster import KMeans

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / 'Output'
EMBEDDINGS_PATH = REPO_ROOT / 'logo_embeddings.csv'

num_clusters = int(sys.argv[1]) if len(sys.argv) > 1 else 10

if not EMBEDDINGS_PATH.exists():
    print(f"'{EMBEDDINGS_PATH.name}' not found - run generate_embeddings.py first.")
    sys.exit(1)

OUTPUT_DIR.mkdir(exist_ok=True)

embeddings_df = pd.read_csv(EMBEDDINGS_PATH)
print(f"{EMBEDDINGS_PATH.name} loaded with {embeddings_df.shape[0]} logos and {embeddings_df.shape[1] - 1} features.")
embedding_vectors = embeddings_df.drop('domain', axis=1).values

kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
embeddings_df['cluster'] = kmeans.fit_predict(embedding_vectors)
embeddings_df[['domain', 'cluster']].to_csv(OUTPUT_DIR / 'clustered_logos.csv', index=False)
print(f'Clustering completed with k={num_clusters} and saved to Output/clustered_logos.csv')

cluster_counts = embeddings_df['cluster'].value_counts().sort_index()
print('\nCluster distribution:')
print(cluster_counts)

plt.figure(figsize=(8, 4))
cluster_counts.plot(kind='bar')
plt.title('Logo Distribution per Cluster')
plt.xlabel('Cluster')
plt.ylabel('Number of Logos')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'cluster_distribution.png')
print('\nCluster distribution plot saved as Output/cluster_distribution.png')
