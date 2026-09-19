import os
import re

import streamlit as st
from supabase import create_client
from datetime import datetime
from zoneinfo import ZoneInfo

def format_timestamp(timestamp):
    if not timestamp:
        return "Not available"

    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=ZoneInfo("UTC")
            )

        lagos_time = timestamp.astimezone(
            ZoneInfo("Africa/Lagos")
        )

        return lagos_time.strftime(
            "%d %b %Y, %I:%M %p WAT"
        )

    except (ValueError, TypeError):
        return str(timestamp)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Farmer Dashboard | AgroAid AI",
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
# SUPABASE CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_secret_key = os.getenv("SUPABASE_SECRET_KEY")

    if not supabase_url or not supabase_secret_key:
        return None

    return create_client(
        supabase_url,
        supabase_secret_key,
    )


supabase = get_supabase_client()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "farmer_case" not in st.session_state:
    st.session_state["farmer_case"] = None

if "farmer_diagnosis" not in st.session_state:
    st.session_state["farmer_diagnosis"] = None


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize_contact(value):
    value = str(value or "").strip()

    if "@" in value:
        return value.lower()

    # For phone numbers, ignore spaces, +, -, brackets, etc.
    return re.sub(r"\D", "", value)


def status_step(status):
    status = (status or "Pending").strip().lower()

    if status == "resolved":
        return 4

    if status in {"in review", "reviewing"}:
        return 3

    return 2


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🌱 AgroAid Farmer Dashboard")

st.write(
    "Track your expert-help request and view recommendations "
    "from an agricultural specialist."
)

st.divider()


# --------------------------------------------------
# CASE LOOKUP
# --------------------------------------------------

st.subheader("Track Your Case")

st.write(
    "Enter the Case ID and the same phone number or email address "
    "you used when requesting expert help."
)

with st.form("farmer_case_lookup_form"):

    case_id_input = st.text_input(
        "Case ID",
        placeholder="Example: AG-AC054197",
    )

    contact_input = st.text_input(
        "Phone number or email",
        placeholder="Enter the contact information used in your request",
    )

    lookup_button = st.form_submit_button(
        "View My Case",
        type="primary",
        width="stretch",
    )


# --------------------------------------------------
# LOOKUP CASE
# --------------------------------------------------

if lookup_button:

    st.session_state["farmer_case"] = None
    st.session_state["farmer_diagnosis"] = None

    case_id = case_id_input.strip().upper()
    contact = normalize_contact(contact_input)

    if not case_id or not contact:

        st.warning(
            "Please enter both your Case ID and contact information."
        )

    elif supabase is None:

        st.error(
            "The database connection is not configured."
        )

    else:

        try:

            response = (
                supabase
                .table("expert_requests")
                .select("*")
                .eq("case_id", case_id)
                .limit(1)
                .execute()
            )

            rows = response.data or []

            if not rows:

                st.error(
                    "No matching case was found. "
                    "Check your Case ID and try again."
                )

            else:

                case = rows[0]

                saved_contact = normalize_contact(
                    case.get("contact_detail")
                )

                if saved_contact != contact:

                    st.error(
                        "The contact information does not match this case."
                    )

                else:

                    st.session_state["farmer_case"] = case

                    diagnosis_id = case.get("diagnosis_id")

                    if diagnosis_id:

                        diagnosis_response = (
                            supabase
                            .table("diagnoses")
                            .select("*")
                            .eq(
                                "diagnosis_id",
                                diagnosis_id,
                            )
                            .limit(1)
                            .execute()
                        )

                        diagnosis_rows = (
                            diagnosis_response.data or []
                        )

                        if diagnosis_rows:
                            st.session_state[
                                "farmer_diagnosis"
                            ] = diagnosis_rows[0]

        except Exception as error:

            st.error(
                "Your case could not be retrieved. Please try again."
            )

            print(
                f"Farmer dashboard lookup error: {error}"
            )


# --------------------------------------------------
# DISPLAY CASE
# --------------------------------------------------

case = st.session_state.get("farmer_case")

if case:

    st.divider()

    case_id = case.get("case_id", "Unknown")
    status = case.get("status") or "Pending"

    st.header(f"Case {case_id}")

    status_lower = status.lower()

    if status_lower == "resolved":
        st.success("Case Status: Resolved")
    elif status_lower == "in review":
        st.info("Case Status: In Review")
    else:
        st.warning(f"Case Status: {status}")

    # --------------------------------------------------
    # CASE INFORMATION
    # --------------------------------------------------

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Farmer:** "
                f"{case.get('farmer_name') or 'Not provided'}"
            )

            st.write(
                f"**Category:** "
                f"{case.get('category') or 'Not provided'}"
            )

            st.write(
                f"**Type:** "
                f"{case.get('item_type') or 'Not provided'}"
            )

        with col2:
            st.write(
                f"**Urgency:** "
                f"{case.get('urgency') or 'Not specified'}"
            )

            st.write(
                f"**Submitted:** {format_timestamp(case.get('created_at'))}"
)

            if case.get("diagnosis_id"):
                st.write(
                    f"**Diagnosis reference:** "
                    f"{case['diagnosis_id']}"
                )

        if case.get("symptoms"):

            st.markdown("### Reported symptoms")
            st.write(case["symptoms"])

        if case.get("additional_notes"):

            st.markdown("### Additional notes")
            st.write(case["additional_notes"])


    # --------------------------------------------------
    # CASE PROGRESS
    # --------------------------------------------------

    st.subheader("Case Progress")

    current_step = status_step(status)

    if current_step >= 1:
        st.write("✅ Request submitted")

    if case.get("diagnosis_id"):
        st.write("✅ AI assessment completed")
    else:
        st.write("○ AI assessment")

    if current_step >= 3:
        st.write("✅ Specialist reviewing case")
    else:
        st.write("⏳ Waiting for specialist review")

    if current_step >= 4:
        st.write("✅ Specialist responded")
    else:
        st.write("○ Specialist response")


    # --------------------------------------------------
    # AI DIAGNOSIS
    # --------------------------------------------------

    diagnosis = st.session_state.get("farmer_diagnosis")

    if diagnosis:

        st.subheader("AI Assessment")

        with st.container(border=True):

            st.caption(
                f"Diagnosis reference: "
                f"{diagnosis.get('diagnosis_id')}"
            )

            ai_diagnosis = diagnosis.get("ai_diagnosis")

            if ai_diagnosis:
                st.markdown(ai_diagnosis)

    elif case.get("diagnosis_id"):

        st.info(
            "The AI diagnosis reference exists, but the assessment "
            "could not currently be loaded."
        )


    # --------------------------------------------------
    # SPECIALIST RESPONSE
    # --------------------------------------------------

    st.subheader("Specialist Recommendation")

    specialist_response = case.get("specialist_response")

    if specialist_response:

        st.success(
            "An agricultural specialist has responded to your case."
        )

        with st.container(border=True):

            st.markdown("### 👩‍🌾 Specialist Recommendation")

            st.write(specialist_response)

            if case.get("responded_at"):
                st.caption(
                    f"Response received: "
                    f"{format_timestamp(case.get('responded_at'))}"
)

    else:

        if status_lower == "in review":

            st.info(
                "Your case is currently being reviewed by an "
                "agricultural specialist."
            )

        else:

            st.info(
                "Your request has been received. "
                "A specialist has not responded yet."
            )


    # --------------------------------------------------
    # NEW LOOKUP
    # --------------------------------------------------

    st.divider()

    if st.button(
        "Check Another Case",
        width="stretch",
    ):

        st.session_state["farmer_case"] = None
        st.session_state["farmer_diagnosis"] = None
        st.rerun()