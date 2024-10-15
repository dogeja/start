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
        self.load_settings()
        self.check_updates()
        
    def initUI(self):
        # 기존 코드 유지
        ...

    # 기존 메서드들 유지
    ...
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
        QTimer.singleShot(3 * 24 * 60 * 60 * 1000, self.check_updates)

    def setup_autostart(self):
        script_path = os.path.abspath(sys.argv[0])
        batch_content = f'@echo off\npythonw "{script_path}" --startup'
        startup_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        batch_file = os.path.join(startup_folder, "run_url_folder_tasks.bat")
        
        try:
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            QMessageBox.information(self, "Success", "Startup tasks have been set up successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set up startup tasks: {str(e)}")