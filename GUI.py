import streamlit as st
import base64

def set_background(image_file):
    """Sets the background of the Streamlit app to an image."""
    with open(image_file, "rb") as f:
        img_data = f.read()
    b64_encoded = base64.b64encode(img_data).decode()
    style = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64_encoded});
            background-size: cover;
            color: white; /* Set default text color to white */
        }}

        /* White text for input labels */
        .stTextInput > label {{
            color: white !important;
        }}
        .stNumberInput > label {{
            color: white !important;
        }}
        .stTextArea > label {{
            color: white !important;
        }}

        /* White text for selectbox labels */
        .stSelectbox > label {{
            color: white !important;
        }}

        /* White text for radio button labels */
        .stRadio > label {{
            color: white !important;
        }}

        /* Make written content white */
        p, li, span, div, h1, h2, h3, h4, h5, h6 {{
            color: white;
            text-shadow: 1px 1px 2px black; /* Add a subtle shadow for better readability */
        }}

        /* Style the Suggest button */
        div.stButton > button:first-child {{
            color: white !important;
            background-color: transparent !important;
            border: 1px solid white !important; /* Optional: Add a white border */
        }}

        /*Button hover effect*/
        div.stButton > button:first-child:hover {{
            background-color: rgba(255, 255, 255, 0.2) !important; /* White with transparency */
            color: black !important; /* Text color on hover */
        }}

        /* Label hover effect*/
        label:hover {{
           color: #ADD8E6; /* Example: Light blue on hover */
           cursor: pointer;
        }}

        </style>
    """
    st.markdown(style, unsafe_allow_html=True)


set_background('meow.jpg')  # Ensure this path is correct

# Set the title of the app
st.markdown("<h1 style='color:white;'>Movie Recommender</h1>", unsafe_allow_html=True)

# Ask for the user's name using a text input
st.markdown("<p style='color:white;'>What is your name?</p>", unsafe_allow_html=True)
user_name = st.text_input("")

# (Optional) Display a greeting using the user's name, but only if a name is entered.
if user_name:
    st.markdown(f"<p style='color:white;'>Hello, {user_name}! Welcome to the Movie Recommender.</p>", unsafe_allow_html=True)

# Movie type input with a suggest button in line
col1, col2 = st.columns([3, 1])  # Create two columns with a 3:1 width ratio

with col1:
    st.markdown("<p style='color:white;'>What type of movie do you want?</p>", unsafe_allow_html=True)
    movie_type = st.text_input("", key="movie_type_input")

with col2:
    if st.button("Suggest", key="suggest_button"):
        # Suggestion logic goes here (replace with your actual suggestion code)
        suggestions = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror"]
        st.markdown(f"<p style='color:white;'>Here are some suggestions: {', '.join(suggestions)}</p>", unsafe_allow_html=True)

# Display boxes side by side
col3, col4 = st.columns([1, 1])  # Create two columns with equal width

with col3:
    st.markdown("<h2 style='color:white;'>Suggestions</h2>", unsafe_allow_html=True)
    if movie_type:
        st.markdown(f"<p style='color:white;'>Suggestions based on {movie_type}:</p>", unsafe_allow_html=True)
        # Display movie suggestions here (replace with your actual data)
        st.markdown("<p style='color:white;'>- Movie 1</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:white;'>- Movie 2</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:white;'>- Movie 3</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:white;'>Enter a movie type to get suggestions.</p>", unsafe_allow_html=True)

with col4:
    st.markdown("<h2 style='color:white;'>Sort</h2>", unsafe_allow_html=True)
    sort_options = ["Title", "Rating", "Popularity"]
    st.markdown(f"<p style='color:white;'>Sorting by:</p>", unsafe_allow_html=True)
    sort_by = st.selectbox("  ", sort_options, key="sort_selectbox") # Added whitespace to overwrite pre-existing text

# Example Recommendation (replace with your actual recommendation logic)
if user_name and movie_type:
    st.markdown(f"<p style='color:white;'>Okay, {user_name}, you want a {movie_type} movie. Based on that, I recommend...</p>", unsafe_allow_html=True)