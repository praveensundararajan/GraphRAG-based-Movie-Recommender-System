import os
import pandas as pd
import networkx as nx
import nx_arangodb as nxadb
from arango import ArangoClient
import google.generativeai as genai
import streamlit as st
import base64
import re

# Configure Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyACAkSVq9cFUWZNUVaK4H2LyxcGiJeGFqo"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
llm = genai.GenerativeModel("gemini-1.5-flash")

# Connect to ArangoDB
db = ArangoClient(hosts="https://85fe77a05130.arangodb.cloud:8529").db("_system", username="root", password="nCZ147G2z4BeBZAmVDDr", verify=True)

graph_name = "MovieReco"

def load_data():
    """Load user and movie data from CSV files."""
    user_df = pd.read_csv("users.csv")
    movie_df = pd.read_csv("movies.csv")
    
    # Convert date_x to datetime format
    movie_df['date_x'] = pd.to_datetime(movie_df['date_x'], errors='coerce')
    movie_df['movie_id'] = movie_df['movie_id'].astype(str)  # Ensure movie_id is a string
    movie_df['genre'] = movie_df['genre'].str.lower().fillna("")  # Ensure genre is lowercase and not null
    return user_df, movie_df

def build_graph(user_df, movie_df):
    """Construct the graph from user and movie data."""
    G = nx.MultiGraph()
    
    for row in movie_df.itertuples():
        movie_node = f"movie_{row.movie_id}"
        if movie_node not in G:
            G.add_node(
                movie_node, 
                node_type="movie", 
                names=str(row.names), 
                genre=str(row.genre).lower(), 
                crew=str(row.crew).lower() if pd.notna(row.crew) else "", 
                score=float(row.score) if pd.notna(row.score) else None, 
                year=row.date_x.year if pd.notna(row.date_x) else None
            )
    
    for row in user_df.itertuples():
        user_node = f"user_{row.user_id}"
        movie_node = f"movie_{row.movie_id}"
        rating = float(row.user_rating)

        if user_node not in G:
            G.add_node(user_node, node_type="user", user_name=str(row.user_name))

        G.add_edge(user_node, movie_node, relation_type="RATED", rating=rating)
    
    for i, m1 in enumerate(movie_df.itertuples()):
        for j, m2 in enumerate(movie_df.itertuples()):
            if i < j and m1.genre == m2.genre and str(m1.genre) != "":
                G.add_edge(f"movie_{m1.movie_id}", f"movie_{m2.movie_id}", relation_type="SIMILAR")
    
    return G

def upload_graph():
    """Upload the graph to ArangoDB, ensuring it is properly stored."""
    return nxadb.MultiGraph(name=graph_name, db=db)
       

def recommend_movies_by_query(user_id, query, G_adb, movie_df):
    """Generate movie recommendations based on the user's query."""
    if user_id not in G_adb.nodes:
        return ["User not found in database."]
    
    genre_match = re.search(r'\b(horror|comedy|drama|sci-fi|action|thriller)\b', query, re.IGNORECASE)
    genre = genre_match.group(1).lower() if genre_match else None
    
    candidate_movies = [n for n, attr in G_adb.nodes(data=True) if attr.get('node_type') == 'movie']
    
    if genre:
        candidate_movies = [m for m in candidate_movies if genre in G_adb.nodes[m].get('genre', '').lower()]
    
    if not candidate_movies:
        print("DEBUG: No movies found after filtering by genre.")
        return ["No movies found matching your query."]
    
    recommended_movie_ids = [m.replace("MovieReco_node/", "") for m in candidate_movies[:5]]
    print(f"DEBUG: Recommended movie IDs: {recommended_movie_ids}")
    
    recommended_movies = movie_df[movie_df["movie_id"].isin(recommended_movie_ids)]
    movie_names = recommended_movies["names"].tolist()
    
    if not movie_names:
        print("DEBUG: Movie IDs found but no matching names in dataset.")
        return ["No movies found in the dataset after filtering."]
    
    return movie_names

# Initialize data and graph before UI
user_df, movie_df = load_data()
#G = build_graph(user_df, movie_df)
G_adb = upload_graph()

# Check if graph was created successfully
if not G_adb or len(G_adb.nodes) == 0:
    print("Graph upload failed or no nodes were added. Check data consistency.")

# Streamlit UI
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


set_background('meow.jpg') 
st.title("Movie Recommender")

user_id = st.text_input("Enter User ID:")
query = st.text_input("What type of recommendation do you want?")

if st.button("Suggest") and user_id and query:
    if not G_adb or len(G_adb.nodes) == 0:
        st.write("Error: Graph database is empty. Try reloading the data.")
    else:
        recommendations = recommend_movies_by_query(user_id, query, G_adb, movie_df)

        # Build HTML using the custom class
        html_output = """
        <div class="my-box">
            <h3>Recommended Movies:</h3>
        """
        for movie in recommendations:
            html_output += f"<p>- {movie}</p>"
        html_output += "</div>"

        st.markdown(html_output, unsafe_allow_html=True)