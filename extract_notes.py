"""
Preprocesses exported Google Keep notes, converts them to markdown, groups them
into labels and stores a markdown file for each label.
"""
import json
import os
import glob
from datetime import datetime
from pathlib import Path

DATA_BASE_PATH = "data/Keep/"
DATA_EXPORT_PATH = "data/output/"
NOTE_KEYS_TO_POP = ["color",
                    "isTrashed",
                    "isPinned",
                    "isArchived",
                    "createdTimestampUsec",
                    ]

def load_json_files(directory):
    all_data = []  # List to store all data

    # Use glob to find all json files in the directory
    for filepath in glob.glob(directory + '/*.json'):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            all_data.append(data)  # Append data to the list

    return all_data


def extract_valid_notes(note_list: []) -> []:
    """Drop all notes with isTrashed: True and isArchived: True"""
    note_list = list(filter(lambda x: x["isTrashed"] is False, note_list))
    note_list = list(filter(lambda x: x["isArchived"] is False, note_list))
    notes_valid = {
        idx: note for idx, note in enumerate(note_list)
    }
    return notes_valid

def group_notes_per_label(notes_valid: {}) -> {}:
    """Extract labels from note"""
    labels = set([note["labels"][0]["name"] for note in notes_valid.values() if "labels" in note] + ["general"])
    notes = {}
    for label in labels:
        notes[label] = []
    for idx, note in notes_valid.items():
        note_label = note.get("labels")[0].get("name") if "labels" in note else "general"
        notes[note_label].append(note)
    return notes


def convert_note_date(unix_timestamp: int) -> str:
    # Convert microseconds to seconds
    timestamp_sec = unix_timestamp / 1000000

    # Convert to datetime and format it
    date_string = datetime.utcfromtimestamp(timestamp_sec).strftime('%Y-%m-%d')
    return date_string


def convert_note_content(note_content: []) -> str:
    content = ""
    for item in note_content:
        if item["isChecked"] is True:
            content += f"- [x] {item['text']}\n"
        elif item["isChecked"] is False:
            content += f"- [ ] {item['text']}\n"
        else:
            print(f"ERROR: Cannot infer if checked item: {note_content}")
    content += "\n"
    return content


def convert_note_to_markdown(label: str, note: {}) -> {}:
    text = ""
    # Set note title
    text += f"## {note['title']}\n\n"

    # Set update date
    updated_at = convert_note_date(note["userEditedTimestampUsec"])
    text += f"Updated at: {updated_at}\n\n"

    # Set content
    if "listContent" in note:
        content_input = note["listContent"]
        content = convert_note_content(content_input)
    else:
        content = note["textContent"]
    text += content

    # Set annotations
    if "annotations" in note:
        annotations = "\n".join(list(map(lambda x: "- " + x["url"] if x["source"] == "WEBLINK" else "", note["annotations"])))
        text += annotations
    text += "\n\n"
    return text


def convert_notes(notes_labeled: {}) -> {}:
    notes_markdown = {}
    for label, note_list in notes_labeled.items():
        label_notes = f"# {label}\n\nExtracted from Google Keep!\n\n"
        for note in sorted(note_list, key=lambda x: x["userEditedTimestampUsec"])[::-1]:
            # Add notes from most recent to oldest into a file
            label_notes += convert_note_to_markdown(label, note)
        notes_markdown[label] = label_notes
    return notes_markdown


def export_notes_as_markdown(notes: {}):
    for label, note in notes.items():
        export_path = f"{DATA_EXPORT_PATH}{label.lower().replace(' ', '_')}.md"
        with open(export_path, 'w', encoding="utf-8") as ofile:
            ofile.write(note)
        print(f"Successfully exported notes to: {export_path}")


def main():
    note_list = load_json_files(DATA_BASE_PATH)
    notes_valid = extract_valid_notes(note_list)

    # Check for duplicate labels!
    all_labels = [len(note["labels"]) for note in notes_valid.values() if "labels" in note]
    assert all([d == 1 for d in all_labels]) is True, "Duplicate Labels found!"
    double_labels = [d["title"] for d in notes_valid.values() if "labels" in d and len(d["labels"])>1]

    notes_labeled = group_notes_per_label(notes_valid)
    notes_markdown = convert_notes(notes_labeled)

    export_notes_as_markdown(notes_markdown)

    print(all_labels)

if __name__ == "__main__":
    main()