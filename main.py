import sys
from PyQt5.QtWidgets import QApplication
from url_folder_selector import UrlFolderSelector
from utils import run_on_startup

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--startup':
        run_on_startup()
    else:
        app = QApplication(sys.argv)
        ex = UrlFolderSelector()
        ex.show()
        sys.exit(app.exec_())
        
# 빌드 순서
# 1. 소스코드 수정
# 2. version.py 파일 수정
# 3. git 커밋
# 4. git 태그 추가 (git tag v1.0.0)
# 5. git push origin v1.0.0
# 6. 깃허브 release 수정 