
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_oauth import OAuth2Component
from urllib.parse import urlencode

from firebase_config import FIREBASE_API_KEY, FIREBASE_URL

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:8501"
)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


# ---------------- FIREBASE AUTH ----------------

def firebase_request(endpoint, data):
    url = f"{FIREBASE_URL}/{endpoint}?key={FIREBASE_API_KEY}"

    try:
        response = requests.post(url, json=data, timeout=15)
        result = response.json()

        if response.status_code != 200:
            error = result.get("error", {}).get(
                "message", "Authentication failed"
            )

            errors = {
                "EMAIL_EXISTS": "This email is already registered.",
                "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
                "EMAIL_NOT_FOUND": "Email is not registered.",
                "INVALID_PASSWORD": "Incorrect password.",
                "WEAK_PASSWORD": "Password must contain at least 6 characters.",
                "OPERATION_NOT_ALLOWED": (
                    "Enable Email/Password sign-in in Firebase."
                ),
                "TOO_MANY_ATTEMPTS_TRY_LATER": (
                    "Too many attempts. Please try later."
                ),
            }

            return {
                "error": errors.get(
                    error, error.replace("_", " ").title()
                )
            }

        return result

    except (requests.RequestException, ValueError):
        return {
            "error": "Network error. Please check your internet connection."
        }


def signup(name, email, password):
    result = firebase_request(
        "accounts:signUp",
        {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
    )

    if "error" in result:
        return result

    try:
        requests.post(
            f"{FIREBASE_URL}/accounts:update?key={FIREBASE_API_KEY}",
            json={
                "idToken": result["idToken"],
                "displayName": name,
                "returnSecureToken": True,
            },
            timeout=15,
        )
    except requests.RequestException:
        pass

    result["displayName"] = name
    return result


def signin(email, password):
    return firebase_request(
        "accounts:signInWithPassword",
        {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
    )


def forgot_password(email):
    return firebase_request(
        "accounts:sendOobCode",
        {
            "requestType": "PASSWORD_RESET",
            "email": email,
        },
    )


def google_firebase_login(id_token):
    app_url = os.getenv(
        "FIREBASE_REQUEST_URI", "http://localhost:8501"
    )

    return firebase_request(
        "accounts:signInWithIdp",
        {
            "postBody": urlencode({
                "id_token": id_token,
                "providerId": "google.com",
            }),
            "requestUri": app_url,
            "returnIdpCredential": True,
            "returnSecureToken": True,
        },
    )


# def save_login(result):
#     st.session_state["authenticated"] = True
#     st.session_state["email"] = result.get("email", "")
#     st.session_state["idToken"] = result.get("idToken", "")
#     st.session_state["refreshToken"] = result.get("refreshToken", "")
#     st.rerun()


def save_login(result):
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = result.get("email", "")
    st.session_state["idToken"] = result.get("idToken", "")
    st.session_state["refreshToken"] = result.get("refreshToken", "")
    st.rerun()


def change_page(page):
    st.session_state.auth_page = page
    st.rerun()


# ---------------- UI CSS ----------------

def add_auth_css():
    st.markdown(
        """
        <style>
        /* REMOVE TOP SPACE */
        [data-testid="stAppViewContainer"] {
            background: #f2f8f1;
        }

        [data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }

        [data-testid="stAppViewBlockContainer"] {
            max-width: 1120px;
            padding: 0.25rem 1.5rem 0.5rem !important;
        }

        #MainMenu,
        footer {
            visibility: hidden;
        }

        /* COLUMNS */
        [data-testid="stHorizontalBlock"] {
            gap: 2rem !important;
            align-items: center !important;
        }

        [data-testid="stColumn"] {
            min-width: 0 !important;
        }

        /* LEFT GREEN PANEL */
        # .brand-card {
        #     box-sizing: border-box;
        #     width: 100%;
        #     min-height: 510px;
        #     padding: 34px 30px;
        #     border-radius: 22px;
        #     background: linear-gradient(
        #         145deg,
        #         #064e3b 0%,
        #         #087443 55%,
        #         #16a34a 100%
        #     );
        #     color: #ffffff;
        #     box-shadow: 0 12px 30px rgba(6, 78, 59, 0.18);
        #     display: flex;
        #     flex-direction: column;
        #     justify-content: center;
        #     white-space: normal;
        #     overflow-wrap: break-word;
        #     word-break: normal;
        # }

        # .brand-card * {
        #     box-sizing: border-box;
        #     font-family: sans-serif;
        #     white-space: normal;
        #     overflow-wrap: break-word;
        #     word-break: normal;
        # }

        # .brand-icon {
        #     font-size: 32px;
        #     font-weight: 800;
        #     line-height: 1.4;
        #     margin-bottom: 18px;
        # }

        # .brand-description {
        #     color: #e4f7e8;
        #     font-size: 15px;
        #     line-height: 1.7;
        #     margin-bottom: 20px;
        # }

        # .brand-feature {
        #     color: #ffffff;
        #     font-size: 14px;
        #     line-height: 2.3;
        # }

        # .brand-footer {
        #     border-top: 1px solid rgba(255,255,255,0.28);
        #     margin-top: 23px;
        #     padding-top: 14px;
        #     color: #dcfce7;
        #     font-size: 10px;
        #     font-weight: 700;
        #     letter-spacing: 1.2px;
        #     line-height: 1.7;
        # }

                /* LEFT BRAND PANEL */
        .brand-card {
            box-sizing: border-box;
            width: 100%;
            min-height: 510px;
            padding: 34px 30px;
            border-radius: 22px;
            background: linear-gradient(
                145deg,
                #064e3b 0%,
                #087443 55%,
                #16a34a 100%
            );
            color: #ffffff;
            box-shadow: 0 12px 30px rgba(6, 78, 59, 0.18);
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
        }

        .brand-icon {
            color: #ffffff;
            font-size: 32px;
            font-weight: 800;
            line-height: 1.4;
            margin-bottom: 18px;
        }

        .brand-description {
            color: #e4f7e8;
            font-size: 15px;
            line-height: 1.7;
            margin-bottom: 20px;
        }

        .brand-feature {
            color: #ffffff;
            font-size: 14px;
            line-height: 2.3;
        }

        .brand-footer {
            border-top: 1px solid rgba(255,255,255,0.28);
            margin-top: 23px;
            padding-top: 14px;
            color: #dcfce7;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.2px;
            line-height: 1.7;
        }

        /* RIGHT WHITE CARD */
        [data-testid="stVerticalBlockBorderWrapper"] {
            box-sizing: border-box !important;
            background: #ffffff !important;
            border: 1px solid #e0ebe1 !important;
            border-radius: 22px !important;
            box-shadow: 0 12px 35px rgba(20, 83, 45, 0.13) !important;
            padding: 25px !important;
            min-width: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]
        [data-testid="stVerticalBlock"] {
            min-width: 0;
        }

        /* HEADINGS */
        .form-heading {
            color: #14532d;
            font-size: 29px;
            line-height: 1.35;
            font-weight: 800;
            margin: 0;
            overflow-wrap: break-word;
        }

        .form-subtitle {
            color: #52665a;
            font-size: 14px;
            line-height: 1.6;
            margin: 4px 0 14px;
        }

        /* INPUT LABELS */
        .stTextInput label {
            color: #244331 !important;
            font-size: 14px !important;
            font-weight: 650 !important;
        }

        /* INPUT BOXES */
        .stTextInput input {
            box-sizing: border-box !important;
            background: #ffffff !important;
            color: #173b25 !important;
            border: 1px solid #d5e5d7 !important;
            border-radius: 9px !important;
            min-height: 43px !important;
            font-size: 14px !important;
        }

        .stTextInput input:focus {
            border-color: #15803d !important;
            box-shadow: 0 0 0 1px #15803d !important;
        }

        [data-testid="stTextInput"] {
            width: 100%;
            max-width: 100%;
        }

        /* REMOVE FORM BORDER */
        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }

        /* FORM SUBMIT BUTTONS */
        [data-testid="stFormSubmitButton"] button {
            box-sizing: border-box !important;
            width: 100% !important;
            min-height: 44px !important;
            border-radius: 9px !important;
            background: #15803d !important;
            color: #ffffff !important;
            border: 1px solid #15803d !important;
            font-size: 14px !important;
            font-weight: 700 !important;
        }

        [data-testid="stFormSubmitButton"] button:hover {
            background: #166534 !important;
            border-color: #166534 !important;
        }

        /* PRIMARY BUTTONS */
        .stButton button[kind="primary"] {
            box-sizing: border-box !important;
            width: 100% !important;
            min-height: 43px !important;
            border-radius: 9px !important;
            background: #15803d !important;
            color: #ffffff !important;
            border: 1px solid #15803d !important;
            font-size: 14px !important;
            font-weight: 700 !important;
        }

        .stButton button[kind="primary"]:hover {
            background: #166534 !important;
        }

        /* SECONDARY BUTTONS */
        .stButton button[kind="secondary"] {
            min-height: 32px !important;
            padding: 3px 5px !important;
            background: transparent !important;
            color: #15803d !important;
            border: none !important;
            box-shadow: none !important;
            font-size: 13px !important;
            font-weight: 650 !important;
        }

        .stButton button[kind="secondary"]:hover {
            color: #166534 !important;
            text-decoration: underline !important;
        }

        /* DIVIDER */
        .auth-divider {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            color: #52665a;
            font-size: 13px;
            line-height: 1.5;
            text-align: center;
            margin: 13px 0;
        }

        .auth-divider::before,
        .auth-divider::after {
            content: "";
            flex: 1;
            height: 1px;
            background: #d5e5d7;
        }

        /* GOOGLE LOGIN CONTAINER */
        .google-dark {
            width: 100%;
            border-radius: 9px;
            overflow: hidden;
        }

        /* LAPTOP */
        @media (min-width: 769px) and (max-height: 850px) {
            [data-testid="stAppViewBlockContainer"] {
                padding-top: 0 !important;
                padding-bottom: 0.3rem !important;
            }

            .brand-card {
                min-height: 475px;
                padding: 25px 26px;
            }

            .brand-icon {
                margin-bottom: 13px;
            }

            .brand-description {
                line-height: 1.55;
                margin-bottom: 14px;
            }

            .brand-feature {
                line-height: 2.1;
            }

            .brand-footer {
                margin-top: 17px;
                padding-top: 11px;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 22px !important;
            }

            .form-heading {
                font-size: 27px;
            }

            .form-subtitle {
                margin-bottom: 11px;
            }

            .auth-divider {
                margin: 10px 0;
            }
        }

        /* MOBILE */
        @media (max-width: 768px) {
            [data-testid="stAppViewBlockContainer"] {
                padding: 0.5rem 0.8rem !important;
            }

            [data-testid="stHorizontalBlock"] {
                gap: 1rem !important;
            }

            .brand-card {
                min-height: 260px;
                height: auto;
                padding: 22px 18px;
                border-radius: 16px;
            }

            .brand-icon {
                font-size: 27px;
                margin-bottom: 10px;
            }

            .brand-description {
                font-size: 13px;
                line-height: 1.6;
                margin-bottom: 12px;
            }

            .brand-feature {
                font-size: 12px;
                line-height: 2;
            }

            .brand-footer {
                font-size: 9px;
                margin-top: 14px;
                padding-top: 9px;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 18px !important;
                border-radius: 16px !important;
            }

            .form-heading {
                font-size: 24px;
            }

            .form-subtitle {
                font-size: 13px;
                margin-bottom: 12px;
            }

            .stTextInput label {
                font-size: 13px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------- GOOGLE LOGIN ----------------

def google_login(key="google_login"):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.info(
            "Google login is not configured. Check your .env file."
        )
        return

    try:
        oauth = OAuth2Component(
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            GOOGLE_AUTH_URL,
            GOOGLE_TOKEN_URL,
            "https://oauth2.googleapis.com/token",
            None,
        )

        st.markdown(
            '<div class="google-dark">',
            unsafe_allow_html=True,
        )

        result = oauth.authorize_button(
            name="Continue with Google",
            redirect_uri=GOOGLE_REDIRECT_URI,
            scope="openid email profile",
            key=key,
            use_container_width=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if result and result.get("token"):
            id_token = result["token"].get("id_token")

            if not id_token:
                st.error(
                    "Google did not return an ID token. Please try again."
                )
                return

            login_result = google_firebase_login(id_token)

            if "error" in login_result:
                st.error(login_result["error"])
            else:
                save_login(login_result)

    except Exception as error:
        st.error(
            "Google login failed. Check your OAuth configuration."
        )
        print("Google OAuth error:", error)


# ---------------- AUTH PAGES ----------------

def render_auth():
    add_auth_css()

    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "signin"

    page = st.session_state.auth_page

    # CREATE BOTH COLUMNS INSIDE THE FUNCTION
    left, right = st.columns([1.05, 0.95], gap="large")

    # -------- LEFT BRAND PANEL --------
    # with left:
    #     st.markdown(
    #     """
    #         <div style="
    #             background-color: #123524;
    #             color: white;
    #             padding: 30px;
    #             border-radius: 15px;
    #         ">
    #             <h2>🍃 LeafCare</h2>

    #             <p>
    #                 Discover a smarter way to explore apple leaf health
    #                 with deep learning and image classification.
    #             </p>

    #             <p>
    #                 🍎 Four apple leaf categories<br>
    #                 🧠 Deep learning classification<br>
    #                 🌱 Symptoms and prevention<br>
    #                 🔐 Secure account access
    #             </p>

    #             <p>GROW HEALTHIER. LEARN SMARTER.</p>
    #         </div>
    #         """,
    #         unsafe_allow_html=True,
    #     )


      # -------- LEFT BRAND PANEL --------
    with left:
        st.html("""
        <div style="
            box-sizing: border-box;
            width: 100%;
            min-height: 510px;
            padding: 35px 30px;
            border-radius: 22px;
            background: linear-gradient(145deg, #064e3b, #087443, #16a34a);
            color: white;
            box-shadow: 0 12px 30px rgba(6,78,59,0.18);
            display: flex;
            flex-direction: column;
            justify-content: center;
            font-family: sans-serif;
        ">

            <div style="
                font-size: 32px;
                font-weight: 800;
                margin-bottom: 22px;
            ">
                🍃 LeafCare
            </div>

            <div style="
                font-size: 15px;
                line-height: 1.8;
                color: #e4f7e8;
                margin-bottom: 24px;
            ">
                Discover a smarter way to explore apple leaf health
                with deep learning and image classification.
            </div>

            <div style="
                font-size: 14px;
                line-height: 2.5;
                color: white;
            ">
                🍎 Four apple leaf categories<br>
                🧠 Deep learning classification<br>
                🌱 Symptoms and prevention<br>
                🔐 Secure account access
            </div>

            <div style="
                border-top: 1px solid rgba(255,255,255,0.3);
                margin-top: 25px;
                padding-top: 16px;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1.5px;
                color: #dcfce7;
            ">
                GROW HEALTHIER. LEARN SMARTER.
            </div>

        </div>
        """)
    # -------- RIGHT AUTHENTICATION CARD --------
    with right:
        with st.container(border=True):

            # -------- SIGN UP --------
            if page == "signup":
                st.markdown(
                    '<div class="form-heading">Create Account</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="form-subtitle">'
                    'Create your LeafCare account to get started.'
                    '</div>',
                    unsafe_allow_html=True,
                )

                with st.form("signup_form"):
                    name = st.text_input(
                        "Full Name",
                        placeholder="Enter your name",
                    )

                    email = st.text_input(
                        "Email Address",
                        placeholder="you@example.com",
                    )

                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="At least 6 characters",
                    )

                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Re-enter password",
                    )

                    submitted = st.form_submit_button(
                        "Create Account",
                        type="primary",
                        use_container_width=True,
                    )

                if submitted:
                    if (
                        not name.strip()
                        or not email.strip()
                        or not password
                    ):
                        st.warning("Please fill in all fields.")

                    elif password != confirm_password:
                        st.error("Passwords do not match.")

                    elif len(password) < 6:
                        st.error(
                            "Password must contain at least 6 characters."
                        )

                    else:
                        result = signup(
                            name.strip(),
                            email.strip(),
                            password,
                        )

                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success("Account created successfully!")
                            save_login(result)

                st.markdown(
                    '<div class="auth-divider">or continue with</div>',
                    unsafe_allow_html=True,
                )

                google_login("google_signup")

                st.markdown(
                    '<div class="auth-divider">'
                    'Already have an account?'
                    '</div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Sign In",
                    key="signup_signin",
                    type="primary",
                    use_container_width=True,
                ):
                    change_page("signin")

            # -------- SIGN IN --------
            elif page == "signin":
                st.markdown(
                    '<div class="form-heading">Welcome Back!</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="form-subtitle">'
                    'Sign in to continue to LeafCare.'
                    '</div>',
                    unsafe_allow_html=True,
                )

                with st.form("signin_form"):
                    email = st.text_input(
                        "Email Address",
                        placeholder="you@example.com",
                    )

                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                    )

                    submitted = st.form_submit_button(
                        "Sign In",
                        type="primary",
                        use_container_width=True,
                    )

                if submitted:
                    if not email.strip() or not password:
                        st.warning(
                            "Please enter your email and password."
                        )
                    else:
                        result = signin(email.strip(), password)

                        if "error" in result:
                            st.error(result["error"])
                        else:
                            save_login(result)

                if st.button(
                    "Forgot Password",
                    key="forgot_link",
                    use_container_width=True,
                ):
                    change_page("forgot")

                google_login("google_signin")

                st.markdown(
                    '<div class="auth-divider">Create User</div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Create Account",
                    key="signin_signup",
                    type="primary",
                    use_container_width=True,
                ):
                    change_page("signup")

            # -------- FORGOT PASSWORD --------
            elif page == "forgot":
                st.markdown(
                    '<div class="form-heading">Reset Password</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="form-subtitle">'
                    'We will email you a password reset link.'
                    '</div>',
                    unsafe_allow_html=True,
                )

                with st.form("forgot_form"):
                    email = st.text_input(
                        "Email Address",
                        placeholder="you@example.com",
                    )

                    submitted = st.form_submit_button(
                        "Send Reset Link",
                        type="primary",
                        use_container_width=True,
                    )

                if submitted:
                    if not email.strip():
                        st.warning("Please enter your email address.")
                    else:
                        result = forgot_password(email.strip())

                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(
                                "If the account is eligible, "
                                "a password reset email will be sent."
                            )

                st.markdown(
                    '<div class="auth-divider">'
                    'Remember your password?'
                    '</div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Back to Sign In",
                    key="forgot_signin",
                ):
                    change_page("signin")
