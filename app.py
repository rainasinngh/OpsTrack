import boto3
from flask import Flask, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

ec2 = boto3.client('ec2', region_name='eu-north-1')
cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')


def get_instance_health():
    instances = ec2.describe_instances()
    instance_health = []
    terminated_instances = []

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            public_ip = instance.get('PublicIpAddress', 'N/A')

            cpu_utilization = get_cpu_utilization(instance_id)

            if state == 'terminated':
                terminated_instances.append(instance_id)

            instance_health.append({
                'InstanceId': instance_id,
                'State': state,
                'PublicIP': public_ip,
                'CPUUtilization': cpu_utilization
            })

    if terminated_instances:
        instance_health.append({
            'Message': 'Some instances were terminated and replaced by Auto Scaling Groups.'
        })

    return instance_health


def get_cpu_utilization(instance_id):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)

    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'cpu_util',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}]  # Fixed incorrect 'value' key
                    },
                    'Period': 300,
                    'Stat': 'Average'
                },
                'ReturnData': True
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
    )

    if response['MetricDataResults']:
        cpu_data = response['MetricDataResults'][0]  # Fixed variable reference
        if cpu_data['Values']:  # Fixed incorrect 'values' key
            return round(cpu_data['Values'][0], 2)

    return 0


@app.route('/')
def health_check():
    instance_health = get_instance_health()
    return render_template('health_check.html', instance_health=instance_health)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

