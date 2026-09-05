import os
import html
import keyboard
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextBrowser, QLabel, QFrame, QGraphicsDropShadowEffect,
    QPushButton,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt6.QtGui import QColor

from logic import ChatWorker, HotkeyThread, _steal_windows_focus

# ---- Look & feel -----------------------------------------------------------
BG = "#151517"
BORDER = "#2A2A2D"
TEXT = "#E0E0E0"
MUTED = "#7A7A7D"
ACCENT = "#00FF7F"
ERROR_COLOR = "#FF453A"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif"

COLLAPSED_IDLE_WIDTH = 200
COLLAPSED_ACTIVE_WIDTH = 220
COLLAPSED_HEIGHT = 60
EXPANDED_SIZE = (460, 520)


class Notch(QMainWindow):
    def __init__(self):
        super().__init__()
        self.expanded = False
        self.history = []
        self.worker = None
        self._build_ui()
        self._update_collapsed_state(animated=False)

        self.hotkeys = HotkeyThread()
        self.hotkeys.toggle.connect(self.toggle)
        self.hotkeys.start()

    # ---- UI ------------------------------------------------------------
    def _build_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(16, 12, 16, 16)
        self.setCentralWidget(outer)

        self.panel = QFrame()
        self.panel.setObjectName("MainPanel")
        self._update_panel_style(max(2, (COLLAPSED_HEIGHT - 28) // 2))

        shadow = QGraphicsDropShadowEffect(self.panel)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.panel.setGraphicsEffect(shadow)
        outer_layout.addWidget(self.panel)

        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(16, 3, 16, 3)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)
        self.dot = QLabel()
        self.dot.setFixedSize(10, 10)

        header.addWidget(self.dot)
        header.addStretch()

        self.title = QLabel("")
        self.title.setStyleSheet(f"QLabel {{ color: {MUTED}; font: 800 12px {FONT}; letter-spacing: 3px; background-color: transparent; border: none; outline: none; }}")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.hide()
        header.addWidget(self.title)

        header.addStretch()
        
        self.new_chat_btn = QPushButton("+")
        self.new_chat_btn.setFixedSize(20, 20)
        self.new_chat_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {MUTED}; border: none; font-size: 20px; font-weight: normal; margin-bottom: 2px; }} QPushButton:hover {{ color: {TEXT}; }}")
        self.new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_chat_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.new_chat_btn.clicked.connect(self.start_new_chat)
        self.new_chat_btn.hide()
        header.addWidget(self.new_chat_btn)
        
        header.addSpacing(4)

        layout.addLayout(header)
        self._set_active(False)

        self.chat = QTextBrowser()
        self.chat.setStyleSheet(f"""
            QTextBrowser {{ 
                background: transparent; 
                border: none; 
                font: 14px {FONT}; 
                color: {TEXT}; 
            }}
            QScrollBar:vertical {{ 
                width: 4px; 
                background: transparent; 
                border: none; 
            }}
            QScrollBar::handle:vertical {{ 
                background: rgba(255, 255, 255, 0.15); 
                border-radius: 2px; 
                min-height: 20px; 
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ 
                border: none; 
                background: none; 
                height: 0; 
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ 
                background: none; 
            }}
        """)
        self.chat.hide()
        layout.addWidget(self.chat)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask me anything…")
        self.input.setFixedHeight(44)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #1A1A1C;
                color: {TEXT};
                border-radius: 22px;
                padding: 0 20px;
                border: 1px solid {BORDER};
                font: 14px {FONT};
            }}
            QLineEdit:focus {{ 
                border: 1px solid #45454A; 
                background-color: #1E1E20; 
            }}
        """)
        self.input.returnPressed.connect(self.send)
        self.input.hide()
        layout.addWidget(self.input)

    def _set_active(self, active):
        color = ACCENT if active else MUTED
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 5px;")

    def _place(self, w, h):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry((screen.width() - w) // 2, 10, w, h)

    # ---- expand / collapse ----------------------------------------------
    def toggle(self):
        if not self.isVisible():
            self.show()
        self.expand() if not self.expanded else self.collapse()

    def expand(self):
        self.expanded = True
        self._update_panel_style(22)
        self.panel.layout().setContentsMargins(16, 12, 16, 16)
        self.chat.show()
        self.input.show()
        self.new_chat_btn.show()
        self._set_active(True)
        self._render()  # Ensure chat is rendered and scrolled correctly after showing
        self._animate(*EXPANDED_SIZE)
        self._grab_focus()

    def collapse(self):
        self.expanded = False
        self._update_panel_style(max(2, (COLLAPSED_HEIGHT - 28) // 2))
        self.panel.layout().setContentsMargins(16, 3, 16, 3)
        self.chat.hide()
        self.input.hide()
        self.new_chat_btn.hide()
        self._set_active(False)
        self._update_collapsed_state()

    def _update_collapsed_state(self, animated=True):
        if self.expanded:
            return

        if self.title.text():
            self.title.show()
            w = COLLAPSED_ACTIVE_WIDTH
        else:
            self.title.hide()
            w = COLLAPSED_IDLE_WIDTH

        # Prevent continuous animation if already at the target size
        current = self.geometry()
        if current.width() == w and current.height() == COLLAPSED_HEIGHT:
            return

        if animated:
            self._animate(w, COLLAPSED_HEIGHT)
        else:
            self._place(w, COLLAPSED_HEIGHT)

    def _animate(self, w, h):
        screen = QApplication.primaryScreen().geometry()
        target = QRect((screen.width() - w) // 2, 10, w, h)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(target)
        self.anim.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.anim.start()

    def _grab_focus(self):
        self.raise_()
        self.activateWindow()
        _steal_windows_focus(int(self.winId()))
        self.input.setFocus()
        QTimer.singleShot(50, self.input.setFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.expanded:
            self.close()
        else:
            super().keyPressEvent(event)

    # ---- chat -------------------------------------------------------------
    def start_new_chat(self):
        if self.worker is not None:
            self.worker.is_cancelled = True
            self.worker = None

        self.save_conversation()
        self.history.clear()
        self.chat.clear()
        self.title.setText("")
        self._update_collapsed_state()
        self.input.setDisabled(False)
        self.input.setPlaceholderText("Ask me anything…")

    def save_conversation(self):
        if not self.history:
            return
        os.makedirs("conversations", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join("conversations", f"chat_{timestamp}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            for msg in self.history:
                role = "YOU" if msg["role"] == "user" else "NOTCH"
                # Strip HTML tags out if there are any, though we store raw markdown basically.
                # The history has HTML from errors, but let's just write raw.
                f.write(f"### {role}\n{msg['content']}\n\n")

    def send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.input.setDisabled(True)
        self.input.setPlaceholderText("Thinking…")
        self.title.setText("Thinking…")
        self._update_collapsed_state()

        self.history.append({"role": "user", "content": text})
        self.history.append({"role": "assistant", "content": ""})
        self._render()

        if self.worker is not None:
            self.worker.is_cancelled = True

        self.worker = ChatWorker(self.history[:-1])
        self.worker.chunk.connect(self._on_chunk)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_error)
        self.worker.start()

    def _on_chunk(self, chunk):
        if not self.history:
            return
        self.title.setText("Typing…")
        self._update_collapsed_state()
        self.history[-1]["content"] += chunk
        self._render()

    def _on_done(self):
        self.input.setDisabled(False)
        self.input.setPlaceholderText("Ask me anything…")
        self.title.setText("")
        self._update_collapsed_state()
        self.input.setFocus()

    def _on_error(self, msg):
        if not self.history:
            return
        self.history[-1]["content"] = f"<span style='color:{ERROR_COLOR};'>{html.escape(msg)}</span>"
        self._render()
        self._on_done()

    def _render(self):
        blocks = []
        for msg in self.history:
            if msg["role"] not in ("user", "assistant"):
                continue

            is_user = msg["role"] == "user"
            body = msg["content"] if not is_user and "<span" in msg["content"] \
                else html.escape(msg["content"]).replace("\n", "<br>")

            if is_user:
                blocks.append(
                    f'<div style="margin-bottom: 12px; text-align: right;">'
                    f'<span style="color: {MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px;">YOU</span><br>'
                    f'<span style="color: #FFFFFF; font-size: 14px;">{body}</span>'
                    f'</div>'
                )
            else:
                blocks.append(
                    f'<div style="margin-bottom: 16px;">'
                    f'<span style="color: {ACCENT}; font-size: 10px; font-weight: 700; letter-spacing: 1px;">NOTCH</span><br>'
                    f'<span style="color: {TEXT}; font-size: 14px; line-height: 1.6;">{body}</span>'
                    f'</div>'
                )

        self.chat.setHtml("".join(blocks))
        sb = self.chat.verticalScrollBar()
        sb.setValue(sb.maximum())

    def closeEvent(self, event):
        self.save_conversation()
        keyboard.unhook_all()
        super().closeEvent(event)
        os._exit(0)

    def _update_panel_style(self, radius):
        self.panel.setStyleSheet(f"""
            QFrame#MainPanel {{
                background-color: {BG};
                border: 1px solid {BORDER};
                border-radius: {radius}px;
            }}
        """)
