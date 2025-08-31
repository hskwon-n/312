responseNAT=ec2.create_nat_gateway(
    AllocationId=EIP,
    SubnetId=publicsubs[0]
)
NatID=responseNAT['NatGateway']['NatGatewayId']
print(NatID)