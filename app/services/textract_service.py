import boto3

textract_client = boto3.client("textract", region_name="eu-west-3")


def extract_text_from_image(file):
    response = textract_client.detect_document_text(Document={"Bytes": file.read()})
    extracted_text = [
        item["Text"].lower()
        for item in response["Blocks"]
        if item["BlockType"] == "LINE"
    ]
    return extracted_text
