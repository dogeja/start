import os
import json
import webbrowser
import shutil
from datetime import datetime, timedelta
import re

def update_date_in_filename(filename):
    match = re.search(r'\((\d{8})\)', filename)
    if match:
        date_str = match.group(1)
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        today = datetime.today()
        today_str = today.strftime('%Y%m%d')
        if date_str == today_str:
            return filename
        new_date_obj = date_obj + timedelta(days=1)
        new_date_str = new_date_obj.strftime('%Y%m%d')
        new_filename = filename[:match.start(1)] + new_date_str + filename[match.end(1):]
        return new_filename
    else:
        return filename

def run_on_startup():
    settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # URL 열기
        for url in settings.get('urls', []):
            webbrowser.open(url)
        
        # 폴더 내 파일 처리
        folder_path = settings.get('folder', '')
        if folder_path:
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if files:
                most_recent_file = max(files, key=os.path.getmtime)
                new_file_name = os.path.join(folder_path, update_date_in_filename(os.path.basename(most_recent_file)))
                shutil.copy2(most_recent_file, new_file_name)
                print(f"Duplicated file: {most_recent_file} to {new_file_name}")
                os.startfile(new_file_name)
                os.startfile(folder_path)