"""Main window - With Two-Tier Heavy Thinking System"""
import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QStatusBar, QMessageBox, QComboBox, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from .chat_panel import ChatPanel
from .tool_panel import ToolPanel
from .media_panel import MediaPanel
from .metrics_panel import MetricsPanel
from src.core.engine import NovaEngine

logger = logging.getLogger(__name__)

class ModelLoadThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def run(self):
        try:
            self.progress.emit("Loading SmolLM3-3B (CPU, 8-bit)...")
            if not self.engine.load_model("smollm3"):
                self.finished.emit(False, "Failed to load SmolLM3")
                return

            self.progress.emit("Loading Llama-3.1-8B (GPU, 8-bit)...")
            if not self.engine.load_model("llama31"):
                logger.warning("Llama 3.1 failed, continuing with SmolLM3 only")

            self.progress.emit("Initializing RAG system...")
            self.engine.initialize_rag()

            self.finished.emit(True, "All models loaded successfully")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

class NovaMainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.engine = NovaEngine(config)
        self.setWindowTitle("Nova AI Dashboard")
        self.setGeometry(100, 100, 1600, 950)
        self._setup_theme()
        self._init_ui()
        self._start_model_loading()

    def _setup_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            QPushButton { background-color: #313244; color: #cdd6f4; border: 2px solid #45475a; border-radius: 8px; padding: 10px 20px; font-weight: 600; min-width: 100px; }
            QPushButton:hover { background-color: #45475a; border-color: #89b4fa; }
            QPushButton:pressed { background-color: #585b70; }
            QPushButton:disabled { background-color: #181825; color: #6c7086; border-color: #313244; }
            QComboBox { background-color: #313244; color: #cdd6f4; border: 2px solid #45475a; border-radius: 8px; padding: 8px 12px; font-weight: 600; min-width: 200px; }
            QComboBox:hover { border-color: #89b4fa; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { image: none; border: none; }
            QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #45475a; border: 2px solid #45475a; }
            QStatusBar { background-color: #181825; color: #a6adc8; border-top: 1px solid #313244; }
            QLabel { background: transparent; }
        """)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        header = QWidget()
        header.setStyleSheet("background-color: #181825; border-radius: 12px; padding: 8px;")
        button_layout = QHBoxLayout(header)

        model_label = QLabel("🤖 Active Model:")
        model_label.setStyleSheet("color: #89b4fa; font-weight: bold; padding-right: 8px;")

        self.model_selector = QComboBox()
        self.model_selector.addItems(["SmolLM3-3B (CPU)", "Llama-3.1-8B (GPU)"])
        self.model_selector.currentIndexChanged.connect(self._switch_model)
        self.model_selector.setEnabled(False)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.clear_btn = QPushButton("🗑 Clear")

        self.refresh_btn.clicked.connect(self._refresh_models)
        self.clear_btn.clicked.connect(self._clear_chat)

        button_layout.addWidget(model_label)
        button_layout.addWidget(self.model_selector)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        main_layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #313244; }")

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(12)
        
        # CHANGED: ChatPanel no longer takes engine parameter
        self.chat_panel = ChatPanel()
        self.media_panel = MediaPanel(self.config, self.engine)
        left_layout.addWidget(self.chat_panel, stretch=7)
        left_layout.addWidget(self.media_panel, stretch=3)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        self.tool_panel = ToolPanel()
        self.metrics_panel = MetricsPanel()
        right_layout.addWidget(self.tool_panel, stretch=5)
        right_layout.addWidget(self.metrics_panel, stretch=5)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)

        main_layout.addWidget(splitter)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("⚡ Initializing Nova...")

        # CHANGED: Connect new signals for heavy thinking
        self.engine.tool_called.connect(self.tool_panel.add_tool_call)
        self.engine.metrics_updated.connect(self.metrics_panel.update_metrics)
        self.engine.heavy_thinking_started.connect(self.chat_panel.show_heavy_thinking)
        self.engine.heavy_thinking_completed.connect(self.chat_panel.hide_heavy_thinking)
        
        # CHANGED: Connect chat panel query signal to new handler
        self.chat_panel.query_submitted.connect(self._handle_query)

    def _start_model_loading(self):
        self.load_thread = ModelLoadThread(self.engine)
        self.load_thread.progress.connect(self._update_loading_status)
        self.load_thread.finished.connect(self._loading_finished)
        self.load_thread.start()
        self.refresh_btn.setEnabled(False)

    def _update_loading_status(self, message: str):
        self.status_bar.showMessage(f"⏳ {message}")

    def _loading_finished(self, success: bool, message: str):
        self.refresh_btn.setEnabled(True)
        self.model_selector.setEnabled(True)
        if success:
            self.status_bar.showMessage(f"✓ {message}")
            # CHANGED: New method name
            self.chat_panel.send_button.setEnabled(True)
        else:
            self.status_bar.showMessage(f"✗ {message}")
            QMessageBox.warning(self, "Error", message)

    # NEW METHOD: Handle queries with mode selection
    def _handle_query(self, query: str, mode: str):
        """Handle query with specified mode"""
        try:
            result = self.engine.process_query(query, mode)
            
            if "error" in result:
                self.chat_panel.display_error(result["error"])
            else:
                self.chat_panel.display_response(result)
                
        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            self.chat_panel.display_error(str(e))

    def _switch_model(self, index):
        if index == 0:
            self.engine.switch_primary_model("smollm3")
            self.status_bar.showMessage("✓ Using SmolLM3-3B (CPU)")
        else:
            self.engine.switch_primary_model("llama31")
            self.status_bar.showMessage("✓ Using Llama-3.1-8B (GPU)")

    def _refresh_models(self):
        self.chat_panel.send_button.setEnabled(False)
        self._start_model_loading()

    def _clear_chat(self):
        self.chat_panel.chat_display.clear()
