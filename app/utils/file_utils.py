import os
import requests


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
