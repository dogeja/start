import os
import json
import webbrowser
import shutil
from datetime import datetime, timedelta
import re
import requests
import sys
import subprocess
import winreg

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
        today = datetime.today()
        today_str = today.strftime('%Y%m%d')
        if date_str == today_str:
            return filename
        new_filename = filename[:match.start(1)] + today_str + filename[match.end(1):]
        return new_filename
    else:
        return filename

def check_for_updates(current_version):
    try:
        print(f"현재 버전: {current_version}")  # 로그 추가
        response = requests.get('https://api.github.com/repos/dogeja/start/releases/latest')
        print(f"API 응답 상태 코드: {response.status_code}")  # 로그 추가
        
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            print(f"최신 버전: {latest_version}")  # 로그 추가
            
            # 버전 비교를 위해 숫자로 변환
            current_nums = [int(x) for x in current_version.lstrip('v').split('.')]
            latest_nums = [int(x) for x in latest_version.split('.')]
            
            # 버전 비교
            is_update_needed = False
            for current, latest in zip(current_nums, latest_nums):
                if latest > current:
                    is_update_needed = True
                    break
                elif current > latest:
                    break
            
            print(f"업데이트 필요: {is_update_needed}")  # 로그 추가
            return is_update_needed, latest_version
        else:
            print("API 요청 실패")
            return False, None
    except Exception as e:
        print(f"업데이트 확인 중 오류 발생: {str(e)}")
        return False, None

def download_update(version):
    try:
        print(f"다운로드 시작: 버전 {version}")  # 로그 추가
        url = f'https://github.com/dogeja/start/releases/download/v{version}/환실련의아침.exe'
        print(f"다운로드 URL: {url}")  # 로그 추가
        
        response = requests.get(url, stream=True)
        print(f"다운로드 응답 상태 코드: {response.status_code}")  # 로그 추가
        
        if response.status_code == 200:
            current_exe = sys.executable
            temp_exe = current_exe + '.new'
            print(f"임시 파일 경로: {temp_exe}")  # 로그 추가
            
            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("다운로드 완료")  # 로그 추가
            return True
        else:
            print("다운로드 실패")
            return False
    except Exception as e:
        print(f"다운로드 중 오류 발생: {str(e)}")
        return False

def apply_update():
    try:
        current_exe = sys.executable
        temp_exe = current_exe + '.new'
        
        print(f"현재 실행 파일: {current_exe}")  # 로그 추가
        print(f"새 실행 파일: {temp_exe}")  # 로그 추가
        
        if not os.path.exists(temp_exe):
            print("업데이트 파일이 존재하지 않습니다.")
            return False

        # 업데이트 배치 파일 생성
        batch_file = 'update.bat'
        batch_content = f'''
@echo off
echo 업데이트를 시작합니다...
:loop
timeout /t 1 /nobreak > nul
tasklist | find /i "{os.path.basename(current_exe)}" > nul
if errorlevel 1 (
    echo 프로그램이 종료되었습니다. 업데이트를 진행합니다...
    move /y "{temp_exe}" "{current_exe}"
    if errorlevel 1 (
        echo 파일 이동 실패
        exit /b 1
    )
    start "" "{current_exe}"
    del "%~f0"
    exit
) else (
    echo 프로그램이 아직 실행 중입니다. 대기 중...
    goto loop
)
'''
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print("업데이트 배치 파일 생성 완료")  # 로그 추가
        subprocess.Popen(batch_file, shell=True)
        print("업데이트 프로세스 시작")  # 로그 추가
        sys.exit()
        
    except Exception as e:
        print(f"업데이트 적용 중 오류 발생: {str(e)}")
        return False

def process_folder(folder_path):
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
        os.startfile(folder_path)

def run_startup_tasks():
    settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        program_path = settings.get('program_path')
        if not program_path or not os.path.exists(program_path):
            print("프로그램 경로가 변경되었습니다. 자동 시작 설정을 다시 해주세요.")
            return

        urls = list(dict.fromkeys(settings.get('urls', [])))  # 중복 제거
        if urls:
            try:
                webbrowser.open(urls[0])  # 첫 번째 URL은 새 창에서 열기
                for url in urls[1:]:
                    webbrowser.open_new_tab(url)  # 나머지 URL은 새 탭에서 열기
            except Exception as e:
                print(f"URL을 여는 중 오류가 발생했습니다: {e}")
                    
        folder_path = settings.get('folder', '')
        if folder_path:
            process_folder(folder_path)
    else:
        print("설정 파일을 찾을 수 없습니다.")

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
        
def check_and_cleanup_autostart():
    try:
        # 레지스트리 확인
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
            try:
                winreg.DeleteValue(registry_key, "환실련의아침")
            except FileNotFoundError:
                pass

        # 시작 폴더 확인
        startup_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        bat_file = os.path.join(startup_folder, "run_url_folder_script.bat")
        if os.path.exists(bat_file):
            os.remove(bat_file)

        return True, "자동 시작 설정을 초기화했습니다."
    except Exception as e:
        return False, f"오류 발생: {str(e)}"
    
def update_autostart():
    try:
        current_exe = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        
        settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
        settings = {}
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        settings['program_path'] = current_exe
        with open(settings_file, 'w') as f:
            json.dump(settings, f)
        
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
            winreg.SetValueEx(registry_key, "환실련의아침", 0, winreg.REG_SZ, f'"{current_exe}" --startup')
        
        return True, "자동 시작 설정이 업데이트되었습니다."
    except Exception as e:
        return False, f"자동 시작 설정 중 오류 발생: {str(e)}"