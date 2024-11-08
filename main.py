from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import polish_meds
import dynamodb_utils


url = "https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/5.0.0/overall.xml"
file_path = "./downloaded_files/meds_list.xml"

app = Flask(__name__)

textract_client = boto3.client("textract", region_name="eu-west-3")
dynamodb = boto3.resource("dynamodb", region_name="eu-west-3")
print(dynamodb)
table = dynamodb.Table("Medicine")
print(table)

polish_meds.download_file(url, file_path)
list_of_meds = polish_meds.get_meds(file_path)


@app.route("/upload/", methods=["POST"])
async def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        response = textract_client.detect_document_text(Document={"Bytes": file.read()})

        extracted_text = []
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                extracted_text.append(item["Text"])

        texttract_results = set(word.lower() for word in extracted_text)

        matched_med = polish_meds.match_meds(texttract_results, list_of_meds)
        dynamodb_utils.put_med_into_db(table, matched_med)

        return jsonify({"matched_meds": matched_med})

    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not availabke"}), 403
    except ClientError as e:
        return jsonify({"error": e.response["Error"]["Message"]}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
