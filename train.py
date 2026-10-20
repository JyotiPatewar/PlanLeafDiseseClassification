
import json
import pathlib
import tensorflow as tf

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

DATA_DIR = "dataset"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42

tf.keras.utils.set_random_seed(SEED)

# Load apple leaf dataset
data_path = pathlib.Path(DATA_DIR)

if not data_path.exists():
    raise FileNotFoundError("dataset folder nahi mila!")

train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

class_names = train_ds.class_names
print("Classes:", class_names)

with open("class_names.json", "w", encoding="utf-8") as f:
    json.dump(class_names, f, indent=4)

train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

# Data augmentation
augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.08),
    layers.RandomZoom(0.1)
])

# Transfer learning model
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False

inputs = layers.Input(shape=(224, 224, 3))
x = augmentation(inputs)
x = layers.Rescaling(1 / 127.5, offset=-1)(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(
    len(class_names), activation="softmax"
)(x)

model = models.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

callbacks = [
    ModelCheckpoint(
        "best_apple_model.keras",
        monitor="val_accuracy",
        save_best_only=True,
        mode="max"
    ),
    EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True
    )
]

# Train the model
print("Training started!")

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    callbacks=callbacks
)

# Save best model
best_model = tf.keras.models.load_model("best_apple_model.keras")
best_model.save("apple_disease_model.keras")

loss, accuracy = best_model.evaluate(val_ds, verbose=0)

print(f"Validation accuracy: {accuracy * 100:.2f}%")
print("Training complete!")
