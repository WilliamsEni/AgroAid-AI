import streamlit as st
from PIL import Image


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AgroAid AI",
    page_icon="🌱",
    layout="centered",
)


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
            use_container_width=True,
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
    use_container_width=True,
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

    else:

        st.success("Image ready for analysis.")

        with st.container(border=True):
            st.markdown("### AI analysis placeholder")

            st.write(f"**Category:** {category_name}")
            st.write(f"**Type:** {selected_type}")

            if symptoms.strip():
                st.write("**Farmer's description:**")
                st.write(symptoms)

            st.info(
                "The image has been received successfully. "
                "A vision-capable AI model will be connected here "
                "in the next development stage."
            )

else:

    st.markdown(
        """
        <div class="diagnosis-box">
            <div class="diagnosis-heading">
                Diagnosis results will appear here
            </div>

            After AI integration, this section will contain:
            <br><br>

            • Possible condition<br>
            • Confidence level<br>
            • Symptoms detected in the image<br>
            • Recommended safe next steps<br>
            • Advice on whether expert help is recommended
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# EXPERT HELP
# --------------------------------------------------

st.divider()

st.subheader("👨‍🌾 Get Expert Help")

st.write(
    "If the farmer needs additional assistance, AgroAid AI will allow "
    "the case to be sent to an agricultural specialist."
)

expert_help = st.button(
    "Request Expert Help",
    use_container_width=True,
)


if expert_help:

    if uploaded_file is None:

        st.warning(
            "Please add an image before requesting expert help."
        )

    elif selected_type.startswith("Select"):

        st.warning(
            f"Please select a {category_name.lower()} type first."
        )

    else:

        st.info(
            "Expert request feature is ready for backend integration. "
            "No request has been sent yet."
        )


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