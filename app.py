import html
import json
from pathlib import Path

import numpy as np
import streamlit as st
import tensorflow as tf

from PIL import Image
from auth import render_auth, add_auth_css


# ---------- Configuration ----------

st.set_page_config(
    page_title="LeafCare - Apple Disease Detection",
    page_icon="🍃",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

MODEL_CANDIDATES = [
    BASE_DIR / "models" / "apple_disease_model.keras",
    BASE_DIR / "apple_disease_model.keras"
]

MODEL_PATH = next(
    (path for path in MODEL_CANDIDATES if path.exists()),
    None
)

CLASS_NAMES_PATH = BASE_DIR / "class_names.json"
DATASET_DIR = BASE_DIR / "dataset"


# ---------- Styling ----------

add_auth_css()

st.markdown("""
<style>
/* Main application background */
.stApp {
    background-color: #f7faf7;
}

/* Light green sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #e8f5e9 0%,
        #d9eedb 55%,
        #c8e6c9 100%
    );
    border-right: 1px solid #b4d9b8;
}

[data-testid="stSidebar"] > div {
    background: transparent;
}

/* Sidebar text */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption {
    color: #1b5e20;
}

/* Sidebar navigation */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #1b5e20 !important;
    font-weight: 500;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: #b4d9b8;
}

/* Logout button */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #2e7d32, #1b5e20);
    color: #ffffff !important;
    border: 1px solid #1b5e20;
    border-radius: 12px;
    min-height: 44px;
    padding: 10px 16px;
    font-weight: 700;
    box-shadow: 0 4px 10px rgba(27, 94, 32, 0.18);
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stButton button p,
[data-testid="stSidebar"] .stButton button span {
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: #145218;
    color: #ffffff !important;
    border-color: #145218;
    transform: translateY(-1px);
}

/* Dashboard hero */
.hero {
    background: linear-gradient(120deg, #d9f3df, #ffffff);
    border: 1px solid #cce7d1;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 24px;
}

.hero h1 {
    color: #14532d;
    margin-bottom: 12px;
}

.hero p {
    color: #365b43;
    font-size: 16px;
    line-height: 1.8;
}

/* Information cards */
.info-card {
    background: #ffffff;
    border: 1px solid #dcebdc;
    border-radius: 14px;
    padding: 18px;
    min-height: 145px;
    box-shadow: 0 3px 12px rgba(20, 83, 45, 0.05);
}

.info-card h3 {
    color: #176438;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #ffffff;
    padding: 15px;
    border: 1px solid #dcebdc;
    border-radius: 12px;
}

/* Image corners */
[data-testid="stImage"] img {
    border-radius: 12px;
}

/* Main buttons */
.stMain .stButton button {
    border-radius: 10px;
    font-weight: 600;
}

/* Mobile compatibility */
@media (max-width: 768px) {
    .hero {
        padding: 18px;
    }

    .hero h1 {
        font-size: 26px;
    }

    .info-card {
        min-height: auto;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------- Sample Images ----------

def get_sample_image(folder_name):
    folder = DATASET_DIR / folder_name

    if not folder.exists():
        return None

    extensions = [
        "*.jpg", "*.jpeg", "*.png",
        "*.JPG", "*.JPEG", "*.PNG"
    ]

    for extension in extensions:
        images = sorted(folder.glob(extension))

        if images:
            return str(images[0])

    return None


# ---------- Disease Information ----------

DISEASE_INFO = {
    "Apple___Apple_scab": {
        "name": "Apple Scab",
        "symptoms": (
            "Olive-green or dark spots may appear on leaves. "
            "In affected leaves, spots can become darker and "
            "leaf damage may increase."
        ),
        "prevention": (
            "Remove infected fallen leaves, maintain good airflow "
            "around trees and reduce prolonged leaf wetness. "
            "Seek local agricultural advice if the disease persists."
        )
    },

    "Apple___Black_rot": {
        "name": "Apple Black Rot",
        "symptoms": (
            "Brown leaf spots may develop with darker borders. "
            "Symptoms can vary depending on the infection stage "
            "and plant conditions."
        ),
        "prevention": (
            "Remove infected plant debris, practise garden sanitation "
            "and regularly inspect affected branches and leaves."
        )
    },

    "Apple___Cedar_apple_rust": {
        "name": "Cedar Apple Rust",
        "symptoms": (
            "Yellow-orange spots may appear on leaf surfaces. "
            "The disease is associated with a fungal life cycle "
            "involving apple trees and certain juniper or cedar hosts."
        ),
        "prevention": (
            "Monitor new leaf growth, inspect unusual spots and "
            "seek local agricultural advice for appropriate "
            "disease management."
        )
    },

    "Apple___healthy": {
        "name": "Healthy Apple Leaf",
        "symptoms": (
            "The model classified the image into the healthy leaf "
            "category. A visual classification cannot guarantee "
            "that a plant is completely disease-free."
        ),
        "prevention": (
            "Continue appropriate watering, balanced plant nutrition "
            "and routine leaf inspection. Maintain good growing "
            "conditions to support plant health."
        )
    }
}


# ---------- Model Loader ----------

@st.cache_resource
def load_model():
    if MODEL_PATH is None:
        raise FileNotFoundError(
            "Model file nahi mila. "
            "models/apple_disease_model.keras check karo."
        )

    if not CLASS_NAMES_PATH.exists():
        raise FileNotFoundError(
            "class_names.json nahi mila."
        )

    model = tf.keras.models.load_model(MODEL_PATH)

    with open(CLASS_NAMES_PATH, encoding="utf-8") as file:
        class_names = json.load(file)

    return model, class_names


# ---------- Authentication Guard ----------

if not st.session_state.get("authenticated", False):
    render_auth()
    st.stop()


# ---------- Sidebar ----------

with st.sidebar:
    st.markdown("## 🍃 LeafCare")
    st.caption("Apple Leaf Disease Classification")
    st.divider()

    st.write("Signed Email")
    st.caption(st.session_state.get("user_email", ""))

    if "navigation" not in st.session_state:
        st.session_state.navigation = "Dashboard"

    page = st.radio(
        "Navigation",
        ["Dashboard", "Disease Detection", "About Project"],
        key="navigation"
    )

    st.divider()

    if st.button("Logout", use_container_width=True):
        # Clear authentication and sensitive session tokens.
        for key in [
            "authenticated",
            "user_email",
            "firebase_id_token",
            "firebase_refresh_token",
            "last_prediction",
            "last_upload_id"
        ]:
            st.session_state.pop(key, None)

        st.rerun()
# ---------- Dashboard ----------

if page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>🍎 Welcome to LeafCare</h1>
        <p>
            Your Apple Leaf Health and Disease Classification
            companion. Explore common apple leaf diseases, learn
            about their possible symptoms, and understand basic
            prevention practices with the help of deep learning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🌱 Understanding Apple Leaf Health")

    st.write("""
    Apple trees can be affected by fungal diseases that change the
    appearance of their leaves. Unusual spots, yellow-orange patches,
    dark borders and changes in leaf colour can be signs that a plant
    needs closer inspection.

    LeafCare is an educational project developed using Python,
    Streamlit and TensorFlow/Keras. Its trained image classification
    model identifies an uploaded image as one of four supported
    categories: Apple Scab, Apple Black Rot, Cedar Apple Rust or
    Healthy Apple Leaf.

    The application displays the predicted category, the model's
    output score, possible symptoms and general prevention guidance.
    These results can help with learning and preliminary observation,
    but they do not replace professional agricultural diagnosis.
    """)

    st.info(
        "For a more useful prediction, upload a clear image of one "
        "apple leaf with visible details and good lighting."
    )

    st.divider()

    # Overview cards
    st.markdown("## 🌿 What You Can Explore")

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown("""
        <div class="info-card">
            <h3>🍎 Four Classes</h3>
            <p>
                Explore Apple Scab, Apple Black Rot,
                Cedar Apple Rust and Healthy Apple Leaf.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <h3>🧠 Deep Learning</h3>
            <p>
                A trained image model analyses visual patterns
                and returns scores for its supported categories.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">
            <h3>🌱 Prevention</h3>
            <p>
                Read about common symptoms and general
                practices that support plant health.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("## 🍃 Explore Apple Leaf Categories")

    st.write("""
    The following sample images are loaded from your local dataset.
    Explore their visible characteristics to learn about the four
    categories supported by the model.
    """)

    col1, col2 = st.columns(2, gap="large")

    # Apple Scab
    with col1:
        st.markdown("### 🍂 Apple Scab")

        image_path = get_sample_image("Apple___Apple_scab")

        if image_path:
            st.image(image_path, use_container_width=True)
        else:
            st.warning("Apple Scab sample image not found in dataset.")

        st.write("""
        Apple Scab is a fungal disease that may produce olive-green
        or dark spots on leaves. Affected leaves can become damaged,
        and severe infections may contribute to premature leaf fall.
        """)

        st.markdown("**Possible symptoms**")
        st.write(
            "Olive-green spots, dark lesions and changes in leaf appearance."
        )

        st.markdown("**General prevention**")
        st.write("""
        - Remove infected fallen leaves.
        - Maintain good airflow around trees.
        - Avoid prolonged leaf wetness where practical.
        """)

    # Apple Black Rot
    with col2:
        st.markdown("### 🟤 Apple Black Rot")

        image_path = get_sample_image("Apple___Black_rot")

        if image_path:
            st.image(image_path, use_container_width=True)
        else:
            st.warning("Black Rot sample image not found in dataset.")

        st.write("""
        Apple Black Rot may cause brown leaf spots with darker
        borders. The appearance and severity of symptoms can vary
        with the infection stage and growing conditions.
        """)

        st.markdown("**Possible symptoms**")
        st.write(
            "Brown spots, darker margins and irregular damaged areas."
        )

        st.markdown("**General prevention**")
        st.write("""
        - Remove infected plant debris.
        - Inspect leaves and branches regularly.
        - Practise good garden sanitation.
        """)

    st.divider()

    col3, col4 = st.columns(2, gap="large")

    # Cedar Apple Rust
    with col3:
        st.markdown("### 🟠 Cedar Apple Rust")

        image_path = get_sample_image("Apple___Cedar_apple_rust")

        if image_path:
            st.image(image_path, use_container_width=True)
        else:
            st.warning("Cedar Apple Rust sample image not found.")

        st.write("""
        Cedar Apple Rust may produce yellow-orange spots on apple
        leaves. Its fungal life cycle involves apple trees and
        certain juniper or cedar hosts.
        """)

        st.markdown("**Possible symptoms**")
        st.write(
            "Yellow-orange leaf spots and other changes in leaf appearance."
        )

        st.markdown("**General prevention**")
        st.write("""
        - Monitor new leaf growth.
        - Inspect unusual spots regularly.
        - Seek local agricultural advice when necessary.
        """)

    # Healthy Apple Leaf
    with col4:
        st.markdown("### 🌿 Healthy Apple Leaf")

        image_path = get_sample_image("Apple___healthy")

        if image_path:
            st.image(image_path, use_container_width=True)
        else:
            st.warning("Healthy leaf sample image not found.")

        st.write("""
        A healthy-looking apple leaf generally has a green appearance
        without obvious disease-related spots. Visual appearance alone
        cannot confirm that a plant is disease-free.
        """)

        st.markdown("**Healthy plant practices**")
        st.write("""
        - Provide appropriate watering.
        - Maintain balanced plant nutrition.
        - Inspect leaves regularly for unusual changes.
        """)

    st.divider()

    st.markdown("## 🧠 How LeafCare Works")

    step1, step2, step3 = st.columns(3, gap="medium")

    with step1:
        st.markdown("### 01 · Upload")
        st.write("""
        Select a clear apple leaf image in JPG, JPEG or PNG format
        from the Disease Detection page.
        """)

    with step2:
        st.markdown("### 02 · Classify")
        st.write("""
        The trained TensorFlow/Keras model processes the image
        and generates scores for the four supported classes.
        """)

    with step3:
        st.markdown("### 03 · Understand")
        st.write("""
        View the predicted class, model confidence, possible
        symptoms and general prevention information.
        """)

    st.divider()

    st.markdown("## 💚 Our Goal")

    st.write("""
    LeafCare aims to make image-based apple leaf classification
    easier to explore through a simple interface. It combines
    deep learning with accessible educational information to
    support awareness of common apple leaf conditions.
    """)

    st.caption(
        "Educational use only. Model predictions may be incorrect "
        "and should not be treated as confirmed diagnoses."
    )


# ---------- Disease Detection ----------

elif page == "Disease Detection":

    st.title("🍎 Apple Leaf Disease Detection")

    st.write("""
    Upload a clear image of a single apple leaf. The trained model
    will predict the most likely category among its four supported
    classes and display related information.
    """)

    uploaded = st.file_uploader(
        "Choose an apple leaf image",
        type=["jpg", "jpeg", "png"],
        key="leaf_image"
    )

    if uploaded is not None:

        try:
            image = Image.open(uploaded).convert("RGB")

            st.image(
                image,
                caption="Uploaded Apple Leaf",
                width=400
            )

            if st.button(
                "Predict Disease",
                use_container_width=True
            ):
                try:
                    model, class_names = load_model()

                    # Match the image size used during training.
                    resized = image.resize((224, 224))
                    array = np.asarray(
                        resized,
                        dtype=np.float32
                    )
                    array = np.expand_dims(array, axis=0)

                    # Assumes training used 0-255 pixel values.
                    predictions = model.predict(
                        array,
                        verbose=0
                    )[0]

                    if len(predictions) != len(class_names):
                        raise ValueError(
                            "Model outputs aur class names match nahi karte."
                        )

                    index = int(np.argmax(predictions))
                    class_key = class_names[index]

                    confidence = float(predictions[index]) * 100

                    details = DISEASE_INFO.get(
                        class_key,
                        {
                            "name": class_key.replace("Apple___", ""),
                            "symptoms": "Information unavailable.",
                            "prevention": (
                                "Consult an agricultural expert."
                            )
                        }
                    )

                    st.session_state.last_prediction = {
                        "upload_id": uploaded.file_id,
                        "name": details["name"],
                        "confidence": confidence,
                        "symptoms": details["symptoms"],
                        "prevention": details["prevention"]
                    }

                except Exception as error:
                    st.error(
                        "Prediction failed. Check the model, class names "
                        "and training preprocessing."
                    )
                    st.caption(str(error))

            result = st.session_state.get("last_prediction")

            if (
                result
                and result.get("upload_id") == uploaded.file_id
            ):
                st.divider()
                st.subheader("Prediction Result")

                st.success(
                    f"Predicted class: {result['name']}"
                )

                st.metric(
                    "Model confidence",
                    f"{result['confidence']:.2f}%"
                )

                st.progress(
                    min(
                        1.0,
                        max(0.0, result["confidence"] / 100)
                    )
                )

                if result["confidence"] < 60:
                    st.warning(
                        "Prediction uncertain ho sakti hai. Clear image "
                        "try karo. Model output guaranteed diagnosis nahi hai."
                    )

                st.subheader("Possible Symptoms")
                st.write(result["symptoms"])

                st.subheader("Prevention Guidance")
                st.write(result["prevention"])

                st.caption(
                    "Confidence is the model's output score, not a verified "
                    "probability that the prediction is correct."
                )

        except Exception:
            st.error(
                "Image open nahi ho paayi. Please valid JPG, JPEG "
                "ya PNG image upload karo."
            )


# ---------- About Project ----------

elif page == "About Project":

    st.title("🍃 About LeafCare")

    st.write("""
    LeafCare is an Apple Leaf Disease Classification project developed
    using Python, Streamlit and TensorFlow/Keras.

    The project uses a trained deep learning image model to classify
    apple leaf images into four categories:

    - Apple Scab
    - Apple Black Rot
    - Cedar Apple Rust
    - Healthy Apple Leaf

    The application allows authenticated users to upload an image,
    view a predicted class and model confidence, and read possible
    symptoms and general prevention guidance.
    """)

    st.markdown("## Technologies Used")

    tech1, tech2, tech3 = st.columns(3)

    with tech1:
        st.markdown("""
        <div class="info-card">
            <h3>🐍 Python</h3>
            <p>Programming and application logic.</p>
        </div>
        """, unsafe_allow_html=True)

    with tech2:
        st.markdown("""
        <div class="info-card">
            <h3>🧠 TensorFlow/Keras</h3>
            <p>Loading and running the trained image classifier.</p>
        </div>
        """, unsafe_allow_html=True)

    with tech3:
        st.markdown("""
        <div class="info-card">
            <h3>🌐 Streamlit</h3>
            <p>Interactive web application interface.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("## Important Note")

    st.info("""
    The model's prediction depends on its training data, image quality
    and limitations. A high confidence score does not guarantee a
    correct diagnosis. For serious or uncertain plant problems,
    consult a qualified agricultural expert.
    """)
