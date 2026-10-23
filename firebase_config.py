
# import os
# from dotenv import load_dotenv

# load_dotenv()

# FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# FIREBASE_URL = (
#     "https://identitytoolkit.googleapis.com/v1/accounts:"
# )

# if not FIREBASE_API_KEY:
#     raise ValueError(
#         "FIREBASE_API_KEY .env file mein missing hai."
#     )












import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

FIREBASE_URL = "https://identitytoolkit.googleapis.com/v1"

if not FIREBASE_API_KEY:
    raise ValueError(
        "FIREBASE_API_KEY .env file mein missing hai."
    )
