import boto3
import os

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define the bucket nameclear
bucket_name = 'prem-s3-static-bucket'

# Specify the region for the bucket
region = 'us-west-2'  # Replace with your desired region

# Create the S3 bucket with region specified
s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})

print(f'S3 bucket "{bucket_name}" created successfully in region "{region}"!')


# Specify the directory containing static files
static_files_directory = '/Users/pkumar23/prem4eru/Monitorning_Scaling_Automation/staticwebpage'

# Initialize the S3 resource
s3_resource = boto3.resource('s3')

# Upload static files to S3 bucket
for file_name in os.listdir(static_files_directory):
    file_path = os.path.join(static_files_directory, file_name)
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, file_name)
    print(f"Uploaded '{file_name}' to S3 bucket '{bucket_name}'.")

print("Static files uploaded successfully.")