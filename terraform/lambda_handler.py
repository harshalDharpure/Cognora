<<<<<<< HEAD
import json

def handler(event, context):
    print("Cognora Alert Lambda triggered!")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Cognora Lambda!')
    }
=======
import json

def handler(event, context):
    print("Cognora Alert Lambda triggered!")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Cognora Lambda!')
    }
>>>>>>> 23a3f924b5333426fb4b4fb6085453f9515378f8
