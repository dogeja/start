import webbrowser
import os
import shutil
import time
import re
from datetime import datetime, timedelta

# 열고자 하는 URL 목록
urls = [
    "https://www.ecolink.or.kr/",
    "https://happylog.naver.com/hlog/leekr021/home",
    "https://www.ecolink.or.kr/index.php?module=Logaccess&action=AdminLog&sMode=SELECT_FORM",
    "https://ecowater.or.kr/",
    "https://chatbot.kakao.com/",
    "https://webmail.ecolink.or.kr/user/mail/main.php",
    "https://www.notion.so/119c54153c60801eb820e2639bfe5362?v=119c54153c6081a5a939000ccdcbdcf4",
]

# 각 URL을 기본 웹 브라우저에서 엽니다
for url in urls:
    webbrowser.open(url)

# 폴더 경로를 열고 가장 최근 파일을 복제
folder_path = "C:\\Users\\disk6\\OneDrive\\바탕 화면\\일일업무보고"

# 폴더 내 파일 목록 가져오기
files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# 가장 최근에 수정된 파일 찾기
most_recent_file = max(files, key=os.path.getmtime)

# 가장 최근 파일을 새로운 이름으로 복제
# 파일 이름에서 괄호 뒤에 있는 날짜를 오늘 날짜로 갱신
def update_date_in_filename(filename):
    # 정규 표현식을 사용하여 괄호 안의 날짜를 찾습니다
    match = re.search(r'\((\d{8})\)', filename)
    if match:
        # 날짜 문자열을 datetime 객체로 변환
        date_str = match.group(1)
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        
        # 오늘 날짜를 가져옴
        today = datetime.today()
        today_str = today.strftime('%Y%m%d')
        
        # 날짜가 오늘 날짜와 동일하면 파일 이름 변경을 하지 않음
        if date_str == today_str:
            return filename
        
        # 날짜를 하루 증가
        new_date_obj = date_obj + timedelta(days=1)
        
        # 새로운 날짜 문자열 생성
        new_date_str = new_date_obj.strftime('%Y%m%d')
        
        # 파일 이름에서 날짜를 새로운 날짜로 대체
        new_filename = filename[:match.start(1)] + new_date_str + filename[match.end(1):]
        return new_filename
    else:
        # 날짜가 없는 경우 원래 파일 이름 반환
        return filename

# 새로운 파일 이름 생성
new_file_name = os.path.join(folder_path, update_date_in_filename(os.path.basename(most_recent_file)))
shutil.copy2(most_recent_file, new_file_name)
print(f"Duplicated file: {most_recent_file} to {new_file_name}")

# 생성된 파일 열기
os.startfile(new_file_name)

# 파일이 존재하는 폴더 열기
os.startfile(folder_path)