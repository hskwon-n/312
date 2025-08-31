import boto3
import json
import time

AWS_ACCESS_KEY_ID ="ACCESS KEY"
AWS_SECRET_ACCESS_KEY = "SECRET KEY"
AWS_REGION = input("Region > ")
cidrblock=input("CidrBlock for VPC > ")
ec2 = boto3.client('ec2',  aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION)

#Create VPC
responseVPC = ec2.create_vpc(
    CidrBlock=cidrblock
)
VpcID=responseVPC["Vpc"]["VpcId"]
print(VpcID)
# print(json.dumps(response, indent=3))

#Create Private Subnet
privatesubs=[]
a=int(input("Number of Private Subnets to Create > "))
for i in range(a):
    cidrsubnet=input("CidrBlock for subnet > ")
    azsubnet=input("AvailabilityZone > ")
    responseSubnet=ec2.create_subnet(
        CidrBlock=cidrsubnet,
        VpcId=VpcID,
        AvailabilityZone=azsubnet
    )
    privatesubs.append(responseSubnet["Subnet"]["SubnetId"])
    # print(json.dumps(responseSubnet,indent=3))
print(privatesubs)

#Create Public Subnet
publicsubs=[]
a=int(input("Number of Public Subnets to Create > "))
for i in range(a):
    cidrsubnet=input("CidrBlock for subnet > ")
    azsubnet=input("AvailabilityZone > ")
    responseSubnet=ec2.create_subnet(
        CidrBlock=cidrsubnet,
        VpcId=VpcID,
        AvailabilityZone=azsubnet
    )
    publicsubs.append(responseSubnet["Subnet"]["SubnetId"])
    # print(json.dumps(responseSubnet,indent=3))
print(publicsubs)

#Create IneternetGateway
responseIGW = ec2.create_internet_gateway()
IGWID=responseIGW['InternetGateway']['InternetGatewayId']
print(IGWID)
responseIGW=ec2.attach_internet_gateway(
    InternetGatewayId=IGWID,
    VpcId=VpcID
)
# print(json.dumps(responseIGW,indent=3))

#Create RouteTable-pulic
responseRTpublic=ec2.create_route_table(
    VpcId=VpcID
)
RTpublicID=responseRTpublic['RouteTable']['RouteTableId']
print(RTpublicID)

responseRTpublic=ec2.create_route(#IGT
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=IGWID,
    RouteTableId=RTpublicID
)

for sid in publicsubs:
    responseRTpublic = ec2.associate_route_table(
    RouteTableId=RTpublicID,
    SubnetId=sid
    )
    ec2.modify_subnet_attribute(
        MapPublicIpOnLaunch={
        'Value': True,
        },
        SubnetId=sid
    )


#Create NAT Gateway
responseEIP=ec2.allocate_address()
EIP=responseEIP['AllocationId']
print(EIP)
responseNAT=ec2.create_nat_gateway(
    AllocationId=EIP,
    SubnetId=publicsubs[0]
)

NatID=responseNAT['NatGateway']['NatGatewayId']
print(NatID)


#Create RouteTable-private
responseRTprivate=ec2.create_route_table(
    VpcId=VpcID
)
RTprivateID=responseRTprivate['RouteTable']['RouteTableId']
print(RTprivateID)

while True:
    responseNAT=ec2.describe_nat_gateways(
        NatGatewayIds=[NatID]
    )
    state=responseNAT['NatGateways'][0]['State']
    if state=='available':
        break
    time.sleep(6)

responseRTprivate=ec2.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    NatGatewayId=NatID,
    RouteTableId=RTprivateID
)

for sid in privatesubs:
    responseRTprivate = ec2.associate_route_table(
    RouteTableId=RTprivateID,
    SubnetId=sid
    )



#Create Security Group
responseSG=ec2.create_security_group(
    GroupName='SG',
    Description='SG',
    VpcId=VpcID
)
SgID=responseSG['GroupId']
print(SgID)

