import os
import shutil

# Define paths
base_dir = "/home/kasinadhsarma/dr-detection/backend"
train_dir = os.path.join(base_dir, "train")

# List of (filename, label) pairs
files_with_labels = [
    ("10_left.jpeg", 0),
    ("10_right.jpeg", 0),
    ("13_left.jpeg", 1),
    ("13_right.jpeg", 1),
    ("15_left.jpeg", 2),
    ("15_right.jpeg", 2),
    ("16_left.jpeg", 3),
    ("16_right.jpeg", 3),
    ("17_left.jpeg", 4),
    ("17_right.jpeg", 4),
]

# Reorganize files
for filename, label in files_with_labels:
    label_dir = os.path.join(train_dir, f"class_{label}")
    os.makedirs(label_dir, exist_ok=True)  # Create class subdirectory if it doesn't exist
    src_path = os.path.join(train_dir, filename)
    dest_path = os.path.join(label_dir, filename)

    if os.path.exists(src_path):
        shutil.move(src_path, dest_path)  # Move file to class subdirectory
        print(f"Moved {filename} to {label_dir}")
    else:
        print(f"File not found: {src_path}")

print("Reorganization complete.")
