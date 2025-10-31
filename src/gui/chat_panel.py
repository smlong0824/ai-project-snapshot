"""Chat Panel - Updated with Heavy Thinking Indicator"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QLabel,
                             QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ChatPanel(QWidget):
    query_submitted = pyqtSignal(str, str)  # query, mode
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("💬 Nova Chat")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Status indicator for heavy thinking
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4a9eff;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Auto (Smart)",
            "Fast (SmolLM3)",
            "Deep (Llama)",
            "Legacy"
        ])
        self.mode_selector.setToolTip(
            "Auto: Uses SmolLM3, calls Llama for complex queries\n"
            "Fast: SmolLM3 only (quick responses)\n"
            "Deep: Llama only (detailed analysis)\n"
            "Legacy: Uses primary model setting"
        )
        mode_layout.addWidget(self.mode_selector)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Nova anything...")
        self.input_field.returnPressed.connect(self.submit_query)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #333;
                border-radius: 5px;
                background-color: #2a2a2a;
                color: white;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.submit_query)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
    def submit_query(self):
        query = self.input_field.text().strip()
        if query:
            # Get selected mode
            mode_text = self.mode_selector.currentText()
            mode_map = {
                "Auto (Smart)": "auto",
                "Fast (SmolLM3)": "fast",
                "Deep (Llama)": "deep",
                "Legacy": "legacy"
            }
            mode = mode_map[mode_text]
            
            self.append_message("You", query, "#4a9eff")
            self.input_field.clear()
            self.send_button.setEnabled(False)
            self.query_submitted.emit(query, mode)
    
    def append_message(self, sender: str, message: str, color: str = "#ffffff"):
        """Add a message to the chat display"""
        self.chat_display.append(f'<span style="color: {color}; font-weight: bold;">{sender}:</span>')
        self.chat_display.append(f'<span style="color: #ffffff;">{message}</span>')
        self.chat_display.append("")  # Blank line
        
    def append_system_message(self, message: str):
        """Add a system message (like heavy thinking indicator)"""
        self.chat_display.append(f'<span style="color: #888; font-style: italic;">{message}</span>')
        self.chat_display.append("")
    
    def show_heavy_thinking(self):
        """Show that heavy thinking has started"""
        self.status_label.setText("🧠 Heavy thinking in progress...")
        self.append_system_message("🧠 Activating deep analysis with Llama 3.1...")
        
    def hide_heavy_thinking(self):
        """Hide heavy thinking indicator"""
        self.status_label.setText("")
        
    def display_response(self, result: dict):
        """Display the AI response with metadata"""
        response = result.get("response", "")
        model_used = result.get("model_used", "Unknown")
        inference_time = result.get("inference_time", 0)
        used_heavy_thinking = result.get("used_heavy_thinking", False)
        
        # Show model and timing info
        meta_info = f"[{model_used} • {inference_time:.2f}s"
        if used_heavy_thinking:
            meta_info += " • Used heavy thinking"
        meta_info += "]"
        
        self.append_system_message(meta_info)
        self.append_message("Nova", response, "#00ff88")
        
        self.send_button.setEnabled(True)
        self.hide_heavy_thinking()
        
    def display_error(self, error: str):
        """Display an error message"""
        self.append_message("Error", error, "#ff4444")
        self.send_button.setEnabled(True)
        self.hide_heavy_thinking()
    
    def enable_input(self):
        """Enable input field and send button"""
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
    
    def disable_input(self):
        """Disable input field and send button"""
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.clear()
