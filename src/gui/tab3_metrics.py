"""Tab 3: Performance & Metrics"""
import logging
import psutil
from collections import deque
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QGridLayout, QFrame, QProgressBar, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QPen, QColor
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

logger = logging.getLogger(__name__)

class MetricCard(QFrame):
    """Individual metric display card"""
    def __init__(self, icon, title, value="--", unit=""):
        super().__init__()
        self.unit = unit
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Icon and title
        header = QLabel(f"{icon} {title}")
        header.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 13px; background: transparent; border: none;")
        layout.addWidget(header)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        layout.addWidget(self.value_label)
        
        # Unit label
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent; border: none;")
            layout.addWidget(unit_label)
    
    def update_value(self, value: str):
        self.value_label.setText(value)
    
    def update_value_with_color(self, value: str, threshold_warning: float = 70, threshold_danger: float = 90):
        """Update value with color coding based on thresholds"""
        try:
            numeric_value = float(value.replace('%', '').replace('GB', '').replace('°C', ''))
            if numeric_value >= threshold_danger:
                color = '#f38ba8'  # Red
            elif numeric_value >= threshold_warning:
                color = '#f9e2af'  # Yellow
            else:
                color = '#a6e3a1'  # Green
            
            self.value_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        except:
            pass
        
        self.value_label.setText(value)


class LiveChart(QWidget):
    """Live updating line chart"""
    def __init__(self, title: str, max_points: int = 60):
        super().__init__()
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create chart
        self.series = QLineSeries()
        pen = QPen(QColor("#89b4fa"))
        pen.setWidth(2)
        self.series.setPen(pen)
        
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(title)
        self.chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.chart.legend().hide()
        
        # Customize chart appearance
        self.chart.setBackgroundBrush(QColor("#1e1e2e"))
        self.chart.setTitleBrush(QColor("#cdd6f4"))
        
        # Axes
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, max_points)
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setLabelsColor(QColor("#6c7086"))
        self.axis_x.setGridLineColor(QColor("#313244"))
        
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.axis_y.setLabelFormat("%.1f")
        self.axis_y.setLabelsColor(QColor("#6c7086"))
        self.axis_y.setGridLineColor(QColor("#313244"))
        
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        # Chart view
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setStyleSheet("background-color: #1e1e2e; border: 2px solid #313244; border-radius: 8px;")
        
        layout.addWidget(chart_view)
    
    def add_point(self, value: float):
        """Add new data point"""
        self.data_points.append(value)
        
        # Update series
        self.series.clear()
        for i, point in enumerate(self.data_points):
            self.series.append(i, point)
        
        # Auto-scale Y axis
        if self.data_points:
            max_value = max(self.data_points)
            self.axis_y.setRange(0, max(100, max_value * 1.1))


class MetricsTab(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.inference_history = deque(maxlen=100)
        self._init_ui()
        self._start_monitoring()
    
    def _init_ui(self):
        """Build metrics interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # Header
        header = QLabel("📊 Performance & Metrics")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #94e2d5; background: transparent;")
        main_layout.addWidget(header)
        
        # Metric cards grid
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        
        self.cpu_card = MetricCard("🔥", "CPU Usage", unit="Average across 32 cores")
        self.memory_card = MetricCard("💾", "Memory", unit="System RAM")
        self.gpu_card = MetricCard("🎮", "GPU Load", unit="RTX 3060")
        self.gpu_temp_card = MetricCard("🌡️", "GPU Temp", unit="Temperature")
        self.vram_card = MetricCard("💿", "VRAM", unit="Video Memory")
        self.inference_card = MetricCard("⚡", "Inference", unit="Last query")
        
        cards_layout.addWidget(self.cpu_card, 0, 0)
        cards_layout.addWidget(self.memory_card, 0, 1)
        cards_layout.addWidget(self.gpu_card, 0, 2)
        cards_layout.addWidget(self.gpu_temp_card, 1, 0)
        cards_layout.addWidget(self.vram_card, 1, 1)
        cards_layout.addWidget(self.inference_card, 1, 2)
        
        main_layout.addLayout(cards_layout)
        
        # Live charts
        charts_layout = QHBoxLayout()
        
        self.cpu_chart = LiveChart("CPU Usage (%)", max_points=60)
        self.gpu_chart = LiveChart("GPU Load (%)", max_points=60)
        
        charts_layout.addWidget(self.cpu_chart)
        charts_layout.addWidget(self.gpu_chart)
        
        main_layout.addLayout(charts_layout)
        
        # Model info section
        model_info = self._create_model_info_section()
        main_layout.addWidget(model_info)
        
        # Inference history
        inference_group = QGroupBox("📈 Inference History")
        inference_group.setStyleSheet("""
            QGroupBox {
                background-color: #181825;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 16px;
                margin-top: 12px;
                color: #cdd6f4;
                font-weight: bold;
            }
        """)
        inference_layout = QVBoxLayout(inference_group)
        
        self.inference_stats_label = QLabel("No queries yet")
        self.inference_stats_label.setStyleSheet("color: #a6adc8; background: transparent; border: none;")
        inference_layout.addWidget(self.inference_stats_label)
        
        main_layout.addWidget(inference_group)
    
    def _create_model_info_section(self):
        """Model information display"""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border: 2px solid #313244;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)
        
        info_title = QLabel("🤖 Active Models")
        info_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        info_title.setStyleSheet("color: #89b4fa; background: transparent; border: none;")
        info_layout.addWidget(info_title)
        
        # SmolLM3 info
        smollm_layout = QHBoxLayout()
        self.smollm_label = QLabel("SmolLM3-3B")
        self.smollm_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.smollm_label.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        smollm_layout.addWidget(self.smollm_label)
        
        self.smollm_status = QLabel("● Online")
        self.smollm_status.setStyleSheet("color: #a6e3a1; background: transparent; border: none;")
        smollm_layout.addWidget(self.smollm_status)
        smollm_layout.addStretch()
        info_layout.addLayout(smollm_layout)
        
        smollm_details = QLabel("Device: CPU (Ryzen 9 5950X) • Quantization: 8-bit • Context: 2K")
        smollm_details.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent; border: none;")
        info_layout.addWidget(smollm_details)
        
        # Llama 3.1 info
        llama_layout = QHBoxLayout()
        self.llama_label = QLabel("Llama-3.1-8B")
        self.llama_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.llama_label.setStyleSheet("color: #cdd6f4; background: transparent; border: none;")
        llama_layout.addWidget(self.llama_label)
        
        self.llama_status = QLabel("● Online")
        self.llama_status.setStyleSheet("color: #a6e3a1; background: transparent; border: none;")
        llama_layout.addWidget(self.llama_status)
        llama_layout.addStretch()
        info_layout.addLayout(llama_layout)
        
        llama_details = QLabel("Device: GPU (RTX 3060 12GB) • Quantization: 4-bit • Context: 8K")
        llama_details.setStyleSheet("color: #6c7086; font-size: 11px; background: transparent; border: none;")
        info_layout.addWidget(llama_details)
        
        return info_frame
    
    def _start_monitoring(self):
        """Start real-time monitoring"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_system_metrics)
        self.monitor_timer.start(2000)  # Update every 2 seconds
    
    def _update_system_metrics(self):
        """Update all system metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_card.update_value_with_color(f"{cpu_percent:.1f}%")
            self.cpu_chart.add_point(cpu_percent)
            
            # Memory
            mem = psutil.virtual_memory()
            mem_used = mem.used / 1e9
            mem_percent = mem.percent
            self.memory_card.update_value_with_color(f"{mem_used:.1f}GB")
            
            # GPU (if available)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_load = gpu.load * 100
                    gpu_temp = gpu.temperature
                    gpu_mem_used = gpu.memoryUsed / 1024  # Convert to GB
                    
                    self.gpu_card.update_value_with_color(f"{gpu_load:.1f}%")
                    self.gpu_temp_card.update_value_with_color(f"{gpu_temp:.0f}°C", 75, 85)
                    self.vram_card.update_value_with_color(f"{gpu_mem_used:.1f}GB")
                    self.gpu_chart.add_point(gpu_load)
                else:
                    self.gpu_card.update_value("N/A")
                    self.gpu_temp_card.update_value("N/A")
                    self.vram_card.update_value("N/A")
            except Exception as e:
                logger.debug(f"GPU metrics unavailable: {e}")
                self.gpu_card.update_value("N/A")
                self.gpu_temp_card.update_value("N/A")
                self.vram_card.update_value("N/A")
        
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
    
    def update_metrics(self, metrics: dict):
        """Update metrics from engine"""
        if 'inference_time' in metrics:
            inference_time = metrics['inference_time']
            self.inference_card.update_value(f"{inference_time:.2f}s")
            self.inference_history.append(inference_time)
            
            # Update inference stats
            if self.inference_history:
                avg_time = sum(self.inference_history) / len(self.inference_history)
                min_time = min(self.inference_history)
                max_time = max(self.inference_history)
                
                stats_text = f"""Last: {inference_time:.2f}s  •  Avg: {avg_time:.2f}s  •  Min: {min_time:.2f}s  •  Max: {max_time:.2f}s
Total Queries: {len(self.inference_history)}"""
                
                if metrics.get('used_heavy_thinking'):
                    stats_text += "  •  🧠 Used Heavy Thinking"
                
                self.inference_stats_label.setText(stats_text)
