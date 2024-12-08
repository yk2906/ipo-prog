from pprint import pprint
from datetime import datetime
import requests
import re
import os

# GitHub Actionsの環境変数からAPIキーとWebhook URLを取得
api_key = os.getenv("EDINET_API_KEY")
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

if not api_key or not slack_webhook_url:
    raise EnvironmentError("EDINET_API_KEYまたはSLACK_WEBHOOK_URLが環境変数から取得できません。")

def send_to_slack(message):
    payload = {"text": message}
    try:
        response = requests.post(slack_webhook_url, json=payload)
        if response.status_code != 200:
            print(f"Slackへの送信に失敗しました。ステータスコード: {response.status_code}")
            print("レスポンス内容:", response.text)  # 詳細なエラー内容をログ出力
        else:
            print("Slackにメッセージを送信しました。")
    except requests.exceptions.RequestException as e:
        print(f"Slack送信中にエラーが発生しました: {e}")

def get_reports_for_today():
    # APIのURL
    url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"

    # 本日の日付を取得
    today = datetime.now().date()

    # リクエストパラメータとヘッダー
    params = {
        'date': today.strftime('%Y-%m-%d'),  # YYYY-MM-DD形式
        'type': 2,  # 有価証券報告書
        'Subscription-Key': api_key
    }
    headers = {
        'Subscription-Key': api_key
    }

    # APIリクエスト
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            reports = []

            # docDescriptionに「新規公開」が含まれているもののみ抽出
            include_pattern = r"新規公開"
            exclude_pattern = r"訂正"

            for doc in data.get('results', []):
                text = doc.get('docDescription', '')
                if isinstance(text, str) and re.search(include_pattern, text) and not re.search(exclude_pattern, text):
                    reports.append({
                        'filerName': doc['filerName'],
                        'submitDateTime': doc['submitDateTime'],
                        'docDescription': text
                    })

            # メッセージ生成
            if reports:
                message = f"{today.strftime('%Y-%m-%d')} の新規公開（IPO）に関する有価証券報告書:\n"
                for report in reports:
                    message += f"- {report['filerName']} ({report['submitDateTime']}): {report['docDescription']}\n"
            else:
                message = f"{today.strftime('%Y-%m-%d')} には新規公開（IPO）に関する有価証券報告書が見つかりませんでした。"

            send_to_slack(message)

        else:
            print(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")
            print("レスポンス内容:", response.text)  # エラー内容をログ出力

    except requests.exceptions.RequestException as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")

# 本日の日付で報告書を取得
if __name__ == "__main__":
    get_reports_for_today()
