import json
import boto3

s3 = boto3.client('s3')

#replace with your bucket name
bucket_name = 'your_bucket_name'

def setKeyDictionary(key, dict):
    serialized_dict = json.dumps(dict)
    s3.put_object(Bucket=bucket_name, Key=key, Body=serialized_dict.encode('utf-8'))
    print(f"object stored in s3: {serialized_dict}")


def getKeyDictionary(key):
    data = s3.get_object(Bucket=bucket_name, Key=key)
    print(data)
    serialized_data = data['Body'].read().decode('utf-8')
    dict = json.loads(serialized_data)
    print(f"object retreived from s3: {serialized_data}")
    return dict


def setKeyValue(key, value):
    strInt = str(value)
    s3.put_object(Bucket=bucket_name, Key=key, Body=strInt.encode('utf-8'))
    print(f"value stored in s3: {strInt}")
    
def setKeyString(key, value):
    s3.put_object(Bucket=bucket_name, Key=key, Body=value.encode('utf-8'))
    print(f"value stored in s3: value")


def getKeyValue(key):
    data = s3.get_object(Bucket=bucket_name, Key=key)
    strInt = data['Body'].read().decode('utf-8')
    actualInt = int(strInt)
    print(f"value retreived in s3: {actualInt}")
    return actualInt


def getKeyString(key):
    data = s3.get_object(Bucket=bucket_name, Key=key)
    string = data['Body'].read().decode('utf-8')
    print(f"value retreived in s3: {string}")
    return string


def cleanOutBucket():
    objects = s3.list_objects_v2(Bucket=bucket_name)
    for obj in objects.get('Contents', []):
        s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    print(f'All objects in bucket have been deleted.')