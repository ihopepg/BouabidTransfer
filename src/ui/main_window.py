"""
Main Application Window
Professional, clean UI for BouabidTransfer
"""

import sys
from pathlib import Path
from typing import Optional, List
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QSplitter, QGroupBox, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QStatusBar, QMenuBar, QMenu, QAction, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QLinearGradient, QBrush

from src.utils.logger import get_logger
from src.utils.config import get_config
from src.core.device_detector import DeviceDetector, DeviceInfo
from src.core.transfer_engine import TransferEngine, TransferSession, TransferFile, TransferStatus

logger = get_logger(__name__)


class DeviceListWidget(QListWidget):
    """Custom widget for displaying connected devices"""
    
    device_selected = pyqtSignal(str)  # Emits UDID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        self.itemClicked.connect(self._on_item_clicked)
    
    def _on_item_clicked(self, item):
        """Handle device selection"""
        udid = item.data(Qt.UserRole)
        self.device_selected.emit(udid)
    
    def update_devices(self, devices: List[DeviceInfo]):
        """Update device list"""
        self.clear()
        for device in devices:
            item = QListWidgetItem(f"{device.name}\n{device.model}")
            item.setData(Qt.UserRole, device.udid)
            self.addItem(item)


class TransferProgressWidget(QWidget):
    """Widget showing transfer progress for a file"""
    
    def __init__(self, transfer_file: TransferFile, parent=None):
        super().__init__(parent)
        self.transfer_file = transfer_file
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # File name
        name_label = QLabel(Path(self.transfer_file.source_path).name)
        name_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(name_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.transfer_file.size)
        self.progress_bar.setValue(self.transfer_file.bytes_transferred)
        layout.addWidget(self.progress_bar)
        
        # Status and speed
        status_layout = QHBoxLayout()
        self.status_label = QLabel(self.transfer_file.status.value)
        self.speed_label = QLabel("0 MB/s")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.speed_label)
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
    
    def update_progress(self, bytes_transferred: int, speed_mbps: float = 0.0):
        """Update progress display"""
        self.progress_bar.setValue(bytes_transferred)
        self.speed_label.setText(f"{speed_mbps:.2f} MB/s")
        
        percentage = (bytes_transferred / self.transfer_file.size * 100) if self.transfer_file.size > 0 else 0
        self.status_label.setText(f"{self.transfer_file.status.value} - {percentage:.1f}%")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.device_detector = DeviceDetector()
        self.transfer_engine = TransferEngine(device_detector=self.device_detector)
        self.current_device: Optional[DeviceInfo] = None
        self.current_session: Optional[str] = None
        
        self._setup_ui()
        self._setup_connections()
        self._start_services()
    
    def _setup_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("BouabidTransfer - iPhone to PC Data Transfer")
        self.setMinimumSize(1000, 700)
        
        # Apply modern style
        self._apply_modern_style()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Header with attribution
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Left panel - Devices and file selection
        left_panel = self._create_left_panel()
        
        # Right panel - Transfer progress
        right_panel = self._create_right_panel()
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        content_layout.addWidget(splitter)
        
        # Add content to main layout
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # Menu bar
        self._create_menu_bar()
        
        # Status bar with modern style
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-top: 1px solid #3d3d3d;
                padding: 5px;
            }
        """)
        self.status_bar.showMessage("Ready - Connect your iPhone via USB")
    
    def _apply_modern_style(self):
        """Apply modern, colorful design to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #252525;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4a9eff;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #5cb0ff;
            }
            QPushButton:pressed {
                background-color: #3a8eef;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #666666;
            }
            QListWidget {
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #4a9eff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QTreeWidget {
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 5px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #4a9eff;
                color: white;
            }
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                text-align: center;
                background-color: #252525;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff, stop:1 #5cb0ff);
                border-radius: 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QTextEdit {
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 5px;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #252525;
                color: #ffffff;
                border-bottom: 1px solid #3d3d3d;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #4a9eff;
            }
            QMenu {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
            }
        """)
    
    def _create_header(self) -> QWidget:
        """Create modern header with attribution"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff, stop:1 #5cb0ff);
                border: none;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        header.setLayout(layout)
        
        # App title
        title_label = QLabel("BouabidTransfer")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Attribution
        attribution_label = QLabel("Made by Achraf Bouabid")
        attribution_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: normal;
                background: transparent;
                padding: 5px 15px;
                border-radius: 15px;
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        layout.addWidget(attribution_label)
        
        return header
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with device list and file selection"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Device section
        device_group = QGroupBox("Connected Devices")
        device_layout = QVBoxLayout()
        
        self.device_list = DeviceListWidget()
        device_layout.addWidget(self.device_list)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_devices)
        device_layout.addWidget(refresh_btn)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # File selection section
        file_group = QGroupBox("📁 Files to Transfer")
        file_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
            }
        """)
        file_layout = QVBoxLayout()
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File", "Size", "Status"])
        self.file_tree.setColumnWidth(0, 300)
        file_layout.addWidget(self.file_tree)
        
        file_buttons_layout = QHBoxLayout()
        file_buttons_layout.setSpacing(5)
        
        add_files_btn = QPushButton("➕ Add Files")
        add_files_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        add_files_btn.clicked.connect(self._add_files)
        
        add_folder_btn = QPushButton("📂 Add Folder")
        add_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        add_folder_btn.clicked.connect(self._add_folder)
        
        remove_btn = QPushButton("🗑 Remove")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e4606d;
            }
        """)
        remove_btn.clicked.connect(self._remove_selected_files)
        
        file_buttons_layout.addWidget(add_files_btn)
        file_buttons_layout.addWidget(add_folder_btn)
        file_buttons_layout.addWidget(remove_btn)
        file_layout.addLayout(file_buttons_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Destination selection
        dest_group = QGroupBox("💾 Destination")
        dest_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
            }
        """)
        dest_layout = QVBoxLayout()
        
        dest_layout_widget = QHBoxLayout()
        dest_layout_widget.setSpacing(5)
        
        self.dest_label = QLabel("Not selected")
        self.dest_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                padding: 5px;
                background-color: #252525;
                border-radius: 4px;
            }
        """)
        dest_layout_widget.addWidget(self.dest_label)
        
        browse_btn = QPushButton("🔍 Browse...")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7d868e;
            }
        """)
        browse_btn.clicked.connect(self._browse_destination)
        dest_layout_widget.addWidget(browse_btn)
        dest_layout.addLayout(dest_layout_widget)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Transfer buttons
        transfer_buttons_layout = QHBoxLayout()
        transfer_buttons_layout.setSpacing(10)
        
        self.start_btn = QPushButton("▶ Start Transfer")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #5cb0ff;
            }
        """)
        self.start_btn.clicked.connect(self._start_transfer)
        self.start_btn.setEnabled(False)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffa500;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #ffb533;
            }
        """)
        self.pause_btn.clicked.connect(self._pause_transfer)
        self.pause_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("⏹ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        self.cancel_btn.clicked.connect(self._cancel_transfer)
        self.cancel_btn.setEnabled(False)
        
        transfer_buttons_layout.addWidget(self.start_btn)
        transfer_buttons_layout.addWidget(self.pause_btn)
        transfer_buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(transfer_buttons_layout)
        
        layout.addStretch()
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with transfer progress"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #1e1e1e;")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        panel.setLayout(layout)
        
        # Overall progress
        overall_group = QGroupBox("📊 Transfer Progress")
        overall_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
            }
        """)
        overall_layout = QVBoxLayout()
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        overall_layout.addWidget(self.overall_progress)
        
        stats_layout = QHBoxLayout()
        self.files_label = QLabel("Files: 0/0")
        self.speed_label = QLabel("Speed: 0 MB/s")
        self.eta_label = QLabel("ETA: --:--")
        stats_layout.addWidget(self.files_label)
        stats_layout.addWidget(self.speed_label)
        stats_layout.addWidget(self.eta_label)
        overall_layout.addLayout(stats_layout)
        
        overall_group.setLayout(overall_layout)
        layout.addWidget(overall_group)
        
        # Individual file progress
        files_group = QGroupBox("📋 File Progress")
        files_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
            }
        """)
        files_layout = QVBoxLayout()
        
        self.progress_list = QListWidget()
        files_layout.addWidget(self.progress_list)
        
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)
        
        return panel
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.device_list.device_selected.connect(self._on_device_selected)
        self.device_detector.register_detection_callback(self._on_device_detected)
        self.device_detector.register_removal_callback(self._on_device_removed)
        self.transfer_engine.register_progress_callback(self._on_transfer_progress)
        self.transfer_engine.register_completion_callback(self._on_transfer_complete)
        self.transfer_engine.register_error_callback(self._on_transfer_error)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(1000)  # Update every second
    
    def _start_services(self):
        """Start background services"""
        self.device_detector.start_detection()
        self.transfer_engine.start()
        self._refresh_devices()
    
    def _refresh_devices(self):
        """Refresh device list"""
        devices = self.device_detector.get_devices()
        self.device_list.update_devices(devices)
        if devices:
            self.status_bar.showMessage(f"Found {len(devices)} device(s)")
        else:
            self.status_bar.showMessage("No devices found - Connect your iPhone via USB")
    
    def _on_device_detected(self, device: DeviceInfo):
        """Handle device detection"""
        self._refresh_devices()
        logger.info(f"Device detected: {device.name} ({device.udid})")
    
    def _on_device_removed(self, udid: str):
        """Handle device removal"""
        self._refresh_devices()
        if self.current_device and self.current_device.udid == udid:
            self.current_device = None
            self.status_bar.showMessage("Device disconnected")
    
    def _on_device_selected(self, udid: str):
        """Handle device selection"""
        self.current_device = self.device_detector.get_device(udid)
        if self.current_device:
            self.status_bar.showMessage(f"Selected: {self.current_device.name}")
            self._check_transfer_ready()
    
    def _add_files(self):
        """Add files to transfer list"""
        # In production, this would browse files on the device
        # For now, show a message
        QMessageBox.information(self, "Add Files", "File selection from device will be implemented with device connection")
    
    def _add_folder(self):
        """Add folder to transfer list"""
        QMessageBox.information(self, "Add Folder", "Folder selection from device will be implemented with device connection")
    
    def _remove_selected_files(self):
        """Remove selected files from list"""
        selected = self.file_tree.selectedItems()
        for item in selected:
            index = self.file_tree.indexOfTopLevelItem(item)
            self.file_tree.takeTopLevelItem(index)
    
    def _browse_destination(self):
        """Browse for destination folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.destination_path = folder
            self.dest_label.setText(folder)
            self._check_transfer_ready()
    
    def _check_transfer_ready(self):
        """Check if transfer can be started"""
        has_device = self.current_device is not None
        has_files = self.file_tree.topLevelItemCount() > 0
        has_destination = hasattr(self, 'destination_path') and self.destination_path
        
        self.start_btn.setEnabled(has_device and has_files and has_destination)
    
    def _start_transfer(self):
        """Start file transfer"""
        if not self.current_device:
            QMessageBox.warning(self, "No Device", "Please select a device first")
            return
        
        files = []
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            files.append({
                'source': item.text(0),
                'size': 0  # Would get from device
            })
        
        if not files:
            QMessageBox.warning(self, "No Files", "Please add files to transfer")
            return
        
        self.current_session = self.transfer_engine.create_session(
            self.current_device,
            files,
            self.destination_path
        )
        
        self.transfer_engine.start_transfer(self.current_session)
        
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        
        self.status_bar.showMessage("Transfer started")
    
    def _pause_transfer(self):
        """Pause or resume transfer"""
        if self.current_session:
            session = self.transfer_engine.get_session(self.current_session)
            if session and session.status == TransferStatus.PAUSED:
                # Resume
                self.transfer_engine.resume_transfer(self.current_session)
                self.pause_btn.setText("Pause")
                self.status_bar.showMessage("Transfer resumed")
            else:
                # Pause
                self.transfer_engine.pause_transfer(self.current_session)
                self.pause_btn.setText("Resume")
                self.status_bar.showMessage("Transfer paused")
    
    def _cancel_transfer(self):
        """Cancel transfer"""
        if self.current_session:
            reply = QMessageBox.question(
                self, "Cancel Transfer",
                "Are you sure you want to cancel the transfer?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.transfer_engine.cancel_transfer(self.current_session)
                self.start_btn.setEnabled(True)
                self.pause_btn.setEnabled(False)
                self.cancel_btn.setEnabled(False)
                self.status_bar.showMessage("Transfer cancelled")
    
    def _on_transfer_progress(self, session: TransferSession, transfer_file: TransferFile):
        """Handle transfer progress update"""
        self._update_ui()
    
    def _on_transfer_complete(self, session: TransferSession):
        """Handle transfer completion"""
        QMessageBox.information(self, "Transfer Complete", "All files transferred successfully!")
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.status_bar.showMessage("Transfer completed")
    
    def _on_transfer_error(self, session: TransferSession, transfer_file: TransferFile, error: str):
        """Handle transfer error"""
        QMessageBox.warning(self, "Transfer Error", f"Error transferring {transfer_file.source_path}:\n{error}")
    
    def _update_ui(self):
        """Update UI elements"""
        if self.current_session:
            session = self.transfer_engine.get_session(self.current_session)
            if session:
                # Update overall progress
                if session.total_size > 0:
                    progress = int((session.total_transferred / session.total_size) * 100)
                    self.overall_progress.setValue(progress)
                
                # Update stats
                completed = sum(1 for f in session.files if f.status == TransferStatus.COMPLETED)
                self.files_label.setText(f"Files: {completed}/{len(session.files)}")
    
    def _show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog will be implemented")
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About BouabidTransfer",
            "BouabidTransfer v1.0.0\n\n"
            "Professional iPhone to PC Data Transfer Application\n\n"
            "Features:\n"
            "- Multi-channel transfer (USB, Wi-Fi, Bluetooth)\n"
            "- Data integrity verification\n"
            "- Resume interrupted transfers\n"
            "- Support for all iPhone models\n"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.current_session:
            reply = QMessageBox.question(
                self, "Transfer in Progress",
                "A transfer is in progress. Do you want to close anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        self.device_detector.stop_detection()
        self.transfer_engine.stop()
        event.accept()

