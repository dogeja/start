import sys
import os
import webbrowser
import shutil
from datetime import datetime, timedelta
import re
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import QTimer

class UrlFolderSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
        self.initUI()
        self.load_settings()
        
    def initUI(self):
        self.setWindowTitle('URL and Folder Selector')
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # URL 섹션
        url_label = QLabel('부팅 시 자동으로 열릴 주소:')
        layout.addWidget(url_label)
        
        self.url_list = QListWidget()
        layout.addWidget(self.url_list)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('여기에 주소 입력')
        layout.addWidget(self.url_input)
        
        url_buttons = QHBoxLayout()
        add_url_btn = QPushButton('주소 더하기')
        add_url_btn.clicked.connect(self.add_url)
        url_buttons.addWidget(add_url_btn)
        
        remove_url_btn = QPushButton('주소 지우기')
        remove_url_btn.clicked.connect(self.remove_url)
        url_buttons.addWidget(remove_url_btn)
        
        layout.addLayout(url_buttons)
        
        # 폴더 섹션
        folder_label = QLabel('일일업무보고 폴더 선택:')
        layout.addWidget(folder_label)
        
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        layout.addWidget(self.folder_path)
        
        select_folder_btn = QPushButton('폴더 선택')
        select_folder_btn.clicked.connect(self.select_folder)
        layout.addWidget(select_folder_btn)
        
        # # 실행 버튼
        # run_btn = QPushButton('실행')
        # run_btn.clicked.connect(self.run_script)
        # layout.addWidget(run_btn)
        
        # 저장 버튼
        save_btn = QPushButton('설정 저장')
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)
        
    def add_url(self, url):
        url=self.url_input.text()
        if url:
            self.url_list.addItem(url)
            self.url_input.clear()
            self.save_settings()
    
    def remove_url(self):
        current_item = self.url_list.currentItem()
        if current_item:
            self.url_list.takeItem(self.url_list.row(current_item))
            self.save_settings()
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path.setText(folder)
            self.save_settings()
    
    def run_script(self):
        urls = [self.url_list.item(i).text() for i in range(self.url_list.count())]
        folder_path = self.folder_path.text()
        
        # URL 열기
        for url in urls:
            webbrowser.open(url)
        
        # 폴더 내 파일 처리
        if folder_path:
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if files:
                most_recent_file = max(files, key=os.path.getmtime)
                new_file_name = os.path.join(folder_path, self.update_date_in_filename(os.path.basename(most_recent_file)))
                shutil.copy2(most_recent_file, new_file_name)
                print(f"Duplicated file: {most_recent_file} to {new_file_name}")
                os.startfile(new_file_name)
                os.startfile(folder_path)
    
    def update_date_in_filename(self, filename):
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
    
    def save_settings(self):
        settings = {
            'urls': [self.url_list.item(i).text() for i in range(self.url_list.count())],
            'folder': self.folder_path.text()
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            self.url_list.clear()
            self.url_list.addItems(settings.get('urls', []))
            self.folder_path.setText(settings.get('folder', ''))
    
    def setup_autostart(self):
        # 현재 스크립트의 경로를 얻습니다
        script_path = os.path.abspath(sys.argv[0])
        
        # 배치 파일 내용 생성
        batch_content = f'@echo off\npythonw "{script_path}" --startup'
        
        # 시작 폴더 경로
        startup_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        
        # 배치 파일 경로
        batch_file = os.path.join(startup_folder, "run_url_folder_script.bat")
        
        try:
            # 배치 파일 생성
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            QMessageBox.information(self, "Success", "Auto-start has been set up successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set up auto-start: {str(e)}")

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

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--startup':
        run_on_startup()
    else:
        app = QApplication(sys.argv)
        ex = UrlFolderSelector()
        ex.show()
        sys.exit(app.exec_())