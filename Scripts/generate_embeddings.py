import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image

REPO_ROOT = Path(__file__).resolve().parent.parent
BATCH_SIZE = 32

image_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / 'logos_final'
output_path = REPO_ROOT / 'logo_embeddings.csv'

if not image_folder.is_dir():
    print(f"The folder '{image_folder}' does not exist!")
    sys.exit(1)

image_files = sorted(
    f for f in os.listdir(image_folder)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
)
if not image_files:
    print(f"No images found in '{image_folder}'!")
    sys.exit(1)

mobilenet_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
print('MobileNetV2 model loaded successfully.')
print(f"Starting image processing from folder: '{image_folder}'\n")

embedding_list = []
domain_list = []
batch_images = []
batch_domains = []


def flush_batch():
    """Run the pending batch through the model and collect its embeddings."""
    if not batch_images:
        return
    features = mobilenet_model.predict(np.vstack(batch_images), verbose=0)
    embedding_list.extend(features)
    domain_list.extend(batch_domains)
    batch_images.clear()
    batch_domains.clear()


for image_file in image_files:
    try:
        img = keras_image.load_img(image_folder / image_file, target_size=(224, 224))
        img_array = np.expand_dims(keras_image.img_to_array(img), axis=0)
        batch_images.append(preprocess_input(img_array))
        batch_domains.append(os.path.splitext(image_file)[0])
        print(f'Processed {image_file}')
    except Exception as error:
        print(f'Failed to process {image_file} - {error}')
        continue

    if len(batch_images) == BATCH_SIZE:
        flush_batch()

flush_batch()

embeddings_df = pd.DataFrame(np.array(embedding_list))
embeddings_df['domain'] = domain_list
embeddings_df.to_csv(output_path, index=False)

print(f"\nEmbeddings successfully saved to '{output_path.name}'")
print(f'Total logos processed: {len(domain_list)}')
