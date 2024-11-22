import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb", region_name="eu-west-3")
table = dynamodb.Table("Medicine")


def put_med_into_db(med):
    highest_id = get_highest_id(table)

    if highest_id is None:
        raise Exception("Failed to retrieve highest medicine_id")

    new_med_id = highest_id + 1

    medicine_data = {"medicine_id": new_med_id, "medicine_name": med}

    try:
        table.put_item(Item=medicine_data)
        return {"status": "success", "message": "New med added"}

    except ClientError as e:
        return {"status": "error", "message": e.response["Error"]["Message"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_highest_id(table):
    try:
        response = table.scan()
        items = response.get("Items", [])

        if not items:
            return 0

        max_id = max(item["medicine_id"] for item in items if "medicine_id" in item)
        return max_id

    except ClientError as e:
        print(f"Error fetching items: {e.response['Error']['Message']}")
        return None
