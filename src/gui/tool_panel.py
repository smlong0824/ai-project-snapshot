"""Tool panel - Production UI"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QScrollArea
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class ToolPanel(QWidget):
    def __init__(self):
        super().__init__()
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
        
        # Title with icon
        title = QLabel("🔧 Tool Activity")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #f9e2af; background: transparent;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Real-time model execution monitoring")
        subtitle.setStyleSheet("color: #a6adc8; font-size: 12px; background: transparent;")
        layout.addWidget(subtitle)
        
        # Tool display with custom styling
        self.tool_display = QTextEdit()
        self.tool_display.setReadOnly(True)
        self.tool_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.tool_display)
        
        # Add helpful empty state
        self.tool_display.setHtml("""
            <div style='text-align: center; padding: 40px; color: #6c7086;'>
                <p style='font-size: 48px; margin: 0;'>⚡</p>
                <p style='margin: 10px 0 0 0;'>Tool calls will appear here</p>
                <p style='font-size: 11px; margin: 5px 0 0 0;'>Models: MixTrial • SmolVLM2</p>
            </div>
        """)
    
    def add_tool_call(self, tool_data: dict):
        tool_name = tool_data.get('tool', 'Unknown')
        status = tool_data.get('status', 'running')
        duration = tool_data.get('duration', 0)
        
        # Status-based styling
        if status == 'success':
            color = '#a6e3a1'
            bg_color = '#1e1e2e'
            symbol = '✓'
            border_color = '#a6e3a1'
        elif status == 'error':
            color = '#f38ba8'
            bg_color = '#1e1e2e'
            symbol = '✗'
            border_color = '#f38ba8'
        else:
            color = '#f9e2af'
            bg_color = '#1e1e2e'
            symbol = '⟳'
            border_color = '#f9e2af'
        
        html = f"""
        <div style='margin: 8px 0; padding: 14px; background-color: {bg_color}; 
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
