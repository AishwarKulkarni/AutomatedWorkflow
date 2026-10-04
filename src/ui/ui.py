import os
import html
import keyboard
import datetime
import json
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextBrowser, QLabel, QFrame, QGraphicsDropShadowEffect,
    QPushButton, QListWidget, QListWidgetItem, QMenu
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QRectF, QEasingCurve, QTimer, QEvent
from PyQt6.QtGui import QColor, QMouseEvent, QPainter, QAction
from agent.agent import AgentManager
from automation.action_controller import ActionController
from utils.utils import HotkeyThread, _steal_windows_focus
from voice.transcriber import VoiceTranscriber
from voice.synthesizer import VoiceSynthesizer
# ---- Look & feel -----------------------------------------------------------
BG = "#151517"
BORDER = "#2A2A2D"
TEXT = "#E0E0E0"
MUTED = "#7A7A7D"
ACCENT = "#00FF7F"
ERROR_COLOR = "#FF453A"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif"
COLLAPSED_IDLE_WIDTH = 180
COLLAPSED_ACTIVE_WIDTH = 195
COLLAPSED_HEIGHT = 60
EXPANDED_SIZE = (460, 520)


class WaveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 20)
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_wave)
        
    def start(self):
        self.phase = 0.0
        self.timer.start(16) # ~60 FPS for fluid Apple-like animation
        self.show()
        
    def stop(self):
        self.timer.stop()
        self.hide()
        
    def update_wave(self):
        self.phase += 0.08
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        num_bars = 5
        bar_width = 6.0
        spacing = 3.0
        total_width = num_bars * bar_width + (num_bars - 1) * spacing
        start_x = (self.width() - total_width) / 2.0
        
        accent = QColor(ACCENT)
        
        for i in range(num_bars):
            t = self.phase
            # Different phases and speeds for each bar for organic liquid motion
            p = i * 0.8
            
            v1 = math.sin(t * 1.5 + p)
            v2 = math.sin(t * 0.7 - p * 1.2)
            v3 = math.sin(t * 2.2 + p * 0.5)
            
            val = (v1 + v2 + v3) / 3.0 
            val = (val + 1.0) / 2.0 # Normalize to 0-1
            val = math.pow(val, 1.2) # Snappy ease
            
            # Envelope to ensure center bars are taller (Dynamic Island style)
            dist = abs(i - (num_bars - 1) / 2.0)
            max_h = 16.0 - (dist * 3.5)
            min_h = 4.0
            
            h = min_h + val * (max_h - min_h)
            y = (self.height() - h) / 2.0
            x = start_x + i * (bar_width + spacing)
            
            opacity = int(140 + (val * 115))
            
            # Subtle glow for premium feel
            glow = QColor(accent)
            glow.setAlpha(int(opacity * 0.3))
            painter.setBrush(glow)
            painter.drawRoundedRect(QRectF(x - 1, y - 1, bar_width + 2, h + 2), (bar_width + 2) / 2.0, (bar_width + 2) / 2.0)
            
            # Core bar
            core = QColor(accent)
            core.setAlpha(opacity)
            painter.setBrush(core)
            painter.drawRoundedRect(QRectF(x, y, bar_width, h), bar_width / 2.0, bar_width / 2.0)


class Notch(QMainWindow):
    def __init__(self):
        super().__init__()
        self.expanded = False
        
        os.makedirs("workflows", exist_ok=True)
        
        self.action_controller = ActionController()
        self.action_controller.start()
        
        self.agent = AgentManager(self.action_controller)
        self.agent.chunk.connect(self._on_chunk)
        self.agent.history_updated.connect(self._on_history_updated)
        self.agent.finished_ok.connect(self._on_done)
        self.agent.failed.connect(self._on_error)
        self.agent.status_update.connect(self._on_status_update)
        
        self.voice = VoiceTranscriber()
        self.voice.transcription_ready.connect(self._on_transcription_ready)
        self.voice.status_changed.connect(self._on_voice_status)
        
        self.synthesizer = VoiceSynthesizer(voice="en-GB-RyanNeural")
        
        self._build_ui()
        self._update_collapsed_state(animated=False)

        self.hotkeys = HotkeyThread()
        self.hotkeys.toggle.connect(self.toggle)
        self.hotkeys.toggle_recording.connect(self._toggle_recording)
        self.hotkeys.start()

        QApplication.instance().applicationStateChanged.connect(self._on_app_state_changed)

    def _on_app_state_changed(self, state):
        if state != Qt.ApplicationState.ApplicationActive:
            if self.expanded:
                self.collapse()

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
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.panel.setGraphicsEffect(shadow)
        outer_layout.addWidget(self.panel)

        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(16, 3, 16, 3)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)
        
        self.notch_label = QLabel("NotchAI")
        self.notch_label.setStyleSheet(f"QLabel {{ color: {TEXT}; font: 800 12px {FONT}; letter-spacing: 1px; background-color: transparent; border: none; outline: none; }}")
        self.notch_label.hide()
        header.addWidget(self.notch_label)
        
        header.addStretch()

        self.title = QLabel("")
        self.title.setStyleSheet(f"QLabel {{ color: {MUTED}; font: 800 12px {FONT}; letter-spacing: 3px; background-color: transparent; border: none; outline: none; }}")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.hide()
        header.addWidget(self.title)

        self.wave_widget = WaveWidget()
        self.wave_widget.hide()
        header.addWidget(self.wave_widget)

        header.addStretch()
        
        self.client_btn = QPushButton("OpenRouter")
        self.client_btn.setFixedHeight(20)
        self.client_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.client_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.client_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {MUTED};
                border: none;
                font: 600 11px {FONT};
                padding: 0 2px;
            }}
            QPushButton:hover {{ color: {TEXT}; }}
            QPushButton::menu-indicator {{ image: none; }}
        """)
        
        client_menu = QMenu(self)
        client_menu.setStyleSheet(f"""
            QMenu {{
                background-color: #1A1A1C;
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 4px 12px;
                border-radius: 4px;
                font: 600 11px {FONT};
            }}
            QMenu::item:selected {{
                background-color: #252528;
                color: {ACCENT};
            }}
        """)
        
        for client_name in ["OpenRouter", "Groq", "Gemini"]:
            action = QAction(client_name, self)
            action.triggered.connect(lambda checked, name=client_name: self._on_client_changed(name))
            client_menu.addAction(action)
            
        self.client_btn.setMenu(client_menu)
        self.client_btn.hide()
        header.addWidget(self.client_btn)
        
        header.addSpacing(1)
        
        self.new_chat_btn = QPushButton("+")
        self.new_chat_btn.setFixedSize(20, 20)
        self.new_chat_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {MUTED}; border: none; font-size: 20px; font-weight: normal; margin-bottom: 3px; }} QPushButton:hover {{ color: {TEXT}; }}")
        self.new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_chat_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.new_chat_btn.clicked.connect(self.start_new_chat)
        self.new_chat_btn.hide()
        header.addWidget(self.new_chat_btn)

        layout.addLayout(header)

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
        self.chat.setOpenLinks(False)
        self.chat.hide()
        layout.addWidget(self.chat)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask me anything...")
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
        self.input.textChanged.connect(self._on_input_text_changed)
        self.input.installEventFilter(self)
        
        self.ptt_btn = QPushButton("🎙")
        self.ptt_btn.setFixedSize(44, 44)
        self.ptt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ptt_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._update_ptt_btn_style(False)
        self.ptt_btn.clicked.connect(self._toggle_recording)
        
        self.input.hide()
        self.ptt_btn.hide()
        
        self.suggestion_list = QListWidget()
        self.suggestion_list.hide()
        self.suggestion_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #1A1A1C;
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 4px;
                font: 14px {FONT};
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 8px;
            }}
            QListWidget::item:hover, QListWidget::item:selected {{
                background-color: #252528;
                color: {ACCENT};
            }}
        """)
        self.suggestion_list.setFixedHeight(120)
        self.suggestion_list.itemClicked.connect(self._on_suggestion_clicked)
        self.suggestion_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        layout.addWidget(self.suggestion_list)
        
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.ptt_btn)
        
        layout.addLayout(input_layout)

    def _on_input_text_changed(self, text):
        if text.startswith("/"):
            query = text[1:].lower()
            workflows_dir = os.path.join(".agents", "context", "workflows")
            suggestions = []
            if os.path.exists(workflows_dir):
                for f in os.listdir(workflows_dir):
                    if f.endswith(".md"):
                        cmd = f[:-3]
                        if query in cmd.lower():
                            suggestions.append("/" + cmd)
            
            if suggestions:
                self.suggestion_list.clear()
                self.suggestion_list.addItems(suggestions)
                self.suggestion_list.setCurrentRow(0)
                self.suggestion_list.show()
            else:
                self.suggestion_list.hide()
        else:
            self.suggestion_list.hide()

    def _on_suggestion_clicked(self, item):
        self.input.setText(item.text() + " ")
        self.suggestion_list.hide()
        self.input.setFocus()

    def _on_client_changed(self, text):
        self.client_btn.setText(text)
        self.agent.client.set_client(text)

    def eventFilter(self, obj, event):
        if obj == self.input and event.type() == QEvent.Type.KeyPress:
            if self.suggestion_list.isVisible():
                if event.key() == Qt.Key.Key_Up:
                    row = self.suggestion_list.currentRow()
                    if row > 0:
                        self.suggestion_list.setCurrentRow(row - 1)
                    else:
                        self.suggestion_list.setCurrentRow(self.suggestion_list.count() - 1)
                    return True
                elif event.key() == Qt.Key.Key_Down:
                    row = self.suggestion_list.currentRow()
                    if row < self.suggestion_list.count() - 1:
                        self.suggestion_list.setCurrentRow(row + 1)
                    else:
                        self.suggestion_list.setCurrentRow(0)
                    return True
                elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
                    if self.suggestion_list.currentRow() >= 0:
                        self._on_suggestion_clicked(self.suggestion_list.currentItem())
                        return True
        return super().eventFilter(obj, event)

    def _place(self, w, h):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry((screen.width() - w) // 2, 4, w, h)

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
        self.ptt_btn.show()
        self.new_chat_btn.show()
        self.client_btn.show()
        self.notch_label.show()
        self._render()
        self._animate(*EXPANDED_SIZE)
        self._grab_focus()

    def collapse(self):
        self.expanded = False
        self._update_panel_style(max(2, (COLLAPSED_HEIGHT - 28) // 2))
        self.panel.layout().setContentsMargins(16, 3, 16, 3)
        self.chat.hide()
        self.input.hide()
        self.ptt_btn.hide()
        self.notch_label.hide()
        self.new_chat_btn.hide()
        self.client_btn.hide()
        self._update_collapsed_state()

    def _update_collapsed_state(self, animated=True):
        if self.expanded:
            return

        is_active = False
        if self.title.text():
            self.title.show()
            is_active = True
        else:
            self.title.hide()
            
        if hasattr(self, 'wave_widget') and self.wave_widget.isVisible():
            is_active = True
            
        w = COLLAPSED_ACTIVE_WIDTH if is_active else COLLAPSED_IDLE_WIDTH

        current = self.geometry()
        if current.width() == w and current.height() == COLLAPSED_HEIGHT:
            return

        if animated:
            self._animate(w, COLLAPSED_HEIGHT)
        else:
            self._place(w, COLLAPSED_HEIGHT)

    def _animate(self, w, h):
        screen = QApplication.primaryScreen().geometry()
        target = QRect((screen.width() - w) // 2, 4, w, h)
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

    def _toggle_recording(self):
        if self.voice.is_recording:
            self.voice.stop_recording()
            # Update button visual state if needed, though wave_widget already indicates recording
        else:
            self.synthesizer.stop()
            self.voice.start_recording()

    def _on_transcription_ready(self, text):
        self.input.setText(text)
        self.send()
        
    def _update_ptt_btn_style(self, is_recording):
        if is_recording:
            self.ptt_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ERROR_COLOR};
                    color: #FFFFFF;
                    border-radius: 22px;
                    border: 1px solid {ERROR_COLOR};
                    font-size: 18px;
                }}
                QPushButton:hover {{ background-color: #E63E34; }}
            """)
        else:
            self.ptt_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1A1A1C;
                    color: {TEXT};
                    border-radius: 22px;
                    border: 1px solid {BORDER};
                    font-size: 18px;
                }}
                QPushButton:hover {{ background-color: #252528; }}
                QPushButton:pressed {{ background-color: {ERROR_COLOR}; color: #FFFFFF; }}
            """)

    def _on_voice_status(self, status):
        if status == "Recording...":
            self.wave_widget.start()
            self._update_ptt_btn_style(True)
        else:
            self.wave_widget.stop()
            self._update_ptt_btn_style(False)
        self._update_collapsed_state()

    # ---- chat -------------------------------------------------------------
    def start_new_chat(self):
        self.agent.is_cancelled = True
        self.save_conversation()
        self.agent.clear_history()
        self.chat.clear()
        self.title.setText("")
        self._update_collapsed_state()
        self.input.setDisabled(False)
        self.input.setPlaceholderText("Ask me anything...")

    def save_conversation(self):
        if not self.agent.history:
            return
        os.makedirs("conversations", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join("conversations", f"chat_{timestamp}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            for msg in self.agent.history:
                role = "YOU" if msg["role"] == "user" else "NOTCH"
                f.write(f"### {role}\n")
                
                if msg.get("tool_calls"):
                    for tc in msg["tool_calls"]:
                        fn = tc.get("function", {})
                        f.write(f"**Tool Call:** {fn.get('name')}\n`json\n{fn.get('arguments')}\n`\n")
                
                if msg.get("content"):
                    f.write(f"{msg['content']}\n")
                f.write("\n")

    def send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.input.setDisabled(True)
        
        self.input.setPlaceholderText("Thinking")
        self.title.setText("Thinking")
        self._update_collapsed_state()

        self.agent.process_input(text)
        
        self.agent.is_cancelled = False
        self.agent.start()

    def _on_status_update(self, status: str):
        if status == "Workflow":
            self.input.setPlaceholderText("Running Workflow...")
            self.title.setText("Workflow")
        elif status == "":
            self.title.setText("")
        self._update_collapsed_state()

    def _on_chunk(self, chunk):
        self._render()

    def _on_history_updated(self, history):
        self._render()

    def _on_done(self):
        self.input.setDisabled(False)
        self.input.setPlaceholderText("Ask me anything..")
        self.title.setText("")
        self._update_collapsed_state()
        self.input.setFocus()
        
        if self.agent.history and self.agent.history[-1]["role"] == "assistant":
            content = self.agent.history[-1].get("content", "").strip()
            if content:
                self.synthesizer.speak(content)

    def _on_error(self, msg):
        print(f"AGENT ERROR: {msg}")
        self._on_done()

    def _render(self):
        blocks = []
        for msg in self.agent.history:
            if msg.get("hide_in_ui"):
                continue
            if msg["role"] not in ("user", "assistant"):
                continue
            is_user = msg["role"] == "user"
            content_str = msg.get("content") or ""
            body = (content_str if not is_user and "<span" in content_str
                    else html.escape(content_str).replace("\n", "<br>"))
            if msg.get("tool_calls"):
                html_lines = []
                if body:
                    html_lines.append(body)
                for c in msg.get("tool_calls", []):
                    fn_name = c.get("function", {}).get("name", "")
                    try:
                        args_str = c.get("function", {}).get("arguments", "{}")
                        c_args = json.loads(args_str)
                    except Exception:
                        c_args = {}

                    if fn_name == "execute_actions":
                        actions = c_args.get("actions", [])
                        for action in actions:
                            action_name = action.get("action_name", "?")
                            action_args = action.get("args", [])
                            target = action.get("target_app", "")
                            target_str = f" → <i>{html.escape(target)}</i>" if target else ""
                            args_display = html.escape(", ".join(str(a) for a in action_args)) if action_args else "<i>no args</i>"
                            html_lines.append(
                                f"<br><i>Executing:</i> <b>{html.escape(action_name)}</b>"
                                f"({args_display}){target_str}"
                            )
                    elif fn_name == "web_search":
                        query = c_args.get("query", "")
                        html_lines.append(
                            f'<br><span style="color: {MUTED}; font-size: 12px;">'
                            f'🔍 Searched: &ldquo;{html.escape(query)}&rdquo;</span>'
                        )
                    else:
                        html_lines.append(f"<br><i>Unknown tool:</i> <b>{html.escape(fn_name)}</b>")


                body = "<br>".join(html_lines)

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
        self.action_controller.stop()
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

