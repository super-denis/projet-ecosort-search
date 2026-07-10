"""
Entrainement du modele de classification des dechets (Transfer Learning).
Responsable : Denis (IA)

Dataset : Garbage Classification (Kaggle) place dans dataset/
    dataset/
        cardboard/  glass/  metal/  paper/  plastic/  trash/

Sortie : model/modele_eco_sort.h5
Lancer : python model/train.py
"""

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras import layers, models

IMG_SIZE = (224, 224)
BATCH = 32
EPOCHS = 15
DATASET_DIR = "dataset"

# --- Chargement des donnees ---
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, validation_split=0.2, subset="training", seed=123,
    image_size=IMG_SIZE, batch_size=BATCH,
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, validation_split=0.2, subset="validation", seed=123,
    image_size=IMG_SIZE, batch_size=BATCH,
)

CLASS_NAMES = train_ds.class_names
print("Classes (ordre a reporter dans predict.py) :", CLASS_NAMES)

# --- Augmentation + preprocessing ---
data_aug = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

# --- Modele : MobileNetV2 gele + tete de classification ---
base = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights="imagenet")
base.trainable = False

inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = data_aug(inputs)
x = preprocess_input(x)
x = base(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(len(CLASS_NAMES), activation="softmax")(x)
model = models.Model(inputs, outputs)

model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])

# --- Entrainement ---
model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

# --- Sauvegarde ---
model.save("model/modele_eco_sort.h5")
print("Modele sauvegarde -> model/modele_eco_sort.h5")
