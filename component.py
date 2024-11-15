import streamlit as st
from PIL import Image
import base64

def get_base64_of_bin_file(bin_file):
    """
    Function to encode local file (image or gif) to base64 string
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def page_style():
    # Encode the local image to base64
    sidebar_image_base64 = get_base64_of_bin_file('assets/backgrounds/puzzle_sidebar_background.jpg')

    # Apply custom styles, including the sidebar background image
    custom_style = f"""
        <style>
            /* Hide Streamlit default elements */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}

            /* Sidebar background with a dark overlay */
            [data-testid="stSidebar"] > div:first-child {{
                background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                url("data:image/jpg;base64,{sidebar_image_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: local;
            }}

            /* Adjust header and toolbar */
            [data-testid="stHeader"] {{
                background: rgba(0,0,0,0);
            }}

            [data-testid="stToolbar"] {{
                right: 2rem;
            }}

            /* Button styles */
            .stButton>button {{background-color: #FFA500; color: white !important;}}
            .stDownloadButton>button {{background-color: #FFA500; color: white !important;}}

            /* Custom card styles */
            .cert-card {{
                background-color: #333333;
                color: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .cert-card:hover {{
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            }}
        </style>
    """
    
    # Set the page configuration with a custom icon
    icon = Image.open('photos/rubiks.jpg')
    st.set_page_config(page_title="MasterMind Puzzle", page_icon=icon, layout="wide")

    # Apply custom styles to the page
    st.markdown(custom_style, unsafe_allow_html=True)

    # Display the main background image (optional)
    image = Image.open('assets/backgrounds/main_puzzle_background.png')
    st.image(image)

    # Sidebar content
    with st.sidebar:
        # Display the round profile picture at the top of the sidebar
        st.image("photos/Round_Profile_Photo.png", width=100)

        st.markdown("""
            ## MindForge Puzzle Game 🧩
        """)

        st.markdown("""
        ### About the Game
        **MindForge Puzzle** is an interactive word search game designed to help you learn and master new topics through engaging gameplay. Enter a topic, generate a puzzle, and find the hidden words related to your chosen subject!

        ### Features
        - **Dynamic Word Generation**: Words are fetched from Wikipedia summaries based on your chosen topic.
        - **Customizable Difficulty**: Adjust the number of words and grid size to change the difficulty level.
        - **Interactive Gameplay**: Select words by entering coordinates and receive immediate feedback with sounds and highlights.
        - **Educational Focus**: Enhance your vocabulary and understanding of various topics while having fun.
        """)

        # Button to play background music in a new tab
        new_tab_button = """
        <a href="https://youtu.be/kx5N2TeDqNM?si=-sCwGJpuKLQ1PFO6" target="_blank">
            <button style="background-color: #FFA500; color: white; border: none; padding: 10px 20px; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px;">
                🎵 Play Background Music
            </button>
        </a>
        """
        st.markdown(new_tab_button, unsafe_allow_html=True)

        st.markdown("""---""")

        st.markdown("""
        ### About the Developer
        Hi! I'm **Fahmi Zainal**, a passionate data scientist and developer who enjoys creating interactive applications that combine learning and fun.

        Feel free to connect with me on LinkedIn or check out my other projects on GitHub!
        """)

        # LinkedIn button with logo
        linkedin_url = "https://www.linkedin.com/in/fahmizainal17"
        st.markdown(f"""
            <a href="{linkedin_url}" target="_blank">
                <button style="background-color: #0077B5; color: white; border: none; padding: 10px 20px; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="16" style="vertical-align: middle;"> Connect on LinkedIn
                </button>
            </a>
        """, unsafe_allow_html=True)

        # GitHub button with logo
        github_url = "https://github.com/fahmizainal17"
        st.markdown(f"""
            <a href="{github_url}" target="_blank">
                <button style="background-color: #333; color: white; border: none; padding: 10px 20px; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="16" style="vertical-align: middle;"> Check out my GitHub
                </button>
            </a>
        """, unsafe_allow_html=True)
