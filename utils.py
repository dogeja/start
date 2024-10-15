import os
import json
import webbrowser
import shutil
from datetime import datetime, timedelta
import re
import requests
import sys
import subprocess

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
        with open('환실련의아침_new.exe', 'wb') as f:
            f.write(response.content)
        return True
    return False

def apply_update():
    current_exe = sys.executable
    new_exe = '환실련의아침_new.exe'
    batch_content = f'''
@echo off
:loop
tasklist | find /i "환실련의아침.exe" > nul
if errorlevel 1 (
    move /y "{new_exe}" "{current_exe}"
    start "" "{current_exe}"
    del "%~f0"
    del "환실련의아침_new.exe"
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

def process_folder(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if files:
        most_recent_file = max(files, key=os.path.getmtime)
        new_file_name = os.path.join(folder_path, update_date_in_filename(os.path.basename(most_recent_file)))
        shutil.copy2(most_recent_file, new_file_name)
        print(f"Duplicated file: {most_recent_file} to {new_file_name}")
        os.startfile(new_file_name)
        os.startfile(folder_path)

def run_startup_tasks():
    settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # 업데이트 확인 및 적용
        from version import __version__
        update_available, latest_version = check_for_updates(__version__)
        if update_available:
            if download_update(latest_version):
                check_settings_compatibility(settings_file, latest_version)
                print(f"새 버전 ({latest_version})이 다운로드되었습니다. 업데이트를 적용합니다.")
                apply_update()
                return  # 업데이트 후 프로그램 재시작
        
        # URL 열기
        for url in settings.get('urls', []):
            webbrowser.open(url)
        
        # 폴더 내 파일 처리
        folder_path = settings.get('folder', '')
        if folder_path:
            process_folder(folder_path)