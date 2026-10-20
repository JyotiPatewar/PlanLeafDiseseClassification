
import json
import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image

st.set_page_config(
    page_title="Apple Leaf Disease Detection",
    page_icon="🍎",
    layout="centered"
)

st.title("🍎 Apple Leaf Disease Detection")
st.write("Upload an apple leaf image to predict its possible disease.")

st.info(
    "Use a clear image of one apple leaf. "
    "The prediction may not always be correct."
)


@st.cache_resource
def load_model():
    model = tf.keras.models.load_model("apple_disease_model.keras")

    with open("class_names.json", "r", encoding="utf-8") as file:
        class_names = json.load(file)

    return model, class_names


try:
    model, class_names = load_model()
except Exception as error:
    st.error("Could not load the model. Check that the model files exist.")
    st.code(str(error))
    st.stop()


disease_info = {
    "Apple___Apple_scab": {
        "name": "Apple Scab",
        "symptoms": "Dark green or brown spots may appear on the leaves.",
        "prevention": "Remove fallen leaves and keep the area clean.",
        "care": "Ask a plant expert to confirm the disease before treatment."
    },
    "Apple___Black_rot": {
        "name": "Apple Black Rot",
        "symptoms": "Brown spots may appear on the leaves. Some spots may have dark rings.",
        "prevention": "Remove infected fallen leaves and dead plant material.",
        "care": "Ask a plant expert to confirm the disease before choosing treatment."
    },
    "Apple___Cedar_apple_rust": {
        "name": "Cedar Apple Rust",
        "symptoms": "Yellow or orange spots may appear on the leaves.",
        "prevention": "Check the leaves regularly and keep the garden clean.",
        "care": "Ask a plant expert to confirm the disease and suggest suitable care."
    },
    "Apple___healthy": {
        "name": "Healthy Apple Leaf",
        "symptoms": "The model predicts that the leaf is healthy.",
        "prevention": "Provide proper water and sunlight. Check the leaves regularly.",
        "care": "This result does not guarantee that the plant is disease-free."
    }
}


uploaded_file = st.file_uploader(
    "Choose an apple leaf image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Leaf", use_container_width=True)

        if st.button("Detect Disease", type="primary"):
            resized_image = image.resize((224, 224))
            image_array = np.array(resized_image, dtype=np.float32)
            image_array = np.expand_dims(image_array, axis=0)

            probabilities = model.predict(image_array, verbose=0)[0]
            sorted_indices = np.argsort(probabilities)[::-1]

            best_index = int(sorted_indices[0])
            predicted_class = class_names[best_index]
            confidence = float(probabilities[best_index])

            second_confidence = (
                float(probabilities[int(sorted_indices[1])])
                if len(sorted_indices) > 1 else 0.0
            )

            st.subheader("Prediction")
            st.write("**Predicted Disease:**",
                     predicted_class.replace("Apple___", "").replace("_", " ").title())
            st.write(f"**Confidence Score:** {confidence * 100:.2f}%")
            st.progress(confidence)

            st.subheader("Class Probabilities")

            for index in sorted_indices:
                label = class_names[int(index)].replace(
                    "Apple___", ""
                ).replace("_", " ").title()

                score = float(probabilities[int(index)])
                st.write(f"{label}: {score * 100:.2f}%")
                st.progress(score)

            if confidence < 0.65 or confidence - second_confidence < 0.15:
                st.warning(
                    "The prediction is uncertain. Try a clearer image. "
                    "The actual disease may be different."
                )

            info = disease_info.get(predicted_class)

            if info:
                st.subheader(info["name"])

                st.markdown("**Symptoms**")
                st.write(info["symptoms"])

                st.markdown("**Prevention**")
                st.write(info["prevention"])

                st.markdown("**Care and Treatment**")
                st.write(info["care"])

            st.caption(
                "The confidence score is an estimate, not a guarantee. "
                "Confirm the disease before choosing treatment."
            )

    except Exception as error:
        st.error("Could not process this image. Please try another JPG or PNG image.")
        st.code(str(error))
