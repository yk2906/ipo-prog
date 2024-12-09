from datetime import datetime

today = datetime.now().date()

print(today.strftime('%Y-%m-%d'))