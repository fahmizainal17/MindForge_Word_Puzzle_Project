import streamlit as st
import wikipediaapi
import random
import string
import numpy as np
import pandas as pd
import base64
from stop_words import get_stop_words

# Function to retrieve words related to a topic from Wikipedia
def get_topic_words(topic, num_words, max_word_length):
    """
    Fetch related words from Wikipedia for the given topic with some randomness
    to provide different words each time.
    Only include words shorter than or equal to max_word_length, avoid stop words,
    and prioritize challenging words.
    """
    stop_words = set(get_stop_words('english'))
    
    wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='MindForgeWordPuzzle/1.0 (your_email@example.com)'
    )
    
    page = wiki.page(topic)
    if not page.exists():
        return []
    
    # Split and clean text
    words = list(set(page.summary.split()))
    filtered_words = [
        word.strip(string.punctuation).lower() for word in words 
        if word.isalpha() and 4 < len(word) <= max_word_length
    ]
    
    # Remove stop words
    filtered_words = [word for word in filtered_words if word not in stop_words]
    
    # Shuffle words to add randomness
    random.shuffle(filtered_words)
    
    # Sort words by length (optional: change order for more randomness)
    filtered_words = sorted(filtered_words, key=lambda x: len(x), reverse=True)
    
    # Temperature-like randomness: select a subset of words with random sampling
    temperature_factor = 30  # Lower values create more randomness; adjust as desired
    num_to_select = int(num_words * temperature_factor)
    selected_words = random.sample(filtered_words, min(num_to_select, len(filtered_words)))
    
    # Ensure unique and formatted output
    selected_words = list(set(selected_words))[:num_words]
    return [word.upper() for word in selected_words]

# Define audio HTML function to embed looping background sound
def play_background_audio(file_path, loop=True):
    loop_attr = "loop" if loop else ""
    with open(file_path, "rb") as f:
        data = f.read()
        b64_encoded = base64.b64encode(data).decode()
    audio_html = f"""
        <audio autoplay {loop_attr} style="display:none;">
            <source src="data:audio/mp3;base64,{b64_encoded}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    
# Function to play sound using base64 encoding
def play_sound(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64_encoded = base64.b64encode(data).decode()
    md = f"""
    <audio autoplay>
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
    
    words_not_placed = []
    
    def place_word(word):
        word_len = len(word)
        placed = False
        attempts = 0
        while not placed and attempts < 1000:  # Increased attempts
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
        return placed  # Return whether the word was placed or not
                
    # Place longer words first
    words = sorted(words, key=len, reverse=True)
    
    for word in words:
        if not place_word(word):
            words_not_placed.append(word)
    
    # Fill in the empty spaces with random letters
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r, c] == '':
                grid[r, c] = random.choice(string.ascii_uppercase)
    
    return grid, words_not_placed

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

def is_straight_line(start_row, start_col, end_row, end_col):
    """
    Checks if the selected coordinates form a straight line.
    Acceptable lines can be horizontal, vertical, or diagonal.
    """
    # Horizontal line (same row)
    if start_row == end_row:
        return True
    # Vertical line (same column)
    elif start_col == end_col:
        return True
    # Diagonal line (difference between rows and columns is the same)
    elif abs(start_row - end_row) == abs(start_col - end_col):
        return True
    else:
        return False
