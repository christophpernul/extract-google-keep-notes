"""
Preprocesses exported Google Keep notes, converts them to markdown, groups them
into labels and stores a markdown file for each label.
"""
import json
import os
import glob
from pathlib import Path

DATA_BASE_PATH = "data/Keep/"


def load_json_files(directory):
    all_data = []  # List to store all data

    # Use glob to find all json files in the directory
    for filepath in glob.glob(directory + '/*.json'):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            all_data.append(data)  # Append data to the list

    return all_data


def convert_to_markdown(note):
    content = ""
    if note.text:  # If the note is a text note
        content += note.text + "\n\n"
    if note.bulleted_list:  # If the note contains a bulleted list
        for item in note.items:
            content += f"- {'[x]' if item.checked else '[ ]'} {item.text}\n"
    return content


def extract_valid_notes(note_list: []) -> []:
    """Drop all notes with isTrashed: True and isArchived: True"""
    note_list = list(filter(lambda x: x["isTrashed"] is False, note_list))
    note_list = list(filter(lambda x: x["isArchived"] is False, note_list))
    return note_list

def extract_lables(note_list: []) -> []:
    """Extract labels from note"""

def main():
    note_list = load_json_files(DATA_BASE_PATH)
    note_list = extract_valid_notes(note_list)

    # Check for duplicate labels!
    all_labels = [len(d["labels"]) for d in note_list if "labels" in d]
    assert all([d == 1 for d in all_labels]) is True, "Duplicate Labels found!"
    double_labels = [d["title"] for d in note_list if "labels" in d and len(d["labels"])>1]

    # Extract labels
    # Convert content to markdown lists
    # Combine notes per label into single document
    # Store notes per label

    print(all_labels)

if __name__ == "__main__":
    main()