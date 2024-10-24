from typing import List
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QPushButton
from PyQt5.QtCore import Qt

class UpdateDialog(QDialog):
    def __init__(self, version: str, changes: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("업데이트 완료")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        
        # 버전 정보
        version_label = QLabel(f"버전 {version}(으)로 업데이트 되었습니다.")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # 구분선
        line = QLabel("─" * 50)
        line.setAlignment(Qt.AlignCenter)
        layout.addWidget(line)
        
        # 변경 사항 목록
        changes_browser = QTextBrowser()
        changes_text = "\n".join(f"• {change}" for change in changes)
        changes_browser.setText(changes_text)
        layout.addWidget(changes_browser)
        
        # 확인 버튼
        ok_button = QPushButton("확인")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)

class UpdateNotes:
    def __init__(self):
        self.notes_file = os.path.join(os.path.dirname(__file__), 'latest_update.txt')
        self.flag_file = os.path.join(os.path.expanduser("~"), ".update_shown")
    
    def get_latest_changes(self) -> List[str]:
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        return []
    
    def should_show_update(self, version: str) -> bool:
        if not os.path.exists(self.flag_file):
            return True
            
        with open(self.flag_file, 'r') as f:
            shown_version = f.read().strip()
            return shown_version != version
    
    def mark_update_shown(self, version: str):
        with open(self.flag_file, 'w') as f:
            f.write(version)