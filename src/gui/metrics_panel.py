"""Metrics panel - Production UI"""
import psutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

class MetricCard(QFrame):
    """Individual metric card widget"""
    def __init__(self, icon, title, value="--"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        
        # Icon and title
        header = QLabel(f"{icon} {title}")
        header.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(header)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        layout.addWidget(self.value_label)
    
    def update_value(self, value: str):
        self.value_label.setText(value)

class MetricsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._start_monitoring()
    
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
        title = QLabel("📊 Performance Metrics")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #94e2d5; background: transparent;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Real-time system monitoring")
        subtitle.setStyleSheet("color: #a6adc8; font-size: 12px; background: transparent;")
        layout.addWidget(subtitle)
        
        # Metrics grid
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Create metric cards
        self.cpu_card = MetricCard("🔥", "CPU Usage")
        self.memory_card = MetricCard("💾", "Memory")
        self.gpu_card = MetricCard("🎮", "GPU Load")
        self.inference_card = MetricCard("⚡", "Inference")
        
        grid.addWidget(self.cpu_card, 0, 0)
        grid.addWidget(self.memory_card, 0, 1)
        grid.addWidget(self.gpu_card, 1, 0)
        grid.addWidget(self.inference_card, 1, 1)
        
        layout.addLayout(grid)
        
        # Model info section
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)
        
        info_title = QLabel("🤖 Active Model")
        info_title.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 12px; background: transparent; border: none;")
        info_layout.addWidget(info_title)
        
        self.model_label = QLabel("SmolLM3-3B")
        self.model_label.setStyleSheet("color: #cdd6f4; font-size: 14px; background: transparent; border: none;")
        info_layout.addWidget(self.model_label)
        
        self.quant_label = QLabel("Quantization: 8-bit")
        self.quant_label.setStyleSheet("color: #a6adc8; font-size: 11px; background: transparent; border: none;")
        info_layout.addWidget(self.quant_label)
        
        self.device_label = QLabel("Device: CPU (Ryzen 9 5950X)")
        self.device_label.setStyleSheet("color: #a6adc8; font-size: 11px; background: transparent; border: none;")
        info_layout.addWidget(self.device_label)
        
        layout.addWidget(info_frame)
        layout.addStretch()
    
    def _start_monitoring(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_system_metrics)
        self.timer.start(2000)
    
    def _update_system_metrics(self):
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_card.update_value(f"{cpu_percent:.1f}%")
        
        # Memory
        mem = psutil.virtual_memory()
        mem_used = mem.used / 1e9
        mem_total = mem.total / 1e9
        self.memory_card.update_value(f"{mem_used:.1f}GB")
        
        # GPU
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                self.gpu_card.update_value(f"{gpu.load * 100:.1f}%")
        except:
            self.gpu_card.update_value("N/A")
    
    def update_metrics(self, metrics: dict):
        if 'inference_time' in metrics:
            self.inference_card.update_value(f"{metrics['inference_time']:.2f}s")
        
        if 'model' in metrics:
            self.model_label.setText(metrics['model'])
