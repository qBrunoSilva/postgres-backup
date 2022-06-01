import boto3
import os
from dotenv import load_dotenv

load_dotenv()

FOLDER_NAME = os.environ.get("AWS_FOLDER_NAME")
BACKUP_DIR = os.environ.get("BACKUP_DIR")
 
class SendS3():
    def __init__(self) -> None:
        self.bucket_name = os.environ.get("AWS_BUCKET_NAME")
        self.access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

        self.session = boto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key
        )

        self.s3 = self.session.resource('s3')

    def upload_file(self, path_file):

        result = self.s3.Object(
            self.bucket_name, f"{FOLDER_NAME}/{path_file}").put(Body=open(f"{BACKUP_DIR}/{path_file}", "rb"))
        response = result.get('ResponseMetadata')

        if response.get('HTTPStatusCode') == 200:
            return True
        else:
            return False


