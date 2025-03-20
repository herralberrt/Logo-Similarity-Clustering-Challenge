# Logo Clustering Challenge

## Overview
This project solves the logo clustering challenge by downloading website favicons or scraped logos, generating visual embeddings, and performing clustering based on visual similarity.


### Workflow:
1. Download favicons or scrape logos from websites.
2. Generate visual embeddings using MobileNetV2.
3. Cluster logos based on visual similarity.


## Project Structure
├── download_logos.py            # Script that downloads favicons or scrapes logos
├── generate_embeddings.py       # Script that creates image embeddings using MobileNetV2
├── clustering.py                # Script that runs KMeans clustering
├── logos_final/                 # Folder where all logos (images) are stored
├── logo_embeddings.csv          # CSV with image embeddings and domains
├── clustered_logos.csv          # CSV result with domain and its cluster
├── cluster_distribution.png     # Bar chart image showing the cluster distribution
├── .gitignore                   # Specifies which files to exclude from git
└── README.md                    # Project documentation (ce ai cerut acum)


## Description of Scripts
- **download_logos.py**
  - Downloads favicons or scrapes logos from websites.
  - Stores logos in the `logos_final/` directory.

- **generate_embeddings.py**
  - Loads logos and extracts feature embeddings using the pre-trained MobileNetV2 model.
  - Saves embeddings and domain names to `logo_embeddings.csv`.

- **clustering.py**
  - Loads the embeddings CSV.
  - Runs KMeans clustering (default is 10 clusters).
  - Saves the clustered results to `clustered_logos.csv`.
  - Generates the visualization `cluster_distribution.png`.


## How to Run

1. **Download logos:**
  python3 download_logos.py

2. **Generate embeddings:**
  python3 generate_embeddings.py

3. **Run clustering:**
  python3 clustering.py


## Output
- `clustered_logos.csv`: Contains each domain and the cluster it was assigned to.
- `cluster_distribution.png`: Bar plot showing the number of logos in each cluster.


## Requirements
- Python 3.x
- Libraries:
  - pandas
  - requests
  - urllib3
  - beautifulsoup4
  - pillow
  - numpy
  - tensorflow
  - scikit-learn
  - matplotlib
  Install them using:
    pip install -r requirements.txt


## License
This project is licensed under the MIT License.


## Author
Created as part of the Veridion Logo Clustering Challenge.
