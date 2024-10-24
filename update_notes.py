from typing import List
import os

class UpdateNotes:
    def __init__(self):
        self.notes_file = os.path.join(os.path.dirname(__file__), 'latest_update.txt')
        self.flag_file = os.path.join(os.path.expanduser("~"), ".update_shown")  # 사용자 홈 디렉토리에 숨김 파일로 저장
    
    def get_latest_changes(self) -> List[str]:
        """최신 업데이트 내역을 가져옵니다."""
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        return []
    
    def should_show_update(self, version: str) -> bool:
        """업데이트 알림을 표시해야 하는지 확인합니다."""
        if not os.path.exists(self.flag_file):
            return True
            
        with open(self.flag_file, 'r') as f:
            shown_version = f.read().strip()
            return shown_version != version
    
    def mark_update_shown(self, version: str):
        """현재 버전의 업데이트 알림을 표시했다고 기록합니다."""
        with open(self.flag_file, 'w') as f:
            f.write(version)