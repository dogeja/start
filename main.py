import sys
from PyQt5.QtWidgets import QApplication
from url_folder_selector import UrlFolderSelector
from utils import run_startup_tasks, UpdateDialog
from update_notes import UpdateNotes
from version import __version__

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--startup':
            run_startup_tasks()
        elif sys.argv[1] == '--updated':
            app = QApplication(sys.argv)
            notes = UpdateNotes()
            
            # 이 버전의 업데이트 알림을 아직 보지 않았다면 표시
            if notes.should_show_update(__version__):
                changes = notes.get_latest_changes()
                if changes:
                    dialog = UpdateDialog(__version__, changes)
                    dialog.exec_()
                    notes.mark_update_shown(__version__)  # 표시 완료 기록
            
            ex = UrlFolderSelector()
            ex.show()
            sys.exit(app.exec_())
    else:
        app = QApplication(sys.argv)
        ex = UrlFolderSelector()
        ex.show()
        sys.exit(app.exec_())