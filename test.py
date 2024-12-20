import requests
import pandas as pd
from dotenv import load_dotenv
import json
from pprint import pprint
from datetime import datetime, timedelta
import re
import os

load_dotenv()
api_key = os.getenv("EDINET_API_KEY")

def get_reports_for_date_range(start_date, end_date):

    url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"

    reports = []

    current_date = start_date
    while current_date <= end_date:
        # リクエストパラメータ
        params = {
            'date': current_date.strftime('%Y-%m-%d'),  # YYYY-MM-DD形式
            'type': 2,  # 有価証券報告書
            'Subscription-Key': api_key
        }
        
        # APIリクエスト
        response = requests.get(url, params=params)

        include_pattern = r"新規公開"
        exclude_pattern = r"訂正"

        if response.status_code == 200:
            data = response.json()
            
            # docDesctiptionに「新規公開」が含まれているもののみ抽出
            for doc in data.get('results', []):
                text = doc.get('docDescription', '')
                if isinstance(text, str) and re.search(include_pattern, text) and not re.search(exclude_pattern, text):
                    reports.append({
                        # 'docID': doc['docID'],
                        'filerName': doc['filerName'],
                        'submitDateTime': doc['submitDateTime'],
                        'docDescription': text
                    })
        else:
            print(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")
        
        # 日付を1日進める
        current_date += timedelta(days=1)
    
    if reports:
        pprint(reports)
    else:
        print(f"{start_date.strftime('%Y-%m-%d')} から {end_date.strftime('%Y-%m-%d')} の期間には新規公開（IPO）に関する有価証券報告書が見つかりませんでした。")

# 日付範囲を指定（2024年4月1日から2024年6月30日）
start_date = datetime(2024, 12, 6)
end_date = datetime(2024, 12, 8)

# 指定された日付範囲で報告書を取得
get_reports_for_date_range(start_date, end_date)
#     while current_date <= end_date:

#         params = {
#             'date': current_date.strftime('%Y-%m-%d'),
#             'type': 2,
#             "Subscription-Key": api_key
#         }
#         raw_response = requests.get(url, params=params)

#         if raw_response.status_code == 200:
#             data = raw_response.json()
#         else:
#             print(f"APIリクエストに失敗しました。ステータスコード： {raw_response.status_code}")
#         current_date += timedelta(days=1)
#     print(reports)

# start_date = datetime(2024, 4, 1)
# end_date = datetime(2024, 6, 30)

# get_reports_for_date_range(start_date, end_date)
# data = json.dumps(json_response, indent=4, ensure_ascii=False)
# print(data["filerName"])
# print(json_response)

# documents = json_response['results']
# df = pd.DataFrame(documents)
# pd.set_option("display.max_rows", None)
# df_filtered = df[['filerName', 'docDescription']]
# print(df_filtered)

