import json
import datetime
import base64
from feature_engineering import calculate_features
from s3_writer import write_to_s3
from config import settings


def generate_s3_object_key(event: dict) -> str:
    event_operation_type = event["metadata"]["operation"]
    event_table_name = event["metadata"]["table-name"]
    event_transaction_id = event["metadata"]["transaction-id"]
    current_time = datetime.datetime.now(datetime.UTC).isoformat()
    return f"{event_operation_type}_{event_table_name}_id_{event_transaction_id}_{current_time}"


def is_loan_insert_event(payload_json: dict) -> bool:
    metadata = payload_json.get("metadata", {})
    return metadata.get("table-name") == "loan" and metadata.get("operation") == "insert"


def lambda_handler(event, context):  # pylint: disable=unused-argument
    current_time = datetime.datetime.now(datetime.UTC).isoformat()
    print(f"Current UTC time: {current_time}")
    # Left in for debugging purposes
    print(f"Received event: \n{event}")

    for record in event["Records"]:
        try:
            payload_base64 = record["kinesis"]["data"]
            payload_text = base64.b64decode(payload_base64).decode("utf-8")
            
            print("Decoded Kinesis Payload:")
            payload_json = json.loads(payload_text)
            # For testing purposes, should be removed for production
            payload_json["data"]["client_id"] = 10614
            payload_json["data"]["id"] = 151079
            payload_json["data"]["created_on"] = "2020-06-25"
            print(json.dumps(payload_json, indent=2))

            if not is_loan_insert_event(payload_json):
                print(
                    f"""
                    Skipping event: not a loan/insert. 
                    Table: {payload_json.get('metadata', {}).get('table-name')}, 
                    Operation: {payload_json.get('metadata', {}).get('operation')}
                    """
                )
                continue
            features = calculate_features(payload_json)
            print("Engineered Features:")
            print(json.dumps(features, indent=2))

            s3_object_key = generate_s3_object_key(payload_json)
            write_to_s3(
                features,
                bucket_name=settings.S3_BUCKET_NAME,
                bucket_folder_name=settings.S3_BRONZE_FOLDER_NAME,
                object_key=s3_object_key,
            )
        except json.JSONDecodeError:
            print("Warning: Payload is not valid JSON")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Event received and decoded successfully!", "received_time": current_time}),
    }


# Left in for local testing. As AWS Lambda does not run this part of the code
if __name__ == "__main__":
    with open("test-input/kinesis_test_input.json", "r", encoding="utf-8") as f:
        test_input = f.read().replace("'", '"')
        lambda_handler(json.loads(test_input), None)
