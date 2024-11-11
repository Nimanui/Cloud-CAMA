import boto3

iot = boto3.client('iot')

defaultPolicyName = 'Cama_IoT_Policy'
thingGroupName = 'Cama_DeviceGroup'

try:
    response = iot.create_thing_group(thingGroupName=thingGroupName)
except iot.exceptions.ResourceAlreadyExistsException:
    print("Thing Group already exists.")

for device_num in range(5): 
    thingName = f'Cama_CarDevice{device_num}'

    # Create Thing
    try:
        response = iot.create_thing(thingName=thingName)
    except iot.exceptions.ResourceAlreadyExistsException:
        print(f"Thing {thingName} already exists.")
        continue

    # create certificate
    cert_response = iot.create_keys_and_certificate(setAsActive=True)
    certificateArn = cert_response['certificateArn']
    certificateId = cert_response['certificateId']

    # save certificates
    with open(f'certificate{device_num}.pem.crt', 'w') as f:
        f.write(cert_response['certificatePem'])
    with open(f'private{device_num}.pem.key', 'w') as f:
        f.write(cert_response['keyPair']['PrivateKey'])
    with open(f'public{device_num}.pem.key', 'w') as f:
        f.write(cert_response['keyPair']['PublicKey'])

    # attach Policy
    iot.attach_policy(policyName=defaultPolicyName, target=certificateArn)

    
    iot.attach_thing_principal(thingName=thingName, principal=certificateArn)

    # attach group
    iot.add_thing_to_thing_group(
        thingGroupName=thingGroupName,
        thingName=thingName
    )

    print(f"Device {thingName} created and configured.")
