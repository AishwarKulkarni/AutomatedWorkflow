import sys
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from ui.ui import Notch

def main():
    load_dotenv()
    
    app = QApplication(sys.argv)
    notch = Notch()
    notch.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
