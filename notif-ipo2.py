import os
import requests
from datetime import datetime
import re

# 環境変数からAPIキーとWebhook URLを取得
api_key = os.getenv("EDINET_API_KEY")
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

def send_to_slack(message):
    payload = {"text": message}
    response = requests.post(slack_webhook_url, json=payload)
    if response.status_code != 200:
        print(f"Slackへの送信に失敗しました。ステータスコード: {response.status_code}")
    else:
        print("Slackにメッセージを送信しました。")

def get_reports_for_today():
    # APIのURL
    url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"

    # 本日の日付を取得
    today = datetime.now().date()

    # リクエストパラメータ
    params = {
        'date': today.strftime('%Y-%m-%d'),  # YYYY-MM-DD形式
        'type': 2,  # 有価証券報告書
    }

    headers = {
        'Subscription-Key': api_key
    }

    # APIキーとWebhook URLの確認
    print(f"EDINET_API_KEY: {api_key}")
    print(f"SLACK_WEBHOOK_URL: {slack_webhook_url}")

    # APIリクエスト
    response = requests.get(url, params=params, headers=headers)

    # リクエストURLとステータスコードの表示
    print(f"リクエストURL: {response.url}")
    print(f"ステータスコード: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        reports = []
        include_pattern = r"新規公開"
        exclude_pattern = r"訂正"

        # docDescriptionに「新規公開」が含まれているもののみ抽出
        for doc in data.get('results', []):
            text = doc.get('docDescription', '')
            if isinstance(text, str) and re.search(include_pattern, text) and not re.search(exclude_pattern, text):
                reports.append({
                    'filerName': doc['filerName'],
                    'submitDateTime': doc['submitDateTime'],
                    'docDescription': text
                })

        if reports:
            message = f"{today.strftime('%Y-%m-%d')} の新規公開（IPO）に関する有価証券報告書:\n"
            for report in reports:
                message += f"- {report['filerName']} ({report['submitDateTime']}): {report['docDescription']}\n"
        else:
            message = f"{today.strftime('%Y-%m-%d')} には新規公開（IPO）に関する有価証券報告書が見つかりませんでした。"

        send_to_slack(message)
    else:
        print(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")
        print(f"レスポンス内容: {response.text}")

if __name__ == "__main__":
    get_reports_for_today()
