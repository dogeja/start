import os
import sys
import json
import webbrowser
import shutil
import winreg
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit, QFileDialog, QLabel, QMessageBox, QStatusBar
from PyQt5.QtCore import QTimer
from utils import update_date_in_filename, check_for_updates, download_update, apply_update, check_settings_compatibility, cleanup_temp_files
from version import __version__

class UrlFolderSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
        cleanup_temp_files()  # 임시 파일 정리
        self.initUI()
        self.check_updates()
        
    def initUI(self):
        self.setWindowTitle(f'🌍환실련의아침✨ v{__version__}')
        self.setGeometry(100, 100, 600, 400)
        

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
        
        autostart_btn = QPushButton('자동 시작 설정')
        autostart_btn.clicked.connect(self.setup_autostart)
        self.layout.addWidget(autostart_btn) 
                
        # 상태 바 추가
        self.statusBar = self.statusBar()
        
        self.load_settings()
        self.statusBar.showMessage("설정이 적용되었습니다!", 3000)  # 3초 동안 표시

    def check_updates(self):
        update_available, latest_version = check_for_updates(__version__)
        if update_available:
            reply = QMessageBox.question(self, '업데이트 가능', 
                f'새 버전 ({latest_version})이 있습니다. 지금 업데이트하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                if download_update(latest_version):
                    QMessageBox.information(self, '업데이트 준비 완료', '새 버전이 다운로드되었습니다. 프로그램을 재시작하여 업데이트를 적용합니다.')
                    apply_update()
                else:
                    QMessageBox.warning(self, '업데이트 실패', '업데이트 다운로드에 실패했습니다. 나중에 다시 시도해주세요.')
        
        # 3일 후 다시 확인
        QTimer.singleShot(3 * 24 * 60 * 60 * 1000, self.check_updates)
        
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
        try:
            # 현재 실행 파일의 경로를 가져옵니다.
            if getattr(sys, 'frozen', False):
                # PyInstaller로 만든 실행 파일의 경우
                current_exe = sys.executable
            else:
                # 일반 Python 스크립트의 경우
                current_exe = sys.argv[0]
            
            # .bat 파일 내용 생성
            batch_content = f'@echo off\nstart "" "{current_exe}" --startup'
            
            # 시작 프로그램 폴더 경로
            startup_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            
            # .bat 파일 경로
            bat_file_path = os.path.join(startup_folder, "run_url_folder_script.bat")
            
            # .bat 파일 생성
            with open(bat_file_path, 'w') as f:
                f.write(batch_content)
            
            # Windows 레지스트리에 등록 (추가적인 보장을 위해)
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
                winreg.SetValueEx(registry_key, "URLFolderSelector", 0, winreg.REG_SZ, bat_file_path)
            
            QMessageBox.information(self, "성공", "자동 시작 설정이 완료되었습니다!")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"자동 시작 설정 중 오류가 발생했습니다: {str(e)}")