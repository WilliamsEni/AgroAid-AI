import os
import re
import uuid
import time

import streamlit as st
from PIL import Image
from supabase import create_client
from google import genai


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AgroAid AI",
    page_icon="🌱",
    layout="centered",
)

# -------------------------------------------------
# PUBLIC NAVIGATION
# -------------------------------------------------

with st.sidebar:
    st.markdown("### 🌱 AgroAid AI")

    st.page_link(
        "app.py",
        label="Get Agricultural Help",
        icon="🌱",
    )

    st.page_link(
        "pages/2_Farmer_Dashboard.py",
        label="Track My Case",
        icon="📋",
    )

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

APP_STATE_VERSION = "supabase-v3"

if st.session_state.get("app_state_version") != APP_STATE_VERSION:
    st.session_state["expert_case"] = None
    st.session_state["app_state_version"] = APP_STATE_VERSION

if "expert_request_submitting" not in st.session_state:
    st.session_state["expert_request_submitting"] = False

if "ai_diagnosis" not in st.session_state:
    st.session_state["ai_diagnosis"] = None

if "diagnosis_id" not in st.session_state:
    st.session_state["diagnosis_id"] = None

if "analysis_submitting" not in st.session_state:
    st.session_state["analysis_submitting"] = False

# ---------------------------------------------
# SUPABASE CONNECTION
# ---------------------------------------------

@st.cache_resource
def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_secret_key = os.getenv("SUPABASE_SECRET_KEY")

    if not supabase_url or not supabase_secret_key:
        return None

    return create_client(
        supabase_url,
        supabase_secret_key
    )

# -------------------------------------------------
# GEMINI CONNECTION
# -------------------------------------------------

@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


gemini_client = get_gemini_client()

supabase = get_supabase_client()

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            max-width: 850px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .agro-header {
            padding: 1.5rem;
            border-radius: 16px;
            background: linear-gradient(
                135deg,
                rgba(34, 139, 34, 0.15),
                rgba(76, 175, 80, 0.05)
            );
            margin-bottom: 1.5rem;
        }

        .agro-title {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .agro-description {
            font-size: 1.05rem;
            line-height: 1.6;
        }

        .diagnosis-box {
            border: 1px solid #4b5563;
            border-radius: 14px;
            padding: 22px;
            margin-top: 10px;
            background-color: rgba(128, 128, 128, 0.05);
        }

        .diagnosis-heading {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .expert-box {
            border: 1px solid #4b5563;
            border-radius: 14px;
            padding: 20px;
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER / BRANDING
# --------------------------------------------------

st.markdown(
    """
    <div class="agro-header">
        <div class="agro-title">🌱 AgroAid AI</div>
        <div class="agro-description">
            Smart agricultural assistance for farmers.
            Upload or take a clear photo of a crop or animal showing
            signs of disease and describe what you have noticed.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Early detection • Practical guidance • Access to agricultural specialists"
)

st.divider()


# --------------------------------------------------
# STEP 1 - CATEGORY
# --------------------------------------------------

st.subheader("1. What do you need help with?")

category = st.radio(
    "Choose a category",
    ["🌾 Crop", "🐄 Animal"],
    horizontal=True,
)

category_name = "Crop" if category == "🌾 Crop" else "Animal"


# --------------------------------------------------
# STEP 2 - CROP / ANIMAL TYPE
# --------------------------------------------------

st.subheader("2. Select the type")

if category_name == "Crop":

    type_options = [
        "Select a crop",
        "Maize",
        "Cassava",
        "Rice",
        "Tomato",
        "Pepper",
        "Yam",
        "Plantain",
        "Cocoa",
        "Other",
    ]

    selected_type = st.selectbox(
        "Crop type",
        type_options,
    )

else:

    type_options = [
        "Select an animal",
        "Chicken",
        "Goat",
        "Cattle",
        "Sheep",
        "Pig",
        "Fish",
        "Rabbit",
        "Other",
    ]

    selected_type = st.selectbox(
        "Animal type",
        type_options,
    )


# --------------------------------------------------
# STEP 3 - IMAGE INPUT
# --------------------------------------------------

st.subheader("3. Add a photo")

st.write(
    "Use a clear image showing the affected leaves, skin, body part, "
    "or other visible symptoms."
)

image_method = st.radio(
    "How would you like to add the image?",
    ["Upload image", "Take photo"],
    horizontal=True,
)


uploaded_file = None

if image_method == "Upload image":

    uploaded_file = st.file_uploader(
        "Upload JPG, JPEG or PNG",
        type=["jpg", "jpeg", "png"],
    )

else:

    uploaded_file = st.camera_input(
        "Take a photo"
    )


# --------------------------------------------------
# IMAGE PREVIEW
# --------------------------------------------------

image = None

if uploaded_file is not None:

    try:

        image = Image.open(uploaded_file)

        st.success("Image added successfully.")

        st.image(
            image,
            caption=f"{category_name} image preview",
            width="stretch",
        )

        st.caption(
            f"Image size: {image.width} × {image.height} pixels"
        )

    except Exception:

        st.error(
            "The image could not be opened. "
            "Please use a valid JPG, JPEG or PNG image."
        )


# --------------------------------------------------
# STEP 4 - SYMPTOMS
# --------------------------------------------------

st.subheader("4. Describe the symptoms")

symptoms = st.text_area(
    "What have you noticed? (Optional)",
    placeholder=(
        "Example: The leaves started turning yellow three days ago. "
        "There are brown spots around the edges and the plant looks weak."
        if category_name == "Crop"
        else
        "Example: The animal has been eating less, appears weak and "
        "has unusual spots on its skin."
    ),
    height=130,
)

st.caption(
    "Including when the problem started can help improve the assessment."
)


# --------------------------------------------------
# STEP 5 - ANALYZE
# --------------------------------------------------

st.subheader("5. Analyze")

analyze_button = st.button(
    "🔍 Analyze Image",
    type="primary",
    width="stretch",
)


# --------------------------------------------------
# VALIDATION + FUTURE AI AREA
# --------------------------------------------------

st.subheader("Possible Diagnosis")

if analyze_button:

    if uploaded_file is None:
        st.warning(
            "Please upload or take a photo before analyzing."
        )

    elif selected_type.startswith("Select"):
        st.warning(
            f"Please select a {category_name.lower()} type."
        )

    elif gemini_client is None:
        st.error(
            "AI analysis is not configured. "
            "Please contact the AgroAid AI administrator."
        )

    else:
        try:
            st.session_state["ai_diagnosis"] = None

            with st.spinner("Analyzing image with AgroAid AI..."):

                image = Image.open(uploaded_file)

                prompt = f"""
You are AgroAid AI, an agricultural image analysis assistant.

Analyze the uploaded image using the image itself and the information
provided by the farmer.

Category: {category_name}
Type: {selected_type}
Farmer's symptom description:
{symptoms.strip() if symptoms.strip() else "No symptom description provided."}

Provide a preliminary agricultural assessment using exactly these sections:

### Possible condition
State the most likely crop or animal health problem.

### Confidence
Give a confidence level of Low, Medium, or High and briefly explain why.

### Observed symptoms
Describe the relevant signs visible in the uploaded image.

### Recommended next steps
Give practical and safe actions the farmer should take next.

### Expert help
State whether the farmer should consult an agricultural or veterinary
specialist.

Rules:
- Do not claim absolute certainty.
- Do not invent symptoms that cannot be seen or inferred from the provided information.
- If the image is unclear, say that the image quality limits the assessment.
- Avoid unsafe pesticide, chemical, veterinary, or medical instructions.
- Keep the response clear and practical.
"""

            response = None
            last_error = None

            for attempt in range(3):
                try:
                    response = gemini_client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=[image, prompt],
                    )
                    break

                except Exception as error:
                    last_error = error
                    error_text = str(error)

                    if "503" in error_text or "UNAVAILABLE" in error_text:
                        if attempt < 2:
                            time.sleep(3 * (attempt + 1))
                            continue

                    raise

                if response is None:
                    raise RuntimeError(
                        f"Gemini is temporarily unavailable: {last_error}"
                    )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            diagnosis_text = response.text

            diagnosis_id = f"DX-{uuid.uuid4().hex[:8].upper()}"

            diagnosis_record = {
                "diagnosis_id": diagnosis_id,
                "category": category_name,
                "item_type": selected_type,
                "symptoms": symptoms.strip() or None,
                "ai_diagnosis": diagnosis_text,
                "model": "gemini-3.8-flash",
            }

            if supabase is None:
                raise RuntimeError(
                    "Database connection is not configured."
                )

            db_response = (
                supabase
                .table("diagnoses")
                .insert(diagnosis_record)
                .execute()
            )

            if not db_response.data:
                raise RuntimeError(
                    "The diagnosis could not be saved to the database."
    )

            st.session_state["ai_diagnosis"] = diagnosis_text
            st.session_state["diagnosis_id"] = diagnosis_id


        except Exception as error:
            error_text = str(error)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                st.warning(
                    "AgroAid AI is temporarily busy. "
                    "Please wait a few seconds and try again."
                )
            else:
                st.error(
                    "The image could not be analyzed. "
                    "Please try again."
                )

            print(f"Gemini analysis error: {error}")


if st.session_state.get("ai_diagnosis"):
    with st.container(border=True):

        if st.session_state.get("diagnosis_id"):
            st.caption(
                f"Diagnosis reference: "
                f"{st.session_state['diagnosis_id']}"
            )

        st.markdown(st.session_state["ai_diagnosis"])
# --------------------------------------------------
# EXPERT HELP
# --------------------------------------------------

st.divider()

st.subheader("👨‍🌾 Get Expert Help")

st.write(
    "Request assistance from an agricultural specialist. "
    "Your crop or animal details and symptom description will be "
    "included with the request."
)

with st.expander("Request Expert Help", expanded=False):

    with st.form("expert_help_form"):

        farmer_name = st.text_input(
            "Farmer's name",
            max_chars=80,
            placeholder="Enter your name",
            key="expert_farmer_name"
        )

        contact_method = st.selectbox(
            "Preferred contact method",
            ["Select contact method", "Phone", "WhatsApp", "Email"],
            key="expert_contact_method"
        )

        contact_detail = st.text_input(
            "Phone number or email address",
            max_chars=120,
            placeholder="Example: +2348012345678 or farmer@example.com",
            key="expert_contact_detail"
        )

        farmer_location = st.text_input(
            "Location (Optional)",
            max_chars=100,
            placeholder="Example: Abeokuta, Ogun State",
            key="expert_farmer_location"
        )

        urgency = st.selectbox(
            "How urgent is the problem?",
            ["Normal", "Urgent", "Emergency"],
            key="expert_urgency"
        )

        additional_notes = st.text_area(
            "Additional information (Optional)",
            max_chars=500,
            placeholder=(
                "Add anything else the agricultural specialist "
                "should know."
            ),
            key="expert_additional_notes"
        )

        consent = st.checkbox(
            "I agree to share the information provided in this case "
            "with an agricultural specialist.",
            key="expert_consent"
        )

        submit_expert_request = st.form_submit_button(
            "Submit Expert Request",
            type="primary",
            width="stretch"
        )

# --------------------------------------------------
# EXPERT REQUEST VALIDATION
# --------------------------------------------------

if submit_expert_request:

    errors = []

    if uploaded_file is None:
        errors.append(
            "Please upload or take a photo before requesting expert help."
        )

    if selected_type.startswith("Select"):
        errors.append(
            f"Please select a {category_name.lower()} type."
        )

    if not farmer_name.strip():
        errors.append(
            "Please enter the farmer's name."
        )

    if contact_method == "Select contact method":
        errors.append(
            "Please select a preferred contact method."
        )

    if not contact_detail.strip():
        errors.append(
            "Please enter a phone number or email address."
        )

    if contact_method == "Email" and contact_detail.strip():
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(email_pattern, contact_detail.strip()):
            errors.append(
                "Please enter a valid email address."
            )

    if contact_method in ["Phone", "WhatsApp"] and contact_detail.strip():
        phone_pattern = r"^\+?[0-9\s\-()]{7,20}$"

        if not re.match(phone_pattern, contact_detail.strip()):
            errors.append(
                "Please enter a valid phone number."
            )

    if not consent:
        errors.append(
            "Please confirm consent before submitting the request."
        )

    if errors:
        for error in errors:
            st.error(error)

    else:

        if st.session_state.get("expert_request_submitting", False):
            st.warning("This request is already being submitted.")
            st.stop()

        st.session_state["expert_request_submitting"] = True

        case_id = f"AG-{uuid.uuid4().hex[:8].upper()}"

        db_record = {
            "case_id": case_id,
            "farmer_name": farmer_name.strip(),
            "contact_method": contact_method,
            "contact_detail": contact_detail.strip(),
            "location": farmer_location.strip() or None,
            "category": category_name,
            "item_type": selected_type,
            "symptoms": symptoms.strip() or None,
            "urgency": urgency,
            "additional_notes": additional_notes.strip() or None,
            "diagnosis_id": st.session_state.get("diagnosis_id"),
            "status": "Pending",
        }

        if supabase is None:
            st.session_state["expert_request_submitting"] = False

            st.error(
                "Database connection is not configured. "
                "Please contact the AgroAid AI administrator."
            )

        else:
            try:
                response = (
                    supabase
                    .table("expert_requests")
                    .insert(db_record)
                    .execute()
                )

                if not response.data:
                    raise RuntimeError(
                        "The database did not confirm the new request."
                    )

                st.session_state["expert_case"] = {
                    "case_id": case_id,
                    "diagnosis_id": st.session_state.get("diagnosis_id"),
                    "farmer_name": farmer_name.strip(),
                    "contact_method": contact_method,
                    "contact_detail": contact_detail.strip(),
                    "location": farmer_location.strip(),
                    "category": category_name,
                    "type": selected_type,
                    "symptoms": symptoms.strip(),
                    "urgency": urgency,
                    "additional_notes": additional_notes.strip(),
                }

                st.session_state["expert_request_submitting"] = False

                st.rerun()

            except Exception as error:
                st.session_state["expert_request_submitting"] = False

                st.error(
                    "The expert request could not be saved. "
                    "Please try again."
                )

                print(
                    f"Supabase insert error: {error}"
                )


# --------------------------------------------------
# CASE SUMMARY
# --------------------------------------------------

if st.session_state.get("expert_case"):
    case = st.session_state["expert_case"]

    st.success(
        f"Expert help request created successfully. "
        f"Reference: {case['case_id']}"
    )

    with st.container(border=True):
        st.markdown("### Expert Request Summary")

        st.write(f"**Case ID:** {case['case_id']}")
        if case.get("diagnosis_id"):
            st.write(f"**Diagnosis reference:** {case['diagnosis_id']}")

        st.write(f"**Farmer:** {case['farmer_name']}")
        st.write(
            f"**Contact:** {case['contact_method']} - "
            f"{case['contact_detail']}"
        )

        if case["location"]:
            st.write(f"**Location:** {case['location']}")

        st.write(f"**Category:** {case['category']}")
        st.write(f"**Type:** {case['type']}")
        st.write(f"**Urgency:** {case['urgency']}")

        if case["symptoms"]:
            st.write("**Symptoms:**")
            st.write(case["symptoms"])

        if case["additional_notes"]:
            st.write("**Additional notes:**")
            st.write(case["additional_notes"])

# --------------------------------------------------
# SAFETY NOTE
# --------------------------------------------------

st.divider()

st.caption(
    "AgroAid AI provides preliminary agricultural guidance. "
    "Important treatment decisions should be confirmed by a qualified "
    "agricultural or veterinary professional."
)

st.caption(
    "AgroAid AI • Bincom Hackathon MVP"
)