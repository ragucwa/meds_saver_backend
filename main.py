import tracemalloc
from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import polish_meds
import dynamodb_utils
import cProfile
import pstats


url = "https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/5.0.0/overall.xml"
file_path = "./downloaded_files/meds_list.xml"

app = Flask(__name__)


def profiled_get_meds():
    return polish_meds.get_meds(file_path)


tracemalloc.start()

textract_client = boto3.client("textract", region_name="eu-west-3")
dynamodb = boto3.resource("dynamodb", region_name="eu-west-3")
table = dynamodb.Table("Medicine")

snapshot_aws_services = tracemalloc.take_snapshot()
top_stats_aws = snapshot_aws_services.statistics("lineno")

print("[ AWS Services Initialization Top memory allocations ]")
for stat in top_stats_aws[:10]:
    print(stat)


polish_meds.download_file(url, file_path)

snapshot_download = tracemalloc.take_snapshot()
top_stats_download = snapshot_download.statistics("lineno")

print("[ Download Top memory allocations ]")
for stat in top_stats_download[:10]:
    print(stat)

profiler = cProfile.Profile()
profiler.enable()
matched_med = profiled_get_meds()
profiler.disable()

profiler.dump_stats("output_file.prof")

p = pstats.Stats("output_file.prof")
p.sort_stats("cumulative").print_stats(10)

snapshot_get_meds = tracemalloc.take_snapshot()
top_stats_get_meds = snapshot_get_meds.statistics("lineno")

print("[ Get Medicines Top memory allocations ]")
for stat in top_stats_get_meds[:10]:
    print(stat)


@app.before_request
def start_trace():
    tracemalloc.start()  # Start tracing memory allocations for requests


@app.after_request
def stop_trace(response):
    snapshot = tracemalloc.take_snapshot()  # Take a memory snapshot
    top_stats = snapshot.statistics("lineno")  # Get line statistics

    print("[ Request Top memory allocations ]")
    for stat in top_stats[:10]:  # Display the top 10 memory allocations
        print(stat)

    tracemalloc.stop()  # Stop tracing for the request


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
