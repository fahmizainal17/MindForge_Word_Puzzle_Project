import streamlit as st
import wikipediaapi
import random
import string
import numpy as np
import pandas as pd
import streamlit.components.v1 as components

# Function to retrieve words related to a topic from Wikipedia
def get_topic_words(topic, num_words):
    """
    Fetch related words from Wikipedia for the given topic.
    """
    # Create the Wikipedia object with the language set to 'en' and a custom user-agent
    wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='MindForgeWordPuzzle/1.0 (fahmizainal@invokeisdata.com)'
    )
    
    page = wiki.page(topic)
    if not page.exists():
        return []
    
    # Get words by splitting the summary text of the Wikipedia page
    words = list(set(page.summary.split()))
    filtered_words = [
        word.strip(string.punctuation) for word in words 
        if word.isalpha() and len(word) > 3
    ]
    random.shuffle(filtered_words)
    
    return [word.upper() for word in filtered_words[:num_words]]

# Function to play sound using base64 encoding
def play_sound(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64_encoded = base64.b64encode(data).decode()
    md = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64_encoded}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# Function to create a word search puzzle grid
def create_word_search(words, grid_size=15):
    grid = np.full((grid_size, grid_size), '', dtype='<U1')
    # All possible directions (8 directions)
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1),
                  (-1, 0), (0, -1), (-1, -1), (1, -1)]
    
    def place_word(word):
        word_len = len(word)
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            row, col = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
            dir_r, dir_c = random.choice(directions)
            end_r = row + dir_r * (word_len - 1)
            end_c = col + dir_c * (word_len - 1)
            if 0 <= end_r < grid_size and 0 <= end_c < grid_size:
                can_place = True
                for i in range(word_len):
                    new_r = row + i * dir_r
                    new_c = col + i * dir_c
                    if grid[new_r, new_c] != '' and grid[new_r, new_c] != word[i]:
                        can_place = False
                        break
                if can_place:
                    for i in range(word_len):
                        new_r = row + i * dir_r
                        new_c = col + i * dir_c
                        grid[new_r, new_c] = word[i]
                    placed = True
            attempts += 1
            
    for word in words:
        place_word(word)
    
    # Fill in the empty spaces with random letters
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r, c] == '':
                grid[r, c] = random.choice(string.ascii_uppercase)
    
    return grid

# Function to extract word from grid based on coordinates
def extract_word_from_grid(grid, start_row, start_col, end_row, end_col):
    word = ''
    positions = []
    delta_row = end_row - start_row
    delta_col = end_col - start_col

    length = max(abs(delta_row), abs(delta_col))
    if length == 0:
        return None, None  # Start and end coordinates are the same
    dir_row = (delta_row) // length
    dir_col = (delta_col) // length

    if (delta_row != dir_row * length) or (delta_col != dir_col * length):
        return None, None  # Not a straight line

    for i in range(length + 1):
        r = start_row + i * dir_row
        c = start_col + i * dir_col
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            word += grid[r][c]
            positions.append((r, c))
        else:
            return None, None  # Out of bounds
    return word, positions

# Function to display the grid as a DataFrame with indices
def display_grid_with_indices(grid, found_positions):
    grid_size = len(grid)
    # Create a DataFrame from the grid
    df = pd.DataFrame(grid)
    # Adjust indices to be 1-based to match the grid display
    df.index = df.index + 1
    df.columns = df.columns + 1

    # Function to highlight found letters
    def highlight_found_letters(data):
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        for r in data.index:
            for c in data.columns:
                row_idx = r - 1  # Adjusting index to match 0-based indices
                col_idx = c - 1
                if (row_idx, col_idx) in found_positions:
                    styles.loc[r, c] = "background-color: #90EE90; font-weight: bold"
        return styles

    styled_df = df.style.apply(highlight_found_letters, axis=None)
    return styled_df

# Function to determine difficulty level
def determine_difficulty(num_words, grid_size):
    if num_words <= 8 and grid_size <= 12:
        return "Beginner"
    elif num_words <= 12 and grid_size <= 16:
        return "Intermediate"
    else:
        return "Hard"

# Function to check if a word is in the list
def check_word(word, word_list):
    return word.upper() in word_list

# Initialize session state variables
if 'words_found' not in st.session_state:
    st.session_state.words_found = []
if 'found_positions' not in st.session_state:
    st.session_state.found_positions = set()
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'grid' not in st.session_state:
    st.session_state.grid = None
if 'words' not in st.session_state:
    st.session_state.words = []
if 'show_words' not in st.session_state:
    st.session_state.show_words = True

# Streamlit UI
st.title("MasterMind Puzzle: Learn and Master Topics through Word Search")
st.write("Enter a topic, select the number of words and grid size, and generate a word search puzzle to master key terms.")

# User inputs for topic, word count, and grid size
topic = st.text_input("Enter a topic:", "Machine Learning")
num_words = st.slider("Number of words:", 1, 20, 5)
grid_size = st.slider("Grid size:", 7, 13, 10)

# Determine difficulty level based on num_words and grid_size
difficulty = determine_difficulty(num_words, grid_size)
st.write(f"**Difficulty Level:** {difficulty}")

if st.button("Generate Puzzle"):
    words = get_topic_words(topic, num_words)
    if words:
        grid = create_word_search(words, grid_size)
        st.session_state.grid = grid
        st.session_state.words = words
        st.session_state.words_found = []
        st.session_state.found_positions = set()
        st.session_state.game_over = False
        st.session_state.show_words = True  # Reset to show words by default
    else:
        st.write("Sorry, couldn't find enough words for this topic. Please try another one.")

if st.session_state.grid is not None:
    grid = st.session_state.grid
    words = st.session_state.words

    # Display the puzzle grid with indices and highlighted found words
    st.write("**Your Word Search Puzzle:**")
    grid_display = display_grid_with_indices(grid, st.session_state.found_positions)
    st.dataframe(grid_display, width=700, height=700)

    # Get user input for word selection
    st.write("**Select a word by entering the coordinates:**")
    col1, col2 = st.columns(2)
    with col1:
        start_row = st.number_input("Start Row (1-based index):", min_value=1, max_value=grid_size, value=1)
        start_col = st.number_input("Start Column (1-based index):", min_value=1, max_value=grid_size, value=1)
    with col2:
        end_row = st.number_input("End Row (1-based index):", min_value=1, max_value=grid_size, value=1)
        end_col = st.number_input("End Column (1-based index):", min_value=1, max_value=grid_size, value=1)

    if st.button("Check Selection"):
        # Convert to 0-based index
        start_row_idx = int(start_row) - 1
        start_col_idx = int(start_col) - 1
        end_row_idx = int(end_row) - 1
        end_col_idx = int(end_col) - 1

        # Validate coordinates
        if (0 <= start_row_idx < grid_size and 0 <= start_col_idx < grid_size and
            0 <= end_row_idx < grid_size and 0 <= end_col_idx < grid_size):
            # Extract the word from grid based on coordinates
            word_selected, positions = extract_word_from_grid(
                grid, start_row_idx, start_col_idx, end_row_idx, end_col_idx
            )
            if word_selected:
                reversed_word = word_selected[::-1]
                if ((check_word(word_selected, words) or check_word(reversed_word, words)) and
                    word_selected not in st.session_state.words_found and
                    reversed_word not in st.session_state.words_found):
                    found_word = word_selected if word_selected in words else reversed_word
                    st.session_state.words_found.append(found_word)
                    st.session_state.found_positions.update(positions)
                    st.success(f"Correct! You found the word: {found_word}")
                    
                    # Play correct sound after user interaction
                    play_sound("assets/correct_sound.mp3")
                elif (word_selected in st.session_state.words_found or reversed_word in st.session_state.words_found):
                    st.warning("You've already found this word.")
                else:
                    st.error("Incorrect selection. Try again!")
                    # Play incorrect sound after user interaction
                    play_sound("assets/incorrect_sound.mp3")
            else:
                st.error("Invalid selection. Words must be in straight lines.")
        else:
            st.error("Coordinates out of bounds.")

    # Now display the word list after updating the session state
    st.session_state.show_words = st.checkbox("Show Words to Find", value=st.session_state.show_words)

    if st.session_state.show_words:
        st.write("**Words to Find:**")
        # Cross out found words
        word_list_display = []
        for word in words:
            if word in st.session_state.words_found:
                word_list_display.append(f"~~{word}~~")
            else:
                word_list_display.append(word)
        st.markdown(", ".join(word_list_display))

    # Check if all words are found
    if len(st.session_state.words_found) == len(words):
        if not st.session_state.game_over:
            st.balloons()
            st.success("Congratulations! You've found all the words!")
            # Play congratulatory sound after user interaction
            play_sound("assets/congratulations_sound.mp3")
            st.session_state.game_over = True
            # Prompt to play again
            st.write("Please click the button below to play again and reinforce your learning.")
            if st.button("Play Again"):
                # Reset the session state
                st.session_state.words_found = []
                st.session_state.found_positions = set()
                st.session_state.game_over = False
                st.session_state.grid = None
                st.session_state.words = []
                st.experimental_rerun()