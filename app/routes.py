from flask import Blueprint, request, jsonify
from botocore.exceptions import NoCredentialsError, ClientError
from app.services.textract_service import extract_text_from_image
from app.services.dynamodb_service import put_med_into_db
import polish_meds

bp = Blueprint("routes", __name__)


@bp.route("/upload/", methods=["POST"])
async def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        extracted_text = extract_text_from_image(file)
        matched_med = polish_meds.match_meds(extracted_text, polish_meds.get_meds())
        put_med_into_db(matched_med)

        return jsonify({"matched_meds": matched_med})

    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not availabke"}), 403
    except ClientError as e:
        return jsonify({"error": e.response["Error"]["Message"]}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
