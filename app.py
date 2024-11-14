import streamlit as st
import wikipediaapi
import random
import string
import numpy as np
from streamlit_drawable_canvas import st_canvas

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
    filtered_words = [word.strip(string.punctuation) for word in words if word.isalpha() and len(word) > 3]
    random.shuffle(filtered_words)
    
    return [word.upper() for word in filtered_words[:num_words]]

# Function to create a word search puzzle grid
def create_word_search(words, grid_size=15):
    grid = np.full((grid_size, grid_size), '', dtype='<U1')
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    
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
    delta_row = end_row - start_row
    delta_col = end_col - start_col

    if delta_row == 0 and delta_col != 0:  # Horizontal
        step = 1 if delta_col > 0 else -1
        for c in range(start_col, end_col + step, step):
            word += grid[start_row][c]
    elif delta_col == 0 and delta_row != 0:  # Vertical
        step = 1 if delta_row > 0 else -1
        for r in range(start_row, end_row + step, step):
            word += grid[r][start_col]
    elif abs(delta_row) == abs(delta_col):  # Diagonal
        step_row = 1 if delta_row > 0 else -1
        step_col = 1 if delta_col > 0 else -1
        for i in range(abs(delta_row) + 1):
            r = start_row + i * step_row
            c = start_col + i * step_col
            word += grid[r][c]
    else:
        return None  # Not a valid straight line

    return word

# Function to display the grid
def display_grid(grid):
    grid_display = ""
    for row in grid:
        grid_display += " ".join(row) + "\n"
    return grid_display

# Function to check if a word is in the list
def check_word(word, word_list):
    return word.upper() in word_list

# Streamlit UI
st.title("MasterMind Puzzle: Learn and Master Topics through Word Search")
st.write("Enter a topic, select the difficulty level, and generate a word search puzzle to master key terms.")

# User inputs for topic, word count, and grid size
topic = st.text_input("Enter a topic:", "Machine Learning")
num_words = st.slider("Number of words:", 5, 20, 10)
grid_size = st.slider("Grid size:", 10, 20, 15)

# Difficulty level (show or hide word list)
difficulty = st.selectbox("Choose Difficulty Level:", ["Beginner (Show Words)", "Intermediate (Hide Words)"])
show_words = difficulty == "Beginner (Show Words)"

if 'words_found' not in st.session_state:
    st.session_state.words_found = []

if st.button("Generate Puzzle"):
    words = get_topic_words(topic, num_words)
    if words:
        grid = create_word_search(words, grid_size)
        st.session_state.grid = grid
        st.session_state.words = words
        st.session_state.words_found = []
        st.session_state.game_over = False
    else:
        st.write("Sorry, couldn't find enough words for this topic. Please try another one.")

if 'grid' in st.session_state:
    grid = st.session_state.grid
    words = st.session_state.words

    st.write("**Your Word Search Puzzle:**")
    # Display the puzzle grid
    grid_display = display_grid(grid)
    st.text(grid_display)
    
    if show_words:
        st.write("**Words to Find:**")
        words_remaining = [word for word in words if word not in st.session_state.words_found]
        st.write(", ".join(words_remaining))
    
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
        start_row -= 1
        start_col -= 1
        end_row -= 1
        end_col -= 1
        
        # Validate coordinates
        if (0 <= start_row < grid_size and 0 <= start_col < grid_size and
            0 <= end_row < grid_size and 0 <= end_col < grid_size):
            # Extract the word from grid based on coordinates
            word_selected = extract_word_from_grid(grid, start_row, start_col, end_row, end_col)
            if word_selected:
                if check_word(word_selected, words) and word_selected not in st.session_state.words_found:
                    st.session_state.words_found.append(word_selected)
                    st.success(f"Correct! You found the word: {word_selected}")
                    st.audio('assets/correct_sound.mp3', format='audio/mp3')
                else:
                    st.error("Incorrect selection. Try again!")
                    st.audio('assets/incorrect_sound.mp3', format='audio/mp3')
            else:
                st.error("Invalid selection. Words must be in straight lines.")
        else:
            st.error("Coordinates out of bounds.")

    # Check if all words are found
    if len(st.session_state.words_found) == len(words):
        if not st.session_state.get('game_over', False):
            st.balloons()
            st.success("Congratulations! You've found all the words!")
            st.session_state.game_over = True
