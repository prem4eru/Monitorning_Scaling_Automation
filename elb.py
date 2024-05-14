import boto3

# Initialize the EC2 client
ec2_client = boto3.client('ec2')

# Create VPC
vpc_response = ec2_client.create_vpc(CidrBlock='172.31.0.0/16')
vpc_id = vpc_response['Vpc']['VpcId']

# Initialize the ELBv2 client
elbv2_client = boto3.client('elbv2')

# Create Subnets
subnet_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock='172.31.16.0/20', AvailabilityZone='us-west-2b')
subnet_id1 = subnet_response['Subnet']['SubnetId']

subnet_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock='172.31.48.0/20', AvailabilityZone='us-west-2a')
subnet_id2 = subnet_response['Subnet']['SubnetId']

# Create Security Group
security_group_response = ec2_client.create_security_group(GroupName='ALBSecurityGroup', Description='ALB Security Group', VpcId=vpc_id)
security_group_id = security_group_response['GroupId']

# Authorize Security Group Ingress (e.g., allow HTTP traffic)
ec2_client.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {'IpProtocol': 'tcp',
         'FromPort': 80,
         'ToPort': 80,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ]
)

# Create Target Group
target_group_response = elbv2_client.create_target_group(
    Name='PremTargetGroup',
    Protocol='HTTP',
    Port=80,
    VpcId=vpc_id
)
target_group_arn = target_group_response['TargetGroups'][0]['TargetGroupArn']

# Create Application Load Balancer
load_balancer_response = elbv2_client.create_load_balancer(
    Name='PremLoadBalancer',
    Subnet1=[subnet_id1],
    Subnet2=[subnet_id2],
    SecurityGroups=[security_group_id],
    Scheme='internet-facing',
    Tags=[{'Key': 'Name', 'Value': 'PremLoadBalancer'}],
    Type='application'
)
load_balancer_arn = load_balancer_response['LoadBalancers'][0]['LoadBalancerArn']

print('Application Load Balancer deployed successfully!')