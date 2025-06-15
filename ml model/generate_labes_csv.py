import os
import csv

# Folder paths
real_folder = "real_medicines"
fake_folder = "fake_medicines"

# Output CSV file
csv_filename = "labels.csv"

with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["filename", "label"])

    # Real medicines
    for fname in os.listdir(real_folder):
        if fname.lower().endswith((".jpg", ".png", ".jpeg")):
            writer.writerow([os.path.join(real_folder, fname), "real"])

    # Fake medicines
    for fname in os.listdir(fake_folder):
        if fname.lower().endswith((".jpg", ".png", ".jpeg")):
            writer.writerow([os.path.join(fake_folder, fname), "fake"])

print(f"✅ CSV file created: {csv_filename}")
