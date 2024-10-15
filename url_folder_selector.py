import os
import sys
import json
import webbrowser
import shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import QTimer
from utils import update_date_in_filename, check_for_updates, download_update, apply_update, check_settings_compatibility
from version import __version__

class UrlFolderSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
        self.initUI()
        self.check_updates()
        
    def initUI(self):
        self.setWindowTitle(f'URL and Folder Selector v{__version__}')
        self.setGeometry(100, 100, 600, 400)
        self.layout = QVBoxLayout()
        autostart_btn = QPushButton('자동 시작 설정')
        autostart_btn.clicked.connect(self.setup_autostart)
        self.layout.addWidget(autostart_btn)        
        
        # URL 섹션
        url_label = QLabel('부팅 시 자동으로 열릴 주소:')
        self.layout.addWidget(url_label)
        
        self.url_list = QListWidget()
        self.layout.addWidget(self.url_list)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('여기에 주소 입력')
        self.layout.addWidget(self.url_input)
        
        url_buttons = QHBoxLayout()
        add_url_btn = QPushButton('주소 더하기')
        add_url_btn.clicked.connect(self.add_url)
        url_buttons.addWidget(add_url_btn)
        
        remove_url_btn = QPushButton('주소 지우기')
        remove_url_btn.clicked.connect(self.remove_url)
        url_buttons.addWidget(remove_url_btn)
        
        self.layout.addLayout(url_buttons)
        
        # 폴더 섹션
        folder_label = QLabel('일일업무보고 폴더 선택:')
        self.layout.addWidget(folder_label)
        
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        self.layout.addWidget(self.folder_path)
        
        select_folder_btn = QPushButton('폴더 선택')
        select_folder_btn.clicked.connect(self.select_folder)
        self.layout.addWidget(select_folder_btn)
        
        # 저장 버튼
        save_btn = QPushButton('설정 저장')
        save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(save_btn)
        QMessageBox.information(self, "안내", "설정이 적용되었습니다!")
        self.setLayout(self.layout)
        self.load_settings()

   
    def check_updates(self):
        update_available, latest_version = check_for_updates(__version__)
        if update_available:
            if download_update(latest_version):
                check_settings_compatibility(self.settings_file, latest_version)
                QMessageBox.information(self, '업데이트 준비 완료', '새 버전이 다운로드되었습니다. 프로그램을 재시작하여 업데이트를 적용합니다.')
                apply_update()
            else:
                QMessageBox.warning(self, '업데이트 실패', '업데이트 다운로드에 실패했습니다. 나중에 다시 시도합니다.')
        
        # 3일 후 다시 확인
        # QTimer.singleShot(3 * 24 * 60 * 60 * 1000, self.check_updates)
        QTimer.singleShot(30 * 1000, self.check_updates)

        
    def add_url(self):
        url = self.url_input.text()
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
        script_path = os.path.abspath(sys.argv[0])
        batch_content = f'@echo off\npythonw "{script_path}" --startup'
        startup_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        batch_file = os.path.join(startup_folder, "run_url_folder_tasks.bat")
        
        try:
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            QMessageBox.information(self, "성공", "이제 부팅 시 자동으로 실행됩니다!")
        except Exception as e:
            QMessageBox.warning(self, "에러", f"오류 발생!: {str(e)}")