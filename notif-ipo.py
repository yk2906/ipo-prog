from dotenv import load_dotenv
from pprint import pprint
from datetime import datetime, timedelta
import requests
import re
import os

# 環境変数の読み込み
load_dotenv()
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

    reports = []

    # リクエストパラメータ
    params = {
        'date': today.strftime('%Y-%m-%d'),  # YYYY-MM-DD形式
        'type': 2,  # 有価証券報告書
        'Subscription-Key': api_key
    }

    headers = {
        'Subscription-Key': api_key
    }

    # APIリクエスト
    response = requests.get(url, params=params, headers=headers)

    include_pattern = r"新規公開"
    exclude_pattern = r"訂正"

    if response.status_code == 200:
        data = response.json()
        
        # docDescriptionに「新規公開」が含まれているもののみ抽出
        for doc in data.get('results', []):
            text = doc.get('docDescription', '')
            if isinstance(text, str) and re.search(include_pattern, text) and not re.search(exclude_pattern, text):
                reports.append({
                    # 必要な情報を抽出
                    'filerName': doc['filerName'],
                    'submitDateTime': doc['submitDateTime'],
                    'docDescription': text
                })
    else:
        print(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")

    # 結果を表示
    # if reports:
    #     pprint(reports)
    # else:
    #     print(f"{today.strftime('%Y-%m-%d')} には新規公開（IPO）に関する有価証券報告書が見つかりませんでした。")

    if reports:
        message = f"{today.strftime('%Y-%m-%d')} の新規公開（IPO）に関する有価証券報告書:\n"
        for report in reports:
            message += f"- {report['filerName']} ({report['submitDateTime']}): {report['docDescription']}\n"
    else:
        message = f"{today.strftime('%Y-%m-%d')} には新規公開（IPO）に関する有価証券報告書が見つかりませんでした。"

    send_to_slack(message)

# 本日の日付で報告書を取得
if __name__ == "__main__":
    get_reports_for_today()
