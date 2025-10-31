"""GUI for the academic scraper"""
import sys
import os
from typing import List, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QProgressBar, QLabel, QSpinBox,
    QTextEdit, QScrollArea, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.rag.runner import SEED_URLS, ScrapingRunner

class ScraperWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, config: Dict, subjects: List[str], max_pages: int):
        super().__init__()
        self.config = config
        self.subjects = subjects
        self.max_pages = max_pages
    
    def run(self):
        try:
            runner = ScrapingRunner(self.config)
            for subject in self.subjects:
                self.progress.emit(f"Processing {subject}...")
                # Convert to async
                import asyncio
                asyncio.run(runner.run([subject], self.max_pages))
            self.finished.emit(True)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(False)

class ScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academic RAG Scraper")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Subject selection
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Group checkboxes by category
        categories = {
            "AI & Computer Science": [
                "artificial_intelligence", "computer_science", "programming"
            ],
            "Engineering": [
                "software_engineering", "electrical_engineering",
                "mechanical_engineering", "civil_engineering"
            ],
            "Sciences": [
                "mathematics", "physics", "chemistry", "biology"
            ],
            "Data & Statistics": [
                "data_science", "statistics"
            ],
            "Professional": [
                "economics", "business_management", "law"
            ],
            "Healthcare": [
                "medicine_biomedical", "psychology"
            ],
            "Technology": [
                "web_development", "cloud_and_devops", "databases"
            ]
        }
        
        self.checkboxes = {}
        for category, subjects in categories.items():
            # Category label
            label = QLabel(f"<b>{category}</b>")
            scroll_layout.addWidget(label)
            
            # Subject checkboxes
            for subject in subjects:
                if subject in SEED_URLS:
                    cb = QCheckBox(subject.replace('_', ' ').title())
                    cb.setObjectName(subject)
                    self.checkboxes[subject] = cb
                    scroll_layout.addWidget(cb)
            
            # Add spacing between categories
            scroll_layout.addSpacing(10)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Options panel
        options_layout = QHBoxLayout()
        
        # Pages per subject
        pages_layout = QHBoxLayout()
        pages_label = QLabel("Max pages per subject:")
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 1000)
        self.pages_spin.setValue(100)
        pages_layout.addWidget(pages_label)
        pages_layout.addWidget(self.pages_spin)
        options_layout.addLayout(pages_layout)
        
        # Select/Deselect All
        select_all = QPushButton("Select All")
        select_all.clicked.connect(self.select_all)
        deselect_all = QPushButton("Deselect All")
        deselect_all.clicked.connect(self.deselect_all)
        options_layout.addWidget(select_all)
        options_layout.addWidget(deselect_all)
        
        layout.addLayout(options_layout)
        
        # Progress section
        progress_group = QFrame()
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        progress_layout.addWidget(self.status_text)
        
        layout.addWidget(progress_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Scraping")
        self.start_button.clicked.connect(self.start_scraping)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_scraping)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
    
    def select_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(True)
    
    def deselect_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(False)
    
    def start_scraping(self):
        selected_subjects = [
            name for name, cb in self.checkboxes.items() 
            if cb.isChecked()
        ]
        
        if not selected_subjects:
            QMessageBox.warning(
                self,
                "No Subjects Selected",
                "Please select at least one subject to scrape."
            )
            return
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setMaximum(0)  # Indeterminate mode
        
        config = {
            "chunk_size": 512,
            "chunk_overlap": 50,
            "delay": 2.0,
            "rag_config": {
                "embedding_model": "sentence-transformers/all-mpnet-base-v2",
                "collection_name": "academic_docs"
            },
            "rag_index_dir": os.path.expanduser("~/Nova/data/rag_index")
        }
        
        self.worker = ScraperWorker(
            config,
            selected_subjects,
            self.pages_spin.value()
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.scraping_finished)
        self.worker.start()
    
    def stop_scraping(self):
        if hasattr(self, 'worker'):
            self.worker.terminate()
            self.worker.wait()
            self.update_progress("Scraping stopped by user")
            self.scraping_finished(False)
    
    def update_progress(self, message: str):
        self.status_text.append(message)
    
    def scraping_finished(self, success: bool):
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100 if success else 0)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if success:
            QMessageBox.information(
                self,
                "Scraping Complete",
                "Academic content has been successfully scraped and indexed."
            )
        else:
            QMessageBox.warning(
                self,
                "Scraping Error",
                "There was an error during the scraping process. Check the status log for details."
            )

def main():
    app = QApplication(sys.argv)
    window = ScraperGUI()
    window.show()
    sys.exit(app.exec())