import os
import sys
import numpy as np
import pandas as pd
from PIL import Image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image

image_folder = sys.argv[1] if len(sys.argv) > 1 else 'logos_final'
if not os.path.exists(image_folder):
    print(f"The folder '{image_folder}' does not exist!")
    exit()

mobilenet_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
print("MobileNetV2 model loaded successfully.")
embedding_list = []
domain_list = []
print(f"Starting image processing from folder: '{image_folder}'\n")

for image_file in os.listdir(image_folder):
    if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            image_path = os.path.join(image_folder, image_file)
            img = keras_image.load_img(image_path, target_size=(224, 224))
            img_array = keras_image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)

            features = mobilenet_model.predict(img_array).flatten()
            embedding_list.append(features)
            domain_list.append(image_file.replace('.png', '').replace('.jpg', '').replace('.jpeg', ''))

            print(f"Processed {image_file}")
        except Exception as error:
            print(f"Failed to process {image_file} - {error}")

embeddings_array = np.array(embedding_list)
embeddings_df = pd.DataFrame(embeddings_array)
embeddings_df['domain'] = domain_list
embeddings_df.to_csv('logo_embeddings.csv', index=False)
print("\nEmbeddings successfully saved to 'logo_embeddings.csv'")
print(f"Total logos processed: {len(domain_list)}")
