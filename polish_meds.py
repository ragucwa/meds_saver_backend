from data.list_of_meds import list_of_meds as meds


def get_meds():
    return meds


def match_meds(text_for_search: set, list_of_meds: list):
    matched_med = ""

    for medicine in list_of_meds:
        medicine_words = medicine.lower().split()

        if all(word in text_for_search for word in medicine_words):
            matched_med = medicine

    return matched_med
