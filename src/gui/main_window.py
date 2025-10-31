"""Nova AI - Three-Tab Unified Dashboard"""
import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QTabWidget, QPushButton, QStatusBar, QMessageBox,
                              QComboBox, QLabel)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QGuiApplication

from src.gui.tab1_interaction import InteractionTab
from src.gui.tab2_management import ManagementTab
from src.gui.tab3_metrics import MetricsTab
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
            self.progress.emit("Loading SmolLM3-3B (CPU)...")
            if not self.engine.load_model("smollm3"):
                self.finished.emit(False, "Failed to load SmolLM3")
                return
            self.progress.emit("Loading Llama-3.1-8B (GPU)...")
            if not self.engine.load_model("llama31"):
                logger.warning("Llama 3.1 failed, continuing with SmolLM3 only")
            self.progress.emit("Initializing RAG system...")
            self.engine.initialize_rag()
            self.finished.emit(True, "All systems ready")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

class NovaMainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.engine = NovaEngine(config)
        self.setWindowTitle("Nova AI - Unified Dashboard")
        screen = QGuiApplication.primaryScreen().geometry()
        window_width = int(screen.width() * 0.8)
        window_height = int(screen.height() * 0.8)
        x_pos = (screen.width() - window_width) // 2
        y_pos = (screen.height() - window_height) // 2
        self.setGeometry(x_pos, y_pos, window_width, window_height)
        self.setMinimumSize(1200, 700)
        self.setWindowFlags(Qt.WindowType.Window)
        self._setup_theme()
        self._init_ui()
        self._connect_signals()
        self._start_model_loading()

    def _setup_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            QTabWidget::pane { border: 2px solid #313244; border-radius: 8px; background-color: #181825; }
            QTabBar::tab { background-color: #313244; color: #cdd6f4; padding: 12px 24px; margin-right: 4px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 600; }
            QTabBar::tab:selected { background-color: #89b4fa; color: #1e1e2e; }
            QTabBar::tab:hover:!selected { background-color: #45475a; }
            QPushButton { background-color: #313244; color: #cdd6f4; border: 2px solid #45475a; border-radius: 8px; padding: 10px 20px; font-weight: 600; min-width: 100px; }
            QPushButton:hover { background-color: #45475a; border-color: #89b4fa; }
            QPushButton:pressed { background-color: #585b70; }
            QComboBox { background-color: #313244; color: #cdd6f4; border: 2px solid #45475a; border-radius: 8px; padding: 8px 12px; min-width: 200px; }
            QStatusBar { background-color: #181825; color: #a6adc8; border-top: 1px solid #313244; }
        """)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        header = self._create_header()
        main_layout.addWidget(header)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tab1 = InteractionTab(self.engine)
        self.tabs.addTab(self.tab1, "💬 Conversations")
        self.tab2 = ManagementTab(self.engine)
        self.tabs.addTab(self.tab2, "🔧 Management")
        self.tab3 = MetricsTab(self.engine)
        self.tabs.addTab(self.tab3, "📊 Metrics")
        main_layout.addWidget(self.tabs)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("⚡ Initializing Nova...")

    def _create_header(self):
        header = QWidget()
        header.setStyleSheet("QWidget { background-color: #181825; border-radius: 12px; padding: 8px; }")
        layout = QHBoxLayout(header)
        title = QLabel("🚀 NOVA AI")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; background: transparent;")
        layout.addWidget(title)
        layout.addStretch()
        model_label = QLabel("🤖 Model:")
        model_label.setStyleSheet("color: #89b4fa; font-weight: bold;")
        layout.addWidget(model_label)
        self.model_selector = QComboBox()
        self.model_selector.addItems(["SmolLM3-3B (CPU)", "Llama-3.1-8B (GPU)"])
        self.model_selector.currentIndexChanged.connect(self._switch_model)
        self.model_selector.setEnabled(False)
        layout.addWidget(self.model_selector)
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._refresh_models)
        layout.addWidget(self.refresh_btn)
        return header

    def _connect_signals(self):
        self.engine.tool_called.connect(self.tab2.update_tool_activity)
        self.engine.metrics_updated.connect(self.tab3.update_metrics)
        self.engine.heavy_thinking_started.connect(lambda: self.status_bar.showMessage("🧠 Deep thinking activated..."))
        self.engine.heavy_thinking_completed.connect(lambda: self.status_bar.showMessage("✅ Ready"))

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
            self.status_bar.showMessage(f"✅ {message}")
            self.tab1.enable_interaction()
        else:
            self.status_bar.showMessage(f"❌ {message}")
            QMessageBox.warning(self, "Error", message)

    def _switch_model(self, index):
        if index == 0:
            self.engine.switch_primary_model("smollm3")
            self.status_bar.showMessage("✅ Using SmolLM3-3B (CPU)")
        else:
            self.engine.switch_primary_model("llama31")
            self.status_bar.showMessage("✅ Using Llama-3.1-8B (GPU)")

    def _refresh_models(self):
        self.tab1.disable_interaction()
        self._start_model_loading()
