"""Tab 1: Interaction & Conversations"""
import json
import logging
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QLineEdit, QPushButton, QListWidget, QSplitter,
                              QLabel, QComboBox, QFileDialog, QListWidgetItem,
                              QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation persistence"""
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path.home() / ".nova" / "conversations"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_conversation = None
    
    def create_conversation(self, title: str = None):
        """Create new conversation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = title or f"Conversation_{timestamp}"
        conv = {
            "id": timestamp,
            "title": title,
            "created": timestamp,
            "messages": [],
            "attachments": []
        }
        self.current_conversation = conv
        self.save_conversation(conv)
        return conv
    
    def save_conversation(self, conversation):
        """Save conversation to disk"""
        filepath = self.storage_path / f"{conversation['id']}.json"
        with open(filepath, 'w') as f:
            json.dump(conversation, f, indent=2)
    
    def load_conversation(self, conv_id: str):
        """Load conversation from disk"""
        filepath = self.storage_path / f"{conv_id}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                self.current_conversation = json.load(f)
                return self.current_conversation
        return None
    
    def list_conversations(self):
        """List all saved conversations"""
        conversations = []
        for filepath in sorted(self.storage_path.glob("*.json"), reverse=True):
            try:
                with open(filepath, 'r') as f:
                    conv = json.load(f)
                    conversations.append({
                        "id": conv["id"],
                        "title": conv["title"],
                        "created": conv["created"],
                        "message_count": len(conv["messages"])
                    })
            except Exception as e:
                logger.error(f"Failed to load conversation {filepath}: {e}")
        return conversations
    
    def delete_conversation(self, conv_id: str):
        """Delete conversation"""
        filepath = self.storage_path / f"{conv_id}.json"
        if filepath.exists():
            filepath.unlink()


class InteractionTab(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.conversation_manager = ConversationManager()
        self.current_attachments = []
        self._init_ui()
        self._load_conversations()
        self._create_new_conversation()
    
    def _init_ui(self):
        """Build the interaction interface"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # Left sidebar: Conversation list
        sidebar = self._create_sidebar()
        
        # Center: Chat interface
        chat_area = self._create_chat_area()
        
        # Right panel: Attachments/context
        attachments_panel = self._create_attachments_panel()
        
        # Add to splitter for resizing
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(chat_area)
        splitter.addWidget(attachments_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(splitter)
    
    def _create_sidebar(self):
        """Conversation history sidebar"""
        sidebar = QWidget()
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #181825;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        layout = QVBoxLayout(sidebar)
        
        # Title
        title = QLabel("💬 Conversations")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; background: transparent;")
        layout.addWidget(title)
        
        # New conversation button
        new_conv_btn = QPushButton("➕ New Chat")
        new_conv_btn.clicked.connect(self._create_new_conversation)
        new_conv_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
        """)
        layout.addWidget(new_conv_btn)
        
        # Conversation list
        self.conversation_list = QListWidget()
        self.conversation_list.itemClicked.connect(self._load_selected_conversation)
        self.conversation_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
            QListWidget::item:selected {
                background-color: #45475a;
                color: #89b4fa;
            }
        """)
        layout.addWidget(self.conversation_list)
        
        return sidebar
    
    def _create_chat_area(self):
        """Main chat interface"""
        chat_widget = QWidget()
        chat_widget.setStyleSheet("""
            QWidget {
                background-color: #181825;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(chat_widget)
        layout.setSpacing(12)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "🧠 Auto (Smart)",
            "⚡ Fast (SmolLM3)",
            "🔬 Deep (Llama)",
            "🔧 Legacy"
        ])
        mode_layout.addWidget(self.mode_selector)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Nova anything...")
        self.input_field.returnPressed.connect(self._submit_query)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #313244;
                border-radius: 8px;
                background-color: #1e1e2e;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #89b4fa;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._submit_query)
        self.send_button.setEnabled(False)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-weight: bold;
                min-width: 80px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #6c7086;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        return chat_widget
    
    def _create_attachments_panel(self):
        """Multimodal attachments panel"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #181825;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("📎 Attachments")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #f5c2e7; background: transparent;")
        layout.addWidget(title)
        
        # Upload button
        upload_btn = QPushButton("📤 Upload Files")
        upload_btn.clicked.connect(self._upload_files)
        layout.addWidget(upload_btn)
        
        # Drop zone
        self.drop_zone = QLabel("Drag & Drop\nFiles Here")
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setStyleSheet("""
            QLabel {
                background-color: #1e1e2e;
                border: 2px dashed #313244;
                border-radius: 8px;
                padding: 40px;
                color: #6c7086;
                font-size: 12pt;
            }
        """)
        self.drop_zone.setAcceptDrops(True)
        layout.addWidget(self.drop_zone)
        
        # Attachment list
        self.attachment_list = QListWidget()
        self.attachment_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.attachment_list)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self._clear_attachments)
        layout.addWidget(clear_btn)
        
        return panel
    
    def _load_conversations(self):
        """Load conversation list from disk"""
        self.conversation_list.clear()
        conversations = self.conversation_manager.list_conversations()
        for conv in conversations:
            item_text = f"{conv['title']}\n{conv['message_count']} messages"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, conv['id'])
            self.conversation_list.addItem(item)
    
    def _create_new_conversation(self):
        """Start new conversation"""
        conv = self.conversation_manager.create_conversation()
        self.chat_display.clear()
        self.current_attachments = []
        self.attachment_list.clear()
        self._load_conversations()
        self.chat_display.append('<span style="color: #89b4fa; font-weight: bold;">System:</span>')
        self.chat_display.append('<span style="color: #a6adc8;">New conversation started</span>\n')
    
    def _load_selected_conversation(self, item):
        """Load selected conversation"""
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        conv = self.conversation_manager.load_conversation(conv_id)
        if conv:
            self.chat_display.clear()
            for msg in conv['messages']:
                self._display_message(msg['role'], msg['content'], msg.get('color', '#ffffff'))
    
    def _submit_query(self):
        """Submit query to engine"""
        query = self.input_field.text().strip()
        if not query:
            return
        
        # Get mode
        mode_map = {
            "🧠 Auto (Smart)": "auto",
            "⚡ Fast (SmolLM3)": "fast",
            "🔬 Deep (Llama)": "deep",
            "🔧 Legacy": "legacy"
        }
        mode = mode_map[self.mode_selector.currentText()]
        
        # Display user message
        self._display_message("You", query, "#4a9eff")
        self.input_field.clear()
        self.send_button.setEnabled(False)
        
        # Save to conversation
        self._save_message("user", query)
        
        # Process query
        try:
            result = self.engine.process_query(query, mode)
            if "error" in result:
                self._display_message("Error", result["error"], "#ff4444")
            else:
                response = result.get("response", "")
                self._display_message("Nova", response, "#00ff88")
                self._save_message("assistant", response)
        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            self._display_message("Error", str(e), "#ff4444")
        
        self.send_button.setEnabled(True)
    
    def _display_message(self, sender: str, message: str, color: str):
        """Display message in chat"""
        self.chat_display.append(f'<span style="color: {color}; font-weight: bold;">{sender}:</span>')
        self.chat_display.append(f'<span style="color: #ffffff;">{message}</span>')
        self.chat_display.append("")
    
    def _save_message(self, role: str, content: str):
        """Save message to current conversation"""
        if self.conversation_manager.current_conversation:
            self.conversation_manager.current_conversation['messages'].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self.conversation_manager.save_conversation(
                self.conversation_manager.current_conversation
            )
    
    def _upload_files(self):
        """Upload files dialog"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*);;Images (*.png *.jpg *.jpeg);;Documents (*.pdf *.txt *.docx)"
        )
        if files:
            for filepath in files:
                self.current_attachments.append(filepath)
                self.attachment_list.addItem(Path(filepath).name)
    
    def _clear_attachments(self):
        """Clear all attachments"""
        self.current_attachments = []
        self.attachment_list.clear()
    
    def enable_interaction(self):
        """Enable input after models load"""
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
    
    def disable_interaction(self):
        """Disable input during loading"""
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
