"""Media panel - Production UI"""
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget, 
                              QLabel, QFileDialog, QProgressBar, QHBoxLayout, QListWidgetItem)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon

logger = logging.getLogger(__name__)

class IngestionThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, engine, file_paths):
        super().__init__()
        self.engine = engine
        self.file_paths = file_paths
    
    def run(self):
        try:
            for fp in self.file_paths:
                self.progress.emit(f"Processing {Path(fp).name}...")
                self.engine.ingest_document(fp)
            self.finished.emit(True, f"✓ Ingested {len(self.file_paths)} files")
        except Exception as e:
            self.finished.emit(False, f"✗ Error: {str(e)}")

class MediaPanel(QWidget):
    def __init__(self, config, engine):
        super().__init__()
        self.config = config
        self.engine = engine
        self._init_ui()
    
    def _init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #181825;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("📁 Knowledge Base")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #f5c2e7; background: transparent;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Upload documents for RAG-enhanced responses")
        subtitle.setStyleSheet("color: #a6adc8; font-size: 12px; background: transparent;")
        layout.addWidget(subtitle)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.upload_btn = QPushButton("📤 Upload Files")
        self.upload_btn.clicked.connect(self._upload_files)
        self.upload_btn.setStyleSheet("""
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
        
        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.clicked.connect(self._clear_index)
        self.clear_btn.setMinimumHeight(40)
        
        btn_layout.addWidget(self.upload_btn, stretch=3)
        btn_layout.addWidget(self.clear_btn, stretch=1)
        layout.addLayout(btn_layout)
        
        # File list with custom styling
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
                margin: 2px 0;
                color: #cdd6f4;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
            QListWidget::item:selected {
                background-color: #45475a;
                color: #89b4fa;
            }
        """)
        layout.addWidget(self.file_list)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(8)
        self.progress_bar.setMaximumHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #313244;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #a6e3a1;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to upload documents")
        self.status_label.setStyleSheet("""
            color: #a6adc8; 
            font-size: 12px; 
            background: transparent;
            padding: 4px;
        """)
        layout.addWidget(self.status_label)
        
        # Stats
        self.stats_label = QLabel("📊 0 documents indexed")
        self.stats_label.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent;")
        layout.addWidget(self.stats_label)
    
    def _upload_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "Supported Files (*.txt *.pdf *.docx *.png *.jpg *.jpeg);;All Files (*.*)"
        )
        
        if not file_paths:
            return
        
        # Add to list with file type icons
        for path in file_paths:
            file_path = Path(path)
            suffix = file_path.suffix.lower()
            
            # Icon based on file type
            if suffix in ['.txt', '.md']:
                icon = '📄'
            elif suffix == '.pdf':
                icon = '📕'
            elif suffix in ['.docx', '.doc']:
                icon = '📘'
            elif suffix in ['.png', '.jpg', '.jpeg']:
                icon = '🖼'
            else:
                icon = '📎'
            
            item = QListWidgetItem(f"{icon} {file_path.name}")
            self.file_list.addItem(item)
        
        # Start ingestion
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.upload_btn.setEnabled(False)
        self.status_label.setText("⏳ Processing documents...")
        
        self.ingest_thread = IngestionThread(self.engine, file_paths)
        self.ingest_thread.progress.connect(self._update_progress)
        self.ingest_thread.finished.connect(self._ingestion_finished)
        self.ingest_thread.start()
    
    def _update_progress(self, message: str):
        self.status_label.setText(f"⏳ {message}")
    
    def _ingestion_finished(self, success: bool, message: str):
        self.progress_bar.setVisible(False)
        self.upload_btn.setEnabled(True)
        self.status_label.setText(message)
        
        # Update stats
        count = self.file_list.count()
        self.stats_label.setText(f"📊 {count} document{'s' if count != 1 else ''} indexed")
    
    def _clear_index(self):
        self.file_list.clear()
        self.status_label.setText("✓ Index cleared")
        self.stats_label.setText("📊 0 documents indexed")
