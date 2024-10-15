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