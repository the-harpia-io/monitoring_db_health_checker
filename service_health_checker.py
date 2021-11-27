import requests
import argparse
from slack_sdk.webhook import WebhookClient
import ssl

parser = argparse.ArgumentParser()
parser.add_argument("--monitoring_host_ip", help="Monitoring Host IP", type=str)
parser.add_argument("--slack_webhook", help="URL to Slack Webhook", type=str)
args = parser.parse_args()


if args.monitoring_host_ip is None:
    print(f"Monitoring host IP is not specified. Example: \"python3 service_health_checker.py --monitoring_host_ip 10.0.0.12"
          f" --slack_webhook https://hooks.slack.com/services/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\"")
    exit()

if args.slack_webhook is None:
    print(f"Slack webhook URL is not specified. Example: \"python3 service_health_checker.py --monitoring_host_ip 10.0.0.12"
          f" --slack_webhook https://hooks.slack.com/services/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\"")
    exit()


def slack_notification(text):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    webhook = WebhookClient(args.slack_webhook, ssl=ssl_context)

    response = webhook.send(text=text)
    assert response.status_code == 200
    assert response.body == "ok"


def check_grafana():
    try:
        endpoint = f'http://{args.monitoring_host_ip}:3000/api/health'
        request_status = requests.get(
            url=endpoint,
            timeout=30
        ).json()
        print(f"Grafana is available")
    except Exception as error:
        message = f"Grafana is not available\nError: {error}\nHost IP: {args.monitoring_host_ip}"
        slack_notification(message)


def check_kibana():
    try:
        endpoint = f'http://{args.monitoring_host_ip}:5601/api/status'
        request_status = requests.get(
            url=endpoint,
            timeout=30
        ).json()
        print(f"Kibana is available")
    except Exception as error:
        message = f"Kibana is not available\nError: {error}\nHost IP: {args.monitoring_host_ip}"
        slack_notification(message)


def check_elastic():
    try:
        endpoint = f'http://{args.monitoring_host_ip}:9200/_cluster/health'
        request_status = requests.get(
            url=endpoint,
            timeout=30
        ).json()

        if request_status['status'] == 'green':
            print(f"Elastic is available")
        else:
            message = f"Elastic status is not green - {request_status['status']}\nHost IP: {args.monitoring_host_ip}"
            slack_notification(message)
    except Exception as error:
        message = f"Elastic is not available\nError: {error}\nHost IP: {args.monitoring_host_ip}"
        slack_notification(message)


def service_health():
    check_grafana()
    check_kibana()
    check_elastic()


service_health()
