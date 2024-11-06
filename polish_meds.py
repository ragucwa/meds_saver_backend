import os
import requests
import pandas as pd


def download_file(url: str, file_location: str):
    response = requests.get(url, stream=True)

    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    if response.status_code == 200:
        with open(file_location, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully and saved to {file_location}")
    else:
        print(f"Failed to download the file with {response.status_code}")


def get_meds(file_location: str):
    full_meds_table = pd.read_xml(file_location)
    meds_names_table = full_meds_table["nazwaProduktu"]

    return meds_names_table


def match_meds(text_for_search: set, list_of_meds: pd.Series):
    matched_med = ""

    for medicine in list_of_meds:
        medicine_words = medicine.lower().split()

        if all(word in text_for_search for word in medicine_words):
            matched_med = medicine

    return matched_med
