import os
import json
import webbrowser
import shutil
from datetime import datetime, timedelta
import re
import requests
import sys
import subprocess
from PyQt5.QtWidgets import QMessageBox

def safe_copy(src, dst):
    try:
        if os.path.exists(dst):
            return False, "해당 파일이 이미 존재합니다."
        shutil.copy2(src, dst)
        return True, "파일이 성공적으로 복사되었습니다."
    except Exception as e:
        return False, str(e)

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

def check_for_updates(current_version):
    try:
        response = requests.get('https://api.github.com/repos/dogeja/start/releases/latest')
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            return latest_version > current_version, latest_version
        else:
            print(f"API request failed with status code: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, None

def download_update(version):
    url = f'https://github.com/dogeja/start/releases/download/v{version}/환실련의아침.exe'
    response = requests.get(url)
    if response.status_code == 200:
        current_exe = sys.executable
        temp_exe = current_exe + '.new'
        with open(temp_exe, 'wb') as f:
            f.write(response.content)
        return True
    return False

def apply_update():
    current_exe = sys.executable
    temp_exe = current_exe + '.new'
    
    batch_content = f'''
@echo off
:loop
tasklist | find /i "{os.path.basename(current_exe)}" > nul
if errorlevel 1 (
    move /y "{temp_exe}" "{current_exe}"
    start "" "{current_exe}"
    del "%~f0"
) else (
    timeout /t 1 > nul
    goto loop
)
'''
    
    with open('update.bat', 'w') as f:
        f.write(batch_content)
    
    subprocess.Popen('update.bat', shell=True)
    sys.exit()

def check_settings_compatibility(settings_file, new_version):
    with open(settings_file, 'r') as f:
        settings = json.load(f)
    
    # 필요한 경우 여기에 설정 업데이트 로직 추가
    
    with open(settings_file, 'w') as f:
        json.dump(settings, f)

def process_folder(folder_path, show_notification_func=None):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if files:
        most_recent_file = max(files, key=os.path.getmtime)
        new_file_name = os.path.join(folder_path, update_date_in_filename(os.path.basename(most_recent_file)))
        success, message = safe_copy(most_recent_file, new_file_name)
        if success:
            print(f"Duplicated file: {most_recent_file} to {new_file_name}")
            os.startfile(new_file_name)
        else:
            print(message)
            if show_notification_func:
                show_notification_func("파일 복사", message)
        os.startfile(folder_path)

def run_startup_tasks():
    settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # URL 열기
        urls = settings.get('urls', [])
        if urls:
            chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
            webbrowser.get(chrome_path).open_new(urls[0])  
            for url in urls[1:]:
                webbrowser.get(chrome_path).open_new_tab(url)      
                    
        # 폴더 내 파일 처리
        folder_path = settings.get('folder', '')
        if folder_path:
            process_folder(folder_path)

def cleanup_temp_files():
    current_exe = sys.executable
    temp_exe = current_exe + '.new'
    if os.path.exists(temp_exe):
        try:
            os.remove(temp_exe)
        except:
            pass
    if os.path.exists('update.bat'):
        try:
            os.remove('update.bat')
        except:
            pass