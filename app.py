import streamlit as st
import wikipediaapi
import random
import string
import numpy as np
import pandas as pd
import base64
from stop_words import get_stop_words
from component import page_style
from backend import get_topic_words, play_sound, create_word_search, extract_word_from_grid, display_grid_with_indices, determine_difficulty, check_word, is_straight_line

page_style()

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
st.title("MindForge Puzzle: Forge your mind to any topic you want!")
st.write("Enter a topic, select the number of words and grid size, and generate a word search puzzle to master key terms.")

# User inputs for topic, word count, and grid size
topic = st.text_input("Enter a topic:", "Machine Learning")
num_words = st.slider("Number of words:", 1, 20, 2)
grid_size = st.slider("Grid size:", 11, 13, 13)  # Increased max grid size

# Determine difficulty level based on num_words and grid_size
difficulty = determine_difficulty(num_words, grid_size)
st.write(f"**Difficulty Level:** {difficulty}")

if st.button("Generate Puzzle"):
    max_word_length = grid_size  # Maximum word length based on grid size
    words = get_topic_words(topic, num_words, max_word_length)
    if words:
        grid, words_not_placed = create_word_search(words, grid_size)
        # Remove words that couldn't be placed
        words = [word for word in words if word not in words_not_placed]
        st.session_state.grid = grid
        st.session_state.words = words
        st.session_state.words_found = []
        st.session_state.found_positions = set()
        st.session_state.game_over = False
        st.session_state.show_words = True  # Reset to show words by default
        if words_not_placed:
            st.warning(f"The following words could not be placed due to size constraints and have been removed: {', '.join(words_not_placed)}")
    else:
        st.write("Sorry, couldn't find enough words for this topic. Please try another one.")

if st.session_state.grid is not None:
    grid = st.session_state.grid
    words = st.session_state.words

    # Get user input for word selection
    st.write("**Select a word by entering the coordinates:**")
    col1, col2 = st.columns(2)
    with col1:
        start_row = st.number_input("Start Row (1-based index):", min_value=1, max_value=grid_size, value=1)
        start_col = st.number_input("Start Column (1-based index):", min_value=1, max_value=grid_size, value=1)
    with col2:
        end_row = st.number_input("End Row (1-based index):", min_value=1, max_value=grid_size, value=1)
        end_col = st.number_input("End Column (1-based index):", min_value=1, max_value=grid_size, value=1)

    # Process the selection
    check_selection = st.button("Check Selection")
    if check_selection:
        # Convert to 0-based index
        start_row_idx = int(start_row) - 1
        start_col_idx = int(start_col) - 1
        end_row_idx = int(end_row) - 1
        end_col_idx = int(end_col) - 1

        # Validate coordinates
        if (0 <= start_row_idx < grid_size and 0 <= start_col_idx < grid_size and
            0 <= end_row_idx < grid_size and 0 <= end_col_idx < grid_size):

            # Check if the selection forms a straight line (horizontal, vertical, or diagonal)
            if is_straight_line(start_row_idx, start_col_idx, end_row_idx, end_col_idx):
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
                    # Play incorrect sound after user interaction
                    play_sound("assets/incorrect_sound.mp3")
            else:
                st.error("Invalid selection. Words must be in straight lines.")
                # Play incorrect sound after user interaction
                play_sound("assets/incorrect_sound.mp3")
        else:
            st.error("Coordinates out of bounds.")
            # Play incorrect sound after user interaction
            play_sound("assets/incorrect_sound.mp3")

    # Display the puzzle grid with indices and highlighted found words
    st.write("**Your Word Search Puzzle:**")
    grid_display = display_grid_with_indices(grid, st.session_state.found_positions)
    st.dataframe(grid_display, width=700, height=700)

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
