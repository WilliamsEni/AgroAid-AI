import os

import streamlit as st
from supabase import create_client
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def format_timestamp(value):
    if not value:
        return "Not available"

    try:
        if isinstance(value, str):
            value = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )

        lagos_time = value.astimezone(
            ZoneInfo("Africa/Lagos")
        )

        return lagos_time.strftime(
            "%d %b %Y, %I:%M %p WAT"
        )

    except (ValueError, TypeError):
        return str(value)

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AgroAid Specialist Dashboard",
    page_icon="👨‍🌾",
    layout="wide",
)


# -------------------------------------------------
# SUPABASE CONNECTION
# -------------------------------------------------

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

def get_auth_client():
    supabase_url = os.getenv("SUPABASE_URL")
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not supabase_url or not publishable_key:
        return None

    return create_client(
        supabase_url,
        publishable_key
    )

supabase = get_supabase_client()
auth_client = get_auth_client()

if "specialist_authenticated" not in st.session_state:
    st.session_state["specialist_authenticated"] = False

if "specialist_email" not in st.session_state:
    st.session_state["specialist_email"] = None

if "specialist_access_token" not in st.session_state:
    st.session_state["specialist_access_token"] = None

if "specialist_refresh_token" not in st.session_state:
    st.session_state["specialist_refresh_token"] = None

if (
    auth_client is not None
    and st.session_state.get("specialist_access_token")
    and st.session_state.get("specialist_refresh_token")
):
    try:
        auth_client.auth.set_session(
            st.session_state["specialist_access_token"],
            st.session_state["specialist_refresh_token"],
        )
    except Exception as error:
        print(f"Session restore error: {error}")
        st.session_state["specialist_authenticated"] = False
        st.session_state["specialist_email"] = None
        st.session_state["specialist_access_token"] = None
        st.session_state["specialist_refresh_token"] = None

specialist_emails = {
    email.strip().lower()
    for email in os.getenv("SPECIALIST_EMAILS", "").split(",")
    if email.strip()
}

# -------------------------------------------------
# SPECIALIST AUTHENTICATION
# -------------------------------------------------

if not st.session_state["specialist_authenticated"]:

    st.title("🔐 Specialist Login")

    st.write(
        "Sign in with an authorized AgroAid specialist account "
        "to access farmer requests and AI diagnoses."
    )

    if auth_client is None:
        st.error(
            "Authentication is not configured. "
            "SUPABASE_URL or SUPABASE_PUBLISHABLE_KEY is missing."
        )
        st.stop()

    if not specialist_emails:
        st.error(
            "No specialist accounts have been authorized."
        )
        st.stop()

    with st.form("specialist_login_form"):

        login_email = st.text_input(
            "Email address",
            placeholder="specialist@example.com"
        )

        login_password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "Sign In",
            type="primary",
            width="stretch"
        )

    if login_button:

        normalized_email = login_email.strip().lower()

        if not normalized_email or not login_password:
            st.error("Enter your email address and password.")

        elif normalized_email not in specialist_emails:
            st.error(
                "This account is not authorized to access "
                "the Specialist Dashboard."
            )

        else:

            try:

                login_response = auth_client.auth.sign_in_with_password(
                    {
                        "email": normalized_email,
                        "password": login_password,
                    }
                )

                user = login_response.user

                if user is None:
                    st.error("Unable to sign in.")

                elif (
                    not user.email
                    or user.email.lower() not in specialist_emails
                ):
                    st.error(
                        "This account is not authorized as a specialist."
                    )

                else:
                    session = login_response.session

                    if session is None:
                        st.error("Authentication succeeded, but no session was returned.")
                    else:
                        st.session_state["specialist_authenticated"] = True
                        st.session_state["specialist_email"] = user.email
                        st.session_state["specialist_access_token"] = (
                            session.access_token
                        )
                        st.session_state["specialist_refresh_token"] = (
                            session.refresh_token
                        )

                        st.rerun()

            except Exception as error:

                st.error(
                    "Sign in failed. Check your email and password."
                )

                print(f"Specialist login error: {error}"
        )

    st.stop()


# -------------------------------------------------
# HEADER
# -------------------------------------------------

with st.sidebar:

    st.caption(
        f"Signed in as\n"
        f"{st.session_state['specialist_email']}"
    )

    if st.button(
        "Log Out",
        width="stretch"
    ):
        try:
            auth_client.auth.sign_out()
        except Exception:
            pass

        st.session_state["specialist_authenticated"] = False
        st.session_state["specialist_email"] = None
        st.rerun()


st.title("👨‍🌾 AgroAid Specialist Dashboard")

st.write(
    "Review farmer requests, inspect AI diagnoses, "
    "and update the status of agricultural cases."
)

st.divider()


# -------------------------------------------------
# CHECK DATABASE CONNECTION
# -------------------------------------------------

if auth_client is None:
    st.error(
        "Database connection is not configured. "
        "SUPABASE_URL or SUPABASE_PUBLISHABLE_KEY is missing."
    )
    st.stop()


# -------------------------------------------------
# LOAD EXPERT REQUESTS
# -------------------------------------------------

try:
    response = (
        auth_client
        .table("expert_requests")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    requests = response.data or []

except Exception as error:
    st.error("Unable to load expert requests.")
    print(f"Dashboard database error: {error}")
    st.stop()


# -------------------------------------------------
# DASHBOARD METRICS
# -------------------------------------------------

total_requests = len(requests)

pending_requests = sum(
    1 for request in requests
    if request.get("status") == "Pending"
)

urgent_requests = sum(
    1 for request in requests
    if request.get("urgency") in ["Urgent", "Emergency"]
)

resolved_requests = sum(
    1 for request in requests
    if request.get("status") == "Resolved"
)


col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Requests", total_requests)
col2.metric("Pending", pending_requests)
col3.metric("Urgent / Emergency", urgent_requests)
col4.metric("Resolved", resolved_requests)

st.divider()


# -------------------------------------------------
# FILTER REQUESTS
# -------------------------------------------------

st.subheader("Expert Requests")

status_filter = st.selectbox(
    "Filter by status",
    [
        "All",
        "Pending",
        "In Review",
        "Resolved"
    ]
)


if status_filter == "All":
    filtered_requests = requests
else:
    filtered_requests = [
        request
        for request in requests
        if request.get("status") == status_filter
    ]


# -------------------------------------------------
# REQUEST TABLE
# -------------------------------------------------

if not filtered_requests:

    st.info("No expert requests found.")

else:

    table_data = []

    for request in filtered_requests:

        table_data.append(
            {
                "Case ID": request.get("case_id"),
                "Farmer": request.get("farmer_name"),
                "Category": request.get("category"),
                "Type": request.get("item_type"),
                "Urgency": request.get("urgency"),
                "Status": request.get("status"),
                "Diagnosis": request.get("diagnosis_id"),
                "Submitted": format_timestamp(request.get("created_at")),
            }
        )

    st.dataframe(
        table_data,
        width="stretch",
        hide_index=True,
    )


# -------------------------------------------------
# OPEN A CASE
# -------------------------------------------------

st.divider()

st.subheader("Open Case")


if requests:

    case_lookup = {
        f"{request.get('case_id')} | "
        f"{request.get('farmer_name')} | "
        f"{request.get('urgency')}":
        request
        for request in requests
    }

    selected_case_label = st.selectbox(
        "Select an expert request",
        list(case_lookup.keys())
    )

    selected_case = case_lookup[selected_case_label]


    # ---------------------------------------------
    # FARMER / REQUEST INFORMATION
    # ---------------------------------------------

    with st.container(border=True):

        st.markdown(
            f"### Case {selected_case.get('case_id')}"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Farmer:** "
                f"{selected_case.get('farmer_name') or 'Not provided'}"
            )

            st.write(
                f"**Contact method:** "
                f"{selected_case.get('contact_method') or 'Not provided'}"
            )

            st.write(
                f"**Contact:** "
                f"{selected_case.get('contact_detail') or 'Not provided'}"
            )

            st.write(
                f"**Location:** "
                f"{selected_case.get('location') or 'Not provided'}"
            )

        with col2:

            st.write(
                f"**Category:** "
                f"{selected_case.get('category') or 'Not provided'}"
            )

            st.write(
                f"**Type:** "
                f"{selected_case.get('item_type') or 'Not provided'}"
            )

            st.write(
                f"**Urgency:** "
                f"{selected_case.get('urgency') or 'Normal'}"
            )

            st.write(
                f"**Status:** "
                f"{selected_case.get('status') or 'Pending'}"
            )

        if selected_case.get("symptoms"):

            st.markdown("#### Symptoms")
            st.write(selected_case["symptoms"])

        if selected_case.get("additional_notes"):

            st.markdown("#### Additional notes")
            st.write(selected_case["additional_notes"])


    # ---------------------------------------------
    # LINKED AI DIAGNOSIS
    # ---------------------------------------------

    diagnosis_id = selected_case.get("diagnosis_id")

    if diagnosis_id:

        st.subheader("AI Diagnosis")

        try:

            diagnosis_response = (
                auth_client
                .table("diagnoses")
                .select("*")
                .eq("diagnosis_id", diagnosis_id)
                .limit(1)
                .execute()
            )

            diagnosis_rows = diagnosis_response.data or []

            if diagnosis_rows:

                diagnosis = diagnosis_rows[0]

                with st.container(border=True):

                    st.caption(
                        f"Diagnosis reference: {diagnosis_id}"
                    )

                    st.markdown(
                        diagnosis.get(
                            "ai_diagnosis",
                            "No AI diagnosis available."
                        )
                    )

                    if diagnosis.get("model"):
                        st.caption(
                            f"AI model: {diagnosis['model']}"
                        )

            else:

                st.warning(
                    "The diagnosis reference exists, "
                    "but the diagnosis record could not be found."
                )

        except Exception as error:

            st.error(
                "Unable to load the linked AI diagnosis."
            )

            print(
                f"Diagnosis lookup error: {error}"
            )

    else:

        st.info(
            "This expert request was created before "
            "AI diagnosis linking was added."
        )


# ------------------------------------------------
# SPECIALIST RESPONSE
# ------------------------------------------------

st.subheader("Specialist Recommendation")

existing_response = selected_case.get("specialist_response") or ""

specialist_response = st.text_area(
    "Response to farmer",
    value=existing_response,
    placeholder=(
        "Enter your professional assessment, recommendations, "
        "and any next steps for the farmer."
    ),
    height=180,
    key=f"specialist_response_{selected_case['case_id']}",
)

st.caption(
    "Submitting a specialist response will mark this case as Resolved."
)

if st.button(
    "Submit Specialist Response",
    type="primary",
    width="stretch",
    key=f"submit_specialist_response_{selected_case['case_id']}",
):
    if not specialist_response.strip():
        st.warning("Please enter a specialist response before submitting.")

    else:
        try:
            response_update = (
                auth_client
                .table("expert_requests")
                .update(
                    {
                        "specialist_response": specialist_response.strip(),
                        "specialist_email": st.session_state[
                            "specialist_email"
                        ],
                        "responded_at": datetime.now(
                            timezone.utc
                        ).isoformat(),
                        "status": "Resolved",
                    }
                )
                .eq(
                    "case_id",
                    selected_case["case_id"],
                )
                .execute()
            )

            if not response_update.data:
                raise RuntimeError(
                    "The database did not confirm the specialist response."
                )

            st.success(
                f"Response submitted for "
                f"{selected_case['case_id']}."
            )

            st.rerun()

        except Exception as error:
            st.error(
                "The specialist response could not be saved. "
                "Please try again."
            )

            print(
                f"Specialist response error: {error}"
            )


    # ---------------------------------------------
    # UPDATE CASE STATUS
    # ---------------------------------------------

    st.subheader("Update Case")

    current_status = (
        selected_case.get("status")
        or "Pending"
    )

    status_options = [
        "Pending",
        "In Review",
        "Resolved"
    ]

    if current_status in status_options:
        current_index = status_options.index(
            current_status
        )
    else:
        current_index = 0

    new_status = st.selectbox(
        "Case status",
        status_options,
        index=current_index,
        key=f"status_{selected_case.get('case_id')}"
    )

    if st.button(
        "Update Status",
        type="primary",
        width="stretch"
    ):

        try:

            (
                auth_client
                .table("expert_requests")
                .update(
                    {
                        "status": new_status
                    }
                )
                .eq(
                    "case_id",
                    selected_case["case_id"]
                )
                .execute()
            )

            st.success(
                f"{selected_case['case_id']} "
                f"updated to {new_status}."
            )

            st.rerun()

        except Exception as error:

            st.error(
                "The case status could not be updated."
            )

            print(
                f"Status update error: {error}"
            )