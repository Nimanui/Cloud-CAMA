# Cloud-CAMA

# Components

## Component Commands
- Create core component:
```bash
sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE \
  -jar ./GreengrassInstaller/lib/Greengrass.jar \
  --aws-region us-east-1 \
  --thing-name Camma_Greengrass_Core \
  --thing-group-name Cama_CarDevice \
  --thing-policy-name Cama_IoT_Policy \
  --tes-role-name GreengrassV2TokenExchangeRole \
  --tes-role-alias-name GreengrassCoreTokenExchangeRoleAlias \
  --component-default-user ggc_user:ggc_group \
  --provision true \
  --setup-system-service true
```

- Check the status:

`sudo systemctl status greengrass.service`


- Clone and prepare the component:
```bash
git clone https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python.git

MY_COMPONENT_NAME=com.cama.car-pubsub-component
cp -Rf aws-greengrass-labs-iot-pubsub-sdk-for-python/samples/gg-pubsub-sdk-component-template $MY_COMPONENT_NAME
cd $MY_COMPONENT_NAME/src
```

## Run emulator
```bash
pip3 install AWSIoTPythonSDK pandas
python3 lab4_emulator_client.py
```

## Track the logs
`sudo tail -f /greengrass/v2/logs/com.cama.car-pubsub-component.log`

# Athena
## Athena Query
```sql
SELECT
  vehicle_id, max_co2,
  partition_0 AS year,
  partition_1 AS month,
  partition_2 AS day,
  partition_3 AS hour
FROM parquet_raw_data LIMIT 10;
```
