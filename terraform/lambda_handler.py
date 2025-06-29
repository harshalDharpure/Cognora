import json

def handler(event, context):
    print("Cognora Alert Lambda triggered!")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Cognora Lambda!')
    }
