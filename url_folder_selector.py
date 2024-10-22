import os
import sys
import json
import winreg
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit, QFileDialog, QLabel, QMessageBox, QStatusBar
from PyQt5.QtCore import QTimer
from utils import check_and_cleanup_autostart,check_for_updates, download_update, apply_update, cleanup_temp_files, update_autostart, run_startup_tasks, process_folder
from version import __version__

class UrlFolderSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.settings_file = os.path.join(os.path.expanduser("~"), "주소폴더세팅.json")
        cleanup_temp_files()
        self.initUI()
        self.check_updates()
        
    def initUI(self):
        self.setWindowTitle(f'🌍환실련의아침✨ v{__version__}')
        self.setGeometry(100, 100, 600, 400)
        
        # URL 섹션
        self.layout.addWidget(QLabel('부팅 시 자동으로 열릴 주소:'))
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
        self.layout.addWidget(QLabel('일일업무보고 폴더 선택:'))
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        self.layout.addWidget(self.folder_path)
        select_folder_btn = QPushButton('폴더 선택')
        select_folder_btn.clicked.connect(self.select_folder)
        self.layout.addWidget(select_folder_btn)
        
        # 설정 및 자동 시작 버튼
        save_btn = QPushButton('설정 저장')
        save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(save_btn)
        autostart_btn = QPushButton('자동 시작 설정')
        autostart_btn.clicked.connect(self.setup_autostart)
        self.layout.addWidget(autostart_btn)
        
        # 자동 시작 초기화..버튼
        cleanup_btn = QPushButton('자동 시작 초기화')
        cleanup_btn.clicked.connect(self.cleanup_autostart)
        self.layout.addWidget(cleanup_btn)

    
                
        # 테스트 실행 버튼
        test_run_btn = QPushButton('테스트 실행')
        test_run_btn.clicked.connect(self.test_run)
        self.layout.addWidget(test_run_btn)
        
        self.statusBar = self.statusBar()
        self.load_settings()
        
    def cleanup_autostart(self):
        success, message = check_and_cleanup_autostart()
        if success:
            QMessageBox.information(self, "성공", message)
        else:
            QMessageBox.warning(self, "오류", message)
            
    def check_updates(self):
        try:
            print("업데이트 확인 시작")  # 로그 추가
            update_available, latest_version = check_for_updates(__version__)

            if update_available and latest_version:
                print(f"새 버전 발견: {latest_version}")  # 로그 추가
                reply = QMessageBox.question(self, '업데이트 가능', 
                    f'새 버전 ({latest_version})이 있습니다. 지금 업데이트하시겠습니까?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    print("업데이트 시작")  # 로그 추가
                    self.statusBar.showMessage("업데이트 다운로드 중...")

                    if download_update(latest_version):
                        print("다운로드 성공")  # 로그 추가
                        QMessageBox.information(self, '업데이트 준비 완료', 
                            '새 버전이 다운로드되었습니다. 프로그램을 재시작하여 업데이트를 적용합니다!')
                        apply_update()
                    else:
                        print("다운로드 실패")  # 로그 추가
                        QMessageBox.warning(self, '업데이트 실패', 
                            '업데이트 다운로드에 실패했습니다. 나중에 다시 시도해주세요.')

        except Exception as e:
            print(f"업데이트 프로세스 중 오류 발생: {str(e)}")
            QMessageBox.warning(self, '업데이트 오류', 
                f'업데이트 중 오류가 발생했습니다: {str(e)}')

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
            'folder': self.folder_path.text(),
            'program_path': sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)
        self.statusBar.showMessage("설정이 적용되었습니다!", 3000)
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            self.url_list.clear()
            self.url_list.addItems(settings.get('urls', []))
            self.folder_path.setText(settings.get('folder', ''))
    
    def setup_autostart(self):
        success, message = update_autostart()
        if success:
            QMessageBox.information(self, "성공", "자동 시작 설정이 완료되었습니다!")
            self.statusBar.showMessage("이제 부팅 시 자동 실행됩니다!", 3000)
        else:
            QMessageBox.warning(self, "오류", f"자동 시작 설정 중 오류가 발생했습니다: {message}")
    
    def test_run(self):
        self.save_settings()
        run_startup_tasks()
        self.statusBar.showMessage("테스트 실행이 완료되었습니다.", 3000)