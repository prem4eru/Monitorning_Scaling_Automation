import boto3
import time

ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

def create_infrastructure():
    # Create VPC
    vpc_response = ec2_client.create_vpc(
        CidrBlock='172.31.0.0/16',
        TagSpecifications=[
            {
                'ResourceType': 'vpc',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'MyVPC'
                    },
                ]
            },
        ]
    )
    vpc_id = vpc_response['Vpc']['VpcId']

    # Create Subnet
    subnet_response = ec2_client.create_subnet(
        AvailabilityZone='us-west-2b',
        CidrBlock='172.31.16.0/20',
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'MySubnet'
                    },
                ]
            },
        ]
    )
    subnet_id = subnet_response['Subnet']['SubnetId']

    # Create Security Group
    security_group_response = ec2_client.create_security_group(
        Description='MySecurityGroup',
        GroupName='MySecurityGroup',
        VpcId=vpc_id
    )
    security_group_id = security_group_response['GroupId']

    # Add Inbound Rule to Security Group
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )

    # Create EC2 Instance
    instance_response = ec2_client.run_instances(
        ImageId='ami-0cf2b4e024cdb6960',  # Change to your desired AMI ID
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        KeyName='tm.pem',  # Change to your key pair name
        SecurityGroupIds=[security_group_id],
        SubnetId=subnet_id
    )
    instance_id = instance_response['Instances'][0]['InstanceId']

    # Create S3 Bucket
    s3_client.create_bucket(
        Bucket='my-unique-bucket-name',
        CreateBucketConfiguration={
            'LocationConstraint': 'us-east-1'
        }
    )

    print("Infrastructure deployed successfully!")
    return vpc_id, subnet_id, security_group_id, instance_id

def update_infrastructure(security_group_id):
    # Update Inbound Rule to Security Group
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )

    print("Security group updated successfully!")

def teardown_infrastructure(vpc_id, subnet_id, security_group_id, instance_id):
    # Terminate EC2 Instance
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    print("EC2 instance terminated successfully!")

    # Delete Security Group
    ec2_client.delete_security_group(GroupId=security_group_id)
    print("Security group deleted successfully!")

    # Delete Subnet
    ec2_client.delete_subnet(SubnetId=subnet_id)
    print("Subnet deleted successfully!")

    # Delete VPC
    ec2_client.delete_vpc(VpcId=vpc_id)
    print("VPC deleted successfully!")

    # Delete S3 Bucket
    s3_client.delete_bucket(Bucket='my-unique-bucket-name')
    print("S3 bucket deleted successfully!")

    print("Infrastructure teardown completed!")

# Deploy infrastructure
vpc_id, subnet_id, security_group_id, instance_id = create_infrastructure()

# Wait for a few seconds for the resources to be ready
time.sleep(10)

# Update infrastructure
update_infrastructure(security_group_id)

# Wait for a few seconds for the update to take effect
time.sleep(10)

# Tear down infrastructure
teardown_infrastructure(vpc_id, subnet_id, security_group_id, instance_id)