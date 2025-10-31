"""Tab 2: Node/Agent/Tool Management"""
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                              QPushButton, QLabel, QTextEdit, QSplitter,
                              QTreeWidget, QTreeWidgetItem, QComboBox,
                              QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

logger = logging.getLogger(__name__)

class ManagementTab(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.active_nodes = {}
        self.tool_calls_history = []
        self._init_ui()
        self._start_monitoring()
    
    def _init_ui(self):
        """Build management interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # Header
        header = QLabel("🔧 Node & Agent Management")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #f9e2af; background: transparent;")
        main_layout.addWidget(header)
        
        # Splitter for main areas
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Node tree view
        node_panel = self._create_node_panel()
        splitter.addWidget(node_panel)
        
        # Center: Tool activity
        tool_panel = self._create_tool_panel()
        splitter.addWidget(tool_panel)
        
        # Right: Control panel
        control_panel = self._create_control_panel()
        splitter.addWidget(control_panel)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 2)
        
        main_layout.addWidget(splitter)
    
    def _create_node_panel(self):
        """Node/Agent tree visualization"""
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
        title = QLabel("📊 System Nodes")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; background: transparent;")
        layout.addWidget(title)
        
        # Node tree
        self.node_tree = QTreeWidget()
        self.node_tree.setHeaderLabels(["Component", "Status", "Type"])
        self.node_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                color: #cdd6f4;
            }
            QTreeWidget::item {
                padding: 8px;
            }
            QTreeWidget::item:selected {
                background-color: #45475a;
            }
        """)
        layout.addWidget(self.node_tree)
        
        # Populate initial nodes
        self._populate_node_tree()
        
        return panel
    
    def _create_tool_panel(self):
        """Tool call activity monitor"""
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
        title = QLabel("⚡ Tool Activity")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #f9e2af; background: transparent;")
        layout.addWidget(title)
        
        # Tool display
        self.tool_display = QTextEdit()
        self.tool_display.setReadOnly(True)
        self.tool_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.tool_display)
        
        # Initial message
        self.tool_display.setHtml("""
            <div style='text-align: center; padding: 40px; color: #6c7086;'>
                <p style='font-size: 48px; margin: 0;'>⚡</p>
                <p style='margin: 10px 0 0 0;'>Tool calls will appear here</p>
                <p style='font-size: 11px; margin: 5px 0 0 0;'>Monitoring active</p>
            </div>
        """)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(self._clear_tool_history)
        layout.addWidget(clear_btn)
        
        return panel
    
    def _create_control_panel(self):
        """Node control and configuration"""
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
        title = QLabel("🎛️ Controls")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #a6e3a1; background: transparent;")
        layout.addWidget(title)
        
        # Heavy thinking toggle
        heavy_thinking_group = QGroupBox("Heavy Thinking")
        heavy_thinking_group.setStyleSheet("""
            QGroupBox {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 12px;
                margin-top: 12px;
                color: #cdd6f4;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        ht_layout = QVBoxLayout(heavy_thinking_group)
        
        self.enable_heavy_thinking = QCheckBox("Enable Heavy Thinking")
        self.enable_heavy_thinking.setChecked(True)
        self.enable_heavy_thinking.stateChanged.connect(self._toggle_heavy_thinking)
        ht_layout.addWidget(self.enable_heavy_thinking)
        
        ht_layout.addWidget(QLabel("Word count threshold:"))
        self.threshold_selector = QComboBox()
        self.threshold_selector.addItems(["30", "50", "100", "150"])
        self.threshold_selector.setCurrentText("50")
        self.threshold_selector.currentTextChanged.connect(self._update_threshold)
        ht_layout.addWidget(self.threshold_selector)
        
        layout.addWidget(heavy_thinking_group)
        
        # Model controls
        model_group = QGroupBox("Model Controls")
        model_group.setStyleSheet(heavy_thinking_group.styleSheet())
        model_layout = QVBoxLayout(model_group)
        
        reload_smollm_btn = QPushButton("🔄 Reload SmolLM3")
        reload_smollm_btn.clicked.connect(lambda: self._reload_model("smollm3"))
        model_layout.addWidget(reload_smollm_btn)
        
        reload_llama_btn = QPushButton("🔄 Reload Llama 3.1")
        reload_llama_btn.clicked.connect(lambda: self._reload_model("llama31"))
        model_layout.addWidget(reload_llama_btn)
        
        layout.addWidget(model_group)
        
        # RAG controls
        rag_group = QGroupBox("RAG System")
        rag_group.setStyleSheet(heavy_thinking_group.styleSheet())
        rag_layout = QVBoxLayout(rag_group)
        
        reinit_rag_btn = QPushButton("🔄 Reinitialize RAG")
        reinit_rag_btn.clicked.connect(self._reinit_rag)
        rag_layout.addWidget(reinit_rag_btn)
        
        clear_index_btn = QPushButton("🗑️ Clear Index")
        clear_index_btn.clicked.connect(self._clear_rag_index)
        rag_layout.addWidget(clear_index_btn)
        
        layout.addWidget(rag_group)
        
        layout.addStretch()
        
        # Stats display
        self.stats_label = QLabel("📊 Statistics")
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 12px;
                color: #cdd6f4;
            }
        """)
        layout.addWidget(self.stats_label)
        
        return panel
    
    def _populate_node_tree(self):
        """Build initial node tree"""
        self.node_tree.clear()
        
        # SmolLM3 node
        smollm_item = QTreeWidgetItem(self.node_tree, ["SmolLM3-3B", "Active", "Model"])
        smollm_item.setForeground(1, QColor("#a6e3a1"))
        
        # Sub-components
        QTreeWidgetItem(smollm_item, ["Tokenizer", "Loaded", "Component"])
        QTreeWidgetItem(smollm_item, ["8-bit Quantization", "Active", "Optimization"])
        QTreeWidgetItem(smollm_item, ["CPU Backend", "Online", "Device"])
        
        # Llama 3.1 node
        llama_item = QTreeWidgetItem(self.node_tree, ["Llama-3.1-8B", "Active", "Model"])
        llama_item.setForeground(1, QColor("#a6e3a1"))
        
        # Sub-components
        QTreeWidgetItem(llama_item, ["Tokenizer", "Loaded", "Component"])
        QTreeWidgetItem(llama_item, ["4-bit Quantization", "Active", "Optimization"])
        QTreeWidgetItem(llama_item, ["GPU Backend (RTX 3060)", "Online", "Device"])
        
        # RAG System node
        rag_item = QTreeWidgetItem(self.node_tree, ["RAG System", "Active", "System"])
        rag_item.setForeground(1, QColor("#a6e3a1"))
        
        QTreeWidgetItem(rag_item, ["Document Ingestion", "Ready", "Component"])
        QTreeWidgetItem(rag_item, ["Vector Indexer", "Ready", "Component"])
        QTreeWidgetItem(rag_item, ["Retrieval Engine", "Ready", "Component"])
        
        # Heavy Thinking node
        ht_item = QTreeWidgetItem(self.node_tree, ["Heavy Thinking", "Enabled", "Agent"])
        ht_item.setForeground(1, QColor("#89b4fa"))
        
        QTreeWidgetItem(ht_item, ["Complexity Detector", "Active", "Logic"])
        QTreeWidgetItem(ht_item, ["Delegation Engine", "Active", "Logic"])
        
        self.node_tree.expandAll()
    
    def update_tool_activity(self, tool_data: dict):
        """Update tool activity display"""
        tool_name = tool_data.get('tool', 'Unknown')
        status = tool_data.get('status', 'running')
        duration = tool_data.get('duration', 0)
        
        # Status styling
        if status == 'success':
            color = '#a6e3a1'
            symbol = '✓'
            border_color = '#a6e3a1'
        elif status == 'error':
            color = '#f38ba8'
            symbol = '✗'
            border_color = '#f38ba8'
        else:
            color = '#f9e2af'
            symbol = '⟳'
            border_color = '#f9e2af'
        
        html = f"""
        <div style='margin: 8px 0; padding: 14px; background-color: #1e1e2e; 
                    border-left: 4px solid {border_color}; border-radius: 8px;'>
            <p style='color: {color}; font-weight: bold; margin: 0 0 6px 0; font-size: 14px;'>
                {symbol} {tool_name}
            </p>
            <p style='color: #a6adc8; margin: 0; font-size: 12px;'>
                <span style='color: #89b4fa;'>Duration:</span> {duration:.2f}s • 
                <span style='color: #89b4fa;'>Status:</span> {status}
            </p>
        </div>
        """
        
        # Clear empty state on first call
        if 'Tool calls will appear here' in self.tool_display.toPlainText():
            self.tool_display.clear()
        
        self.tool_display.append(html)
        self.tool_calls_history.append(tool_data)
    
    def _start_monitoring(self):
        """Start periodic stats updates"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_stats)
        self.monitor_timer.start(5000)  # Update every 5 seconds
    
    def _update_stats(self):
        """Update statistics display"""
        try:
            stats = self.engine.get_stats()
            stats_text = f"""📊 Statistics

Total Queries: {stats.get('total_queries', 0)}
Heavy Thinking Calls: {stats.get('heavy_thinking_calls', 0)}
Heavy Thinking Rate: {stats.get('heavy_thinking_rate', '0%')}
"""
            self.stats_label.setText(stats_text)
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    def _toggle_heavy_thinking(self, state):
        """Toggle heavy thinking mode"""
        enabled = state == Qt.CheckState.Checked.value
        self.engine.set_heavy_thinking(enabled)
        logger.info(f"Heavy thinking {'enabled' if enabled else 'disabled'}")
    
    def _update_threshold(self, value):
        """Update heavy thinking threshold"""
        try:
            threshold = int(value)
            self.engine.set_heavy_thinking_threshold(threshold)
            logger.info(f"Heavy thinking threshold set to {threshold} words")
        except ValueError:
            pass
    
    def _reload_model(self, model_name: str):
        """Reload specific model"""
        logger.info(f"Reloading {model_name}...")
        # Implementation depends on your engine's reload capabilities
        self.engine.load_model(model_name)
    
    def _reinit_rag(self):
        """Reinitialize RAG system"""
        logger.info("Reinitializing RAG system...")
        self.engine.initialize_rag()
    
    def _clear_rag_index(self):
        """Clear RAG index"""
        logger.info("Clearing RAG index...")
        # Implementation depends on your RAG system
    
    def _clear_tool_history(self):
        """Clear tool call history"""
        self.tool_display.clear()
        self.tool_calls_history = []
        self.tool_display.setHtml("""
            <div style='text-align: center; padding: 40px; color: #6c7086;'>
                <p style='font-size: 48px; margin: 0;'>⚡</p>
                <p style='margin: 10px 0 0 0;'>Tool calls will appear here</p>
                <p style='font-size: 11px; margin: 5px 0 0 0;'>History cleared</p>
            </div>
        """)
