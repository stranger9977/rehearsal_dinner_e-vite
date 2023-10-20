import boto3
import os

s3 = boto3.client('s3', aws_access_key_id='AWS_KEY', aws_secret_access_key='AWS_SECRET_KEY)
bucket_name = 'rehearsaldinnerguets'
csv_filename = 'guests.csv'

def download_csv_from_s3():
        s3.download_file(bucket_name, csv_filename, csv_filename)

def upload_csv_to_s3():
        s3.upload_file(csv_filename, bucket_name, csv_filename)
