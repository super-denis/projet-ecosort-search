"""
Entrainement du modele de classification des dechets (Par Transfer Learning).

Strategie :
  Phase 1 : base MobileNetV2
  Phase 2 : fine-tuning, on dégèle les dernieres couches avec un petit LR.
  + class weights pour compenser le desequilibre des classes.

Dataset : Garbage Classification (Kaggle, cchangcs) place dans dataset/
    dataset/{cardboard, glass, metal, paper, plastic, trash}/

Sorties : model/modele_eco_sort.h5  et  model/class_names.json
Lancer  : python model/train.py
"""

import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras import layers, models

IMG_SIZE = (224, 224)
BATCH = 32
EPOCHS_PHASE1 = 25   # plafond ; l'early-stopping coupe avant si ca stagne
EPOCHS_PHASE2 = 25
FINE_TUNE_LAYERS = 54  # nb de dernieres couches degelees en phase 2
DATASET_DIR = "dataset"
AUTOTUNE = tf.data.AUTOTUNE

# --- 1. Chargement des donnees ---
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, validation_split=0.2, subset="training", seed=123,
    image_size=IMG_SIZE, batch_size=BATCH,
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, validation_split=0.2, subset="validation", seed=123,
    image_size=IMG_SIZE, batch_size=BATCH,
)

CLASS_NAMES = train_ds.class_names
print("Classes :", CLASS_NAMES)

# --- 2. Class weights (compense le desequilibre : trash << paper) ---
counts = np.zeros(len(CLASS_NAMES))
for _, labels in train_ds.unbatch():
    counts[int(labels.numpy())] += 1
total = counts.sum()
class_weight = {i: total / (len(CLASS_NAMES) * c) for i, c in enumerate(counts)}
print("Class weights :", class_weight)

# --- 3. Perf : cache + prefetch ---
train_ds = train_ds.cache().prefetch(AUTOTUNE)
val_ds = val_ds.cache().prefetch(AUTOTUNE)

# --- 4. Augmentation ---
data_aug = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.15),
    layers.RandomBrightness(0.15),
])

# --- Callbacks : garde le meilleur epoch + baisse le LR quand ca stagne ---
def make_callbacks():
    return [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=6, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7),
    ]

# --- 5. Modele ---
base = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights="imagenet")
base.trainable = False  # Phase 1 : base gelee

inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = data_aug(inputs)
x = preprocess_input(x)
x = base(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(CLASS_NAMES), activation="softmax")(x)
model = models.Model(inputs, outputs)

model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])

# --- 6. Phase 1 : entrainement de la tete ---
print("\n=== PHASE 1 : base gelee ===")
model.fit(train_ds, validation_data=val_ds,
          epochs=EPOCHS_PHASE1, class_weight=class_weight,
          callbacks=make_callbacks())

# --- 7. Phase 2 : fine-tuning des dernieres couches ---
print("\n=== PHASE 2 : fine-tuning ===")
base.trainable = True
for layer in base.layers[:-FINE_TUNE_LAYERS]:  # on degele les dernieres couches
    layer.trainable = False

model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),  # LR tres bas
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
model.fit(train_ds, validation_data=val_ds,
          epochs=EPOCHS_PHASE2, class_weight=class_weight,
          callbacks=make_callbacks())

# --- 8. Evaluation finale ---
loss, acc = model.evaluate(val_ds)
print(f"\nAccuracy validation finale : {acc:.2%}")

# --- 9. Sauvegarde ---
model.save("model/modele_eco_sort.h5")
with open("model/class_names.json", "w") as f:
    json.dump(CLASS_NAMES, f)
print("Modele sauvegarde -> model/modele_eco_sort.h5")
print("Classes sauvegardees -> model/class_names.json")
