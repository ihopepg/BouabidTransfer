"""
Core Transfer Engine
Manages file transfers with multi-channel support, integrity checking, and resume capability
"""

import hashlib
import os
import threading
from pathlib import Path
from typing import List, Dict, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
import time
import json

from src.utils.logger import get_logger
from src.utils.config import get_config
from src.core.device_detector import DeviceInfo, DeviceConnectionType

logger = get_logger(__name__)


class TransferStatus(Enum):
    """Transfer status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TransferFile:
    """Represents a file to be transferred"""
    source_path: str
    destination_path: str
    size: int
    checksum: Optional[str] = None
    status: TransferStatus = TransferStatus.PENDING
    bytes_transferred: int = 0
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    channel_used: Optional[DeviceConnectionType] = None
    resume_data: Optional[Dict] = None


@dataclass
class TransferSession:
    """Represents a transfer session with multiple files"""
    session_id: str
    device_udid: str
    files: List[TransferFile] = field(default_factory=list)
    status: TransferStatus = TransferStatus.PENDING
    total_size: int = 0
    total_transferred: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_count: int = 0
    
    def __post_init__(self):
        self.total_size = sum(f.size for f in self.files)


class TransferEngine:
    """
    Main transfer engine coordinating multi-channel file transfers
    """
    
    def __init__(self, device_detector=None):
        self.config = get_config()
        self.device_detector = device_detector  # Reference to DeviceDetector
        self.active_sessions: Dict[str, TransferSession] = {}
        self.transfer_queue: Queue = Queue()
        self.workers: List[threading.Thread] = []
        self._running = False
        self._lock = threading.Lock()
        
        # Progress callbacks
        self.progress_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Channel managers
        self.channel_managers: Dict[DeviceConnectionType, any] = {}
        self._initialize_channels()
    
    def _initialize_channels(self):
        """Initialize channel-specific transfer managers"""
        try:
            from src.channels.usb_transfer import USBTransferManager
            self.channel_managers[DeviceConnectionType.USB] = USBTransferManager()
        except Exception as e:
            logger.warning(f"Failed to initialize USB transfer manager: {e}")
        
        try:
            from src.channels.wifi_transfer import WiFiTransferManager
            self.channel_managers[DeviceConnectionType.WIFI] = WiFiTransferManager()
        except Exception as e:
            logger.warning(f"Failed to initialize WiFi transfer manager: {e}")
        
        try:
            if self.config.get('bluetooth.enabled', False):  # Default to False
                from src.channels.bluetooth_transfer import BluetoothTransferManager
                self.channel_managers[DeviceConnectionType.BLUETOOTH] = BluetoothTransferManager()
                logger.debug("Bluetooth transfer manager initialized")
            else:
                logger.debug("Bluetooth disabled in configuration")
        except Exception as e:
            logger.debug(f"Bluetooth transfer manager not available: {e}")
    
    def start(self):
        """Start the transfer engine"""
        if self._running:
            return
        
        self._running = True
        num_workers = self.config.get('transfer.max_parallel_transfers', 4)
        
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name=f"TransferWorker-{i}"
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Transfer engine started with {num_workers} workers")
    
    def stop(self):
        """Stop the transfer engine"""
        self._running = False
        for worker in self.workers:
            worker.join(timeout=5.0)
        self.workers.clear()
        logger.info("Transfer engine stopped")
    
    def create_session(
        self,
        device: DeviceInfo,
        files: List[Dict[str, str]],
        destination: str
    ) -> str:
        """
        Create a new transfer session
        Args:
            device: Target device
            files: List of dicts with 'source' and optionally 'destination' keys
            destination: Base destination directory
        Returns:
            Session ID
        """
        session_id = f"session_{int(time.time() * 1000)}"
        session = TransferSession(
            session_id=session_id,
            device_udid=device.udid
        )
        
        # Create transfer files
        for file_info in files:
            source = file_info['source']
            dest = file_info.get('destination', os.path.basename(source))
            dest_path = os.path.join(destination, dest)
            
            # Get file size (will be updated when file is accessed)
            size = file_info.get('size', 0)
            
            transfer_file = TransferFile(
                source_path=source,
                destination_path=dest_path,
                size=size
            )
            session.files.append(transfer_file)
        
        with self._lock:
            self.active_sessions[session_id] = session
        
        logger.info(f"Created transfer session {session_id} with {len(files)} files")
        return session_id
    
    def start_transfer(self, session_id: str):
        """Start a transfer session"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return
            
            if session.status != TransferStatus.PENDING:
                logger.warning(f"Session {session_id} already started")
                return
            
            session.status = TransferStatus.QUEUED
            session.start_time = time.time()
        
        # Queue all files
        for transfer_file in session.files:
            self.transfer_queue.put((session_id, transfer_file))
        
        logger.info(f"Started transfer session {session_id}")
    
    def pause_transfer(self, session_id: str):
        """Pause a transfer session"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if session:
                session.status = TransferStatus.PAUSED
                logger.info(f"Paused transfer session {session_id}")
    
    def resume_transfer(self, session_id: str):
        """Resume a paused transfer session"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if session and session.status == TransferStatus.PAUSED:
                session.status = TransferStatus.QUEUED
                # Re-queue pending files
                for transfer_file in session.files:
                    if transfer_file.status in [TransferStatus.PENDING, TransferStatus.FAILED]:
                        self.transfer_queue.put((session_id, transfer_file))
                logger.info(f"Resumed transfer session {session_id}")
    
    def cancel_transfer(self, session_id: str):
        """Cancel a transfer session"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if session:
                session.status = TransferStatus.CANCELLED
                logger.info(f"Cancelled transfer session {session_id}")
    
    def _worker_loop(self):
        """Worker thread loop for processing transfers"""
        while self._running:
            try:
                session_id, transfer_file = self.transfer_queue.get(timeout=1.0)
                
                # Check if session is still active
                with self._lock:
                    session = self.active_sessions.get(session_id)
                    if not session or session.status == TransferStatus.CANCELLED:
                        continue
                    if session.status == TransferStatus.PAUSED:
                        self.transfer_queue.put((session_id, transfer_file))
                        continue
                
                # Execute transfer
                self._transfer_file(session, transfer_file)
                
            except Empty:
                # Timeout is expected when queue is empty - just continue
                continue
            except Exception as e:
                if self._running:
                    logger.error(f"Error in worker loop: {e}", exc_info=True)
    
    def _transfer_file(self, session: TransferSession, transfer_file: TransferFile):
        """Execute a single file transfer"""
        transfer_file.status = TransferStatus.IN_PROGRESS
        transfer_file.start_time = time.time()
        
        try:
            # Select best available channel
            device = self._get_device(session.device_udid)
            if not device:
                raise Exception("Device not found")
            
            channel = self._select_channel(device)
            if not channel:
                raise Exception("No available transfer channel")
            
            transfer_file.channel_used = channel
            
            # Get channel manager
            manager = self.channel_managers.get(channel)
            if not manager:
                raise Exception(f"Channel manager not available for {channel}")
            
            # Check for resume capability
            if self.config.get('transfer.resume_enabled', True):
                resume_data = self._load_resume_data(transfer_file)
                if resume_data:
                    transfer_file.resume_data = resume_data
                    transfer_file.bytes_transferred = resume_data.get('bytes_transferred', 0)
            
            # Execute transfer
            manager.transfer_file(
                device,
                transfer_file.source_path,
                transfer_file.destination_path,
                progress_callback=lambda bytes_transferred: self._on_progress(
                    session, transfer_file, bytes_transferred
                ),
                resume_from=transfer_file.bytes_transferred
            )
            
            # Verify checksum if enabled
            if self.config.get('transfer.enable_checksum', True):
                expected_checksum = transfer_file.checksum
                if expected_checksum:
                    actual_checksum = self._calculate_checksum(transfer_file.destination_path)
                    if actual_checksum != expected_checksum:
                        raise Exception("Checksum verification failed")
            
            transfer_file.status = TransferStatus.COMPLETED
            transfer_file.end_time = time.time()
            
            # Update session
            with self._lock:
                session.total_transferred += transfer_file.size
                self._check_session_completion(session)
            
            self._notify_progress(session, transfer_file)
            
        except Exception as e:
            transfer_file.status = TransferStatus.FAILED
            transfer_file.error_message = str(e)
            transfer_file.end_time = time.time()
            
            with self._lock:
                session.error_count += 1
                # Save resume data for retry
                if self.config.get('transfer.resume_enabled', True):
                    self._save_resume_data(transfer_file)
            
            logger.error(f"Transfer failed for {transfer_file.source_path}: {e}")
            self._notify_error(session, transfer_file, str(e))
    
    def _select_channel(self, device: DeviceInfo) -> Optional[DeviceConnectionType]:
        """Select the best available channel for transfer"""
        priorities = {
            DeviceConnectionType.USB: self.config.get('transfer.channel_priority.usb', 1),
            DeviceConnectionType.WIFI: self.config.get('transfer.channel_priority.wifi', 2),
            DeviceConnectionType.BLUETOOTH: self.config.get('transfer.channel_priority.bluetooth', 3)
        }
        
        available = []
        if device.connection_type == DeviceConnectionType.USB:
            available.append(DeviceConnectionType.USB)
        # Check for additional available channels
        if self.channel_managers.get(DeviceConnectionType.WIFI):
            available.append(DeviceConnectionType.WIFI)
        if self.channel_managers.get(DeviceConnectionType.BLUETOOTH):
            available.append(DeviceConnectionType.BLUETOOTH)
        
        if not available:
            return None
        
        # Sort by priority
        available.sort(key=lambda x: priorities.get(x, 999))
        return available[0]
    
    def _on_progress(self, session: TransferSession, transfer_file: TransferFile, bytes_transferred: int):
        """Handle transfer progress updates"""
        transfer_file.bytes_transferred = bytes_transferred
        self._notify_progress(session, transfer_file)
    
    def _check_session_completion(self, session: TransferSession):
        """Check if all files in session are completed"""
        completed = sum(1 for f in session.files if f.status == TransferStatus.COMPLETED)
        failed = sum(1 for f in session.files if f.status == TransferStatus.FAILED)
        
        if completed + failed == len(session.files):
            session.status = TransferStatus.COMPLETED if failed == 0 else TransferStatus.FAILED
            session.end_time = time.time()
            self._notify_completion(session)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        algorithm = self.config.get('transfer.checksum_algorithm', 'sha256')
        hash_obj = hashlib.new(algorithm)
        
        buffer_size = self.config.get('transfer.buffer_size', 1048576)
        with open(file_path, 'rb') as f:
            while chunk := f.read(buffer_size):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def _save_resume_data(self, transfer_file: TransferFile):
        """Save resume data for interrupted transfers"""
        resume_dir = Path("transfers/resume")
        resume_dir.mkdir(parents=True, exist_ok=True)
        
        resume_file = resume_dir / f"{hash(transfer_file.source_path)}.json"
        data = {
            'source_path': transfer_file.source_path,
            'destination_path': transfer_file.destination_path,
            'bytes_transferred': transfer_file.bytes_transferred,
            'size': transfer_file.size
        }
        
        with open(resume_file, 'w') as f:
            json.dump(data, f)
    
    def _load_resume_data(self, transfer_file: TransferFile) -> Optional[Dict]:
        """Load resume data if available"""
        resume_dir = Path("transfers/resume")
        resume_file = resume_dir / f"{hash(transfer_file.source_path)}.json"
        
        if resume_file.exists():
            try:
                with open(resume_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load resume data: {e}")
        
        return None
    
    def _get_device(self, udid: str) -> Optional[DeviceInfo]:
        """Get device info from DeviceDetector"""
        if self.device_detector:
            return self.device_detector.get_device(udid)
        return None
    
    def _notify_progress(self, session: TransferSession, transfer_file: TransferFile):
        """Notify progress callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(session, transfer_file)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def _notify_completion(self, session: TransferSession):
        """Notify completion callbacks"""
        for callback in self.completion_callbacks:
            try:
                callback(session)
            except Exception as e:
                logger.error(f"Error in completion callback: {e}")
    
    def _notify_error(self, session: TransferSession, transfer_file: TransferFile, error: str):
        """Notify error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(session, transfer_file, error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    def register_progress_callback(self, callback: Callable):
        """Register progress callback"""
        self.progress_callbacks.append(callback)
    
    def register_completion_callback(self, callback: Callable):
        """Register completion callback"""
        self.completion_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable):
        """Register error callback"""
        self.error_callbacks.append(callback)
    
    def get_session(self, session_id: str) -> Optional[TransferSession]:
        """Get transfer session by ID"""
        with self._lock:
            return self.active_sessions.get(session_id)

