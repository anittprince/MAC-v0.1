"""
MAC Assistant - Mobile Companion App Integration
Cross-platform mobile app support with real-time synchronization.
"""

import json
import os
import time
import threading
import websocket
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import dataclass
import qrcode
from io import BytesIO
import base64

@dataclass
class MobileDevice:
    """Represents a connected mobile device."""
    device_id: str
    device_name: str
    platform: str  # 'android' or 'ios'
    app_version: str
    last_seen: datetime
    location: Optional[Dict[str, float]] = None
    push_token: Optional[str] = None
    is_active: bool = True

class MobileCompanionManager:
    """Manages mobile app connections and synchronization."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize mobile companion manager."""
        self.data_dir = Path(data_dir)
        self.mobile_dir = self.data_dir / "mobile"
        self.mobile_dir.mkdir(parents=True, exist_ok=True)
        
        # Database and config files
        self.devices_db = self.mobile_dir / "mobile_devices.db"
        self.sync_queue = self.mobile_dir / "sync_queue.json"
        self.mobile_config = self.mobile_dir / "mobile_config.json"
        
        # Initialize components
        self._init_mobile_db()
        self.location_manager = LocationManager(self.mobile_dir)
        self.push_notification_manager = PushNotificationManager(self.mobile_dir)
        self.sync_manager = RealTimeSyncManager(self.mobile_dir)
        self.offline_manager = OfflineManager(self.mobile_dir)
        
        # Active connections
        self.connected_devices = {}
        self.websocket_server = None
        self.server_running = False
        
    def _init_mobile_db(self):
        """Initialize mobile devices database."""
        conn = sqlite3.connect(self.devices_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_devices (
                device_id TEXT PRIMARY KEY,
                device_name TEXT NOT NULL,
                platform TEXT NOT NULL,
                app_version TEXT,
                last_seen TEXT,
                location_data TEXT,
                push_token TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                event_type TEXT,
                event_data TEXT,
                timestamp TEXT,
                synced BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (device_id) REFERENCES mobile_devices (device_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS location_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                latitude REAL,
                longitude REAL,
                accuracy REAL,
                timestamp TEXT,
                FOREIGN KEY (device_id) REFERENCES mobile_devices (device_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_mobile_server(self, port: int = 8765) -> Dict[str, Any]:
        """Start WebSocket server for mobile connections."""
        try:
            # Generate QR code for easy pairing
            pairing_info = {
                'server_url': f'ws://localhost:{port}',
                'pairing_code': str(uuid.uuid4())[:8],
                'timestamp': datetime.now().isoformat()
            }
            
            # Save pairing info
            with open(self.mobile_config, 'w') as f:
                json.dump(pairing_info, f, indent=2)
            
            # Generate QR code
            qr_code = self._generate_pairing_qr(pairing_info)
            
            # Start server in background
            self.server_running = True
            server_thread = threading.Thread(target=self._run_websocket_server, args=(port,))
            server_thread.daemon = True
            server_thread.start()
            
            return {
                'success': True,
                'message': f"📱 Mobile server started on port {port}",
                'data': {
                    'server_url': pairing_info['server_url'],
                    'pairing_code': pairing_info['pairing_code'],
                    'qr_code': qr_code,
                    'port': port
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to start mobile server: {str(e)}"
            }
    
    def _generate_pairing_qr(self, pairing_info: Dict) -> str:
        """Generate QR code for mobile app pairing."""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(pairing_info))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 string
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            return f"Error generating QR code: {str(e)}"
    
    def _run_websocket_server(self, port: int):
        """Run WebSocket server for mobile connections."""
        # Placeholder for WebSocket server implementation
        # In real implementation, would use websockets library
        print(f"📱 Mobile WebSocket server running on port {port}")
        while self.server_running:
            time.sleep(1)
    
    def register_mobile_device(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new mobile device."""
        try:
            device_id = device_info.get('device_id', str(uuid.uuid4()))
            device_name = device_info.get('device_name', 'Unknown Device')
            platform = device_info.get('platform', 'unknown')
            app_version = device_info.get('app_version', '1.0.0')
            
            # Create device object
            device = MobileDevice(
                device_id=device_id,
                device_name=device_name,
                platform=platform,
                app_version=app_version,
                last_seen=datetime.now()
            )
            
            # Save to database
            conn = sqlite3.connect(self.devices_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO mobile_devices 
                (device_id, device_name, platform, app_version, last_seen, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (device_id, device_name, platform, app_version, 
                  device.last_seen.isoformat(), True))
            
            conn.commit()
            conn.close()
            
            # Add to active connections
            self.connected_devices[device_id] = device
            
            return {
                'success': True,
                'message': f"📱 Device '{device_name}' registered successfully",
                'data': {
                    'device_id': device_id,
                    'device_name': device_name,
                    'platform': platform
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to register device: {str(e)}"
            }
    
    def get_connected_devices(self) -> Dict[str, Any]:
        """Get list of connected mobile devices."""
        try:
            conn = sqlite3.connect(self.devices_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT device_id, device_name, platform, app_version, last_seen, is_active
                FROM mobile_devices
                WHERE is_active = TRUE
                ORDER BY last_seen DESC
            ''')
            
            devices = []
            for row in cursor.fetchall():
                devices.append({
                    'device_id': row[0],
                    'device_name': row[1],
                    'platform': row[2],
                    'app_version': row[3],
                    'last_seen': row[4],
                    'is_active': bool(row[5])
                })
            
            conn.close()
            
            return {
                'success': True,
                'message': f"📱 Found {len(devices)} connected devices",
                'data': {
                    'devices': devices,
                    'total_count': len(devices),
                    'active_connections': len(self.connected_devices)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error getting devices: {str(e)}"
            }
    
    def sync_command_to_mobile(self, command: str, response: str, device_id: str = None) -> Dict[str, Any]:
        """Sync command and response to mobile devices."""
        try:
            sync_data = {
                'type': 'command_sync',
                'command': command,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'sync_id': str(uuid.uuid4())
            }
            
            if device_id:
                # Sync to specific device
                result = self._send_to_device(device_id, sync_data)
                return result
            else:
                # Sync to all connected devices
                synced_count = 0
                for dev_id in self.connected_devices:
                    result = self._send_to_device(dev_id, sync_data)
                    if result.get('success'):
                        synced_count += 1
                
                return {
                    'success': True,
                    'message': f"📱 Synced to {synced_count} devices",
                    'data': {'synced_count': synced_count}
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Sync error: {str(e)}"
            }
    
    def _send_to_device(self, device_id: str, data: Dict) -> Dict[str, Any]:
        """Send data to specific mobile device."""
        try:
            # In real implementation, would send via WebSocket
            # For now, queue for when device connects
            self._queue_sync_event(device_id, data)
            
            return {
                'success': True,
                'message': f"Data queued for device {device_id}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to send to device: {str(e)}"
            }
    
    def _queue_sync_event(self, device_id: str, data: Dict):
        """Queue sync event for offline device."""
        conn = sqlite3.connect(self.devices_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_events (device_id, event_type, event_data, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (device_id, data.get('type', 'sync'), json.dumps(data), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def handle_mobile_command(self, command: str, device_info: Dict) -> Dict[str, Any]:
        """Handle command from mobile device."""
        try:
            device_id = device_info.get('device_id')
            
            # Process the command (would integrate with main brain)
            response = {
                'success': True,
                'message': f"📱 Mobile command processed: {command}",
                'data': {
                    'command': command,
                    'device_id': device_id,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Mobile command error: {str(e)}"
            }

class LocationManager:
    """Manages location-based features and automation."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.location_rules = data_dir / "location_rules.json"
        self._init_location_rules()
    
    def _init_location_rules(self):
        """Initialize location-based automation rules."""
        default_rules = {
            'home': {
                'coordinates': {'lat': 0.0, 'lng': 0.0, 'radius': 100},
                'triggers': [
                    {'event': 'arrive_home', 'actions': ['turn_on_lights', 'set_comfortable_temperature']},
                    {'event': 'leave_home', 'actions': ['arm_security', 'energy_save_mode']}
                ]
            },
            'work': {
                'coordinates': {'lat': 0.0, 'lng': 0.0, 'radius': 50},
                'triggers': [
                    {'event': 'arrive_work', 'actions': ['work_mode_on', 'check_calendar']},
                    {'event': 'leave_work', 'actions': ['work_mode_off', 'commute_suggestions']}
                ]
            }
        }
        
        if not self.location_rules.exists():
            with open(self.location_rules, 'w') as f:
                json.dump(default_rules, f, indent=2)
    
    def update_location(self, device_id: str, location: Dict[str, float]) -> Dict[str, Any]:
        """Update device location and trigger automations."""
        try:
            # Process location-based triggers
            triggered_actions = self._check_location_triggers(location)
            
            return {
                'success': True,
                'message': f"📍 Location updated for device {device_id}",
                'data': {
                    'location': location,
                    'triggered_actions': triggered_actions
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Location update error: {str(e)}"
            }
    
    def _check_location_triggers(self, location: Dict) -> List[str]:
        """Check if location triggers any automation rules."""
        # Placeholder for location-based automation logic
        return []

class PushNotificationManager:
    """Manages push notifications to mobile devices."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.notification_queue = data_dir / "notification_queue.json"
    
    def send_notification(self, device_id: str, title: str, message: str, data: Dict = None) -> Dict[str, Any]:
        """Send push notification to mobile device."""
        try:
            notification = {
                'device_id': device_id,
                'title': title,
                'message': message,
                'data': data or {},
                'timestamp': datetime.now().isoformat(),
                'id': str(uuid.uuid4())
            }
            
            # In real implementation, would use FCM/APNs
            # For now, queue the notification
            self._queue_notification(notification)
            
            return {
                'success': True,
                'message': f"📱 Notification sent to {device_id}",
                'data': notification
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Notification error: {str(e)}"
            }
    
    def _queue_notification(self, notification: Dict):
        """Queue notification for delivery."""
        try:
            queue = []
            if self.notification_queue.exists():
                with open(self.notification_queue, 'r') as f:
                    queue = json.load(f)
            
            queue.append(notification)
            
            with open(self.notification_queue, 'w') as f:
                json.dump(queue, f, indent=2)
                
        except Exception as e:
            print(f"Error queueing notification: {e}")

class RealTimeSyncManager:
    """Manages real-time synchronization between devices."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.sync_log = data_dir / "sync_log.json"
    
    def sync_user_data(self, device_id: str, data_type: str, data: Dict) -> Dict[str, Any]:
        """Sync user data between devices."""
        try:
            sync_event = {
                'device_id': device_id,
                'data_type': data_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'sync_id': str(uuid.uuid4())
            }
            
            # Log sync event
            self._log_sync_event(sync_event)
            
            return {
                'success': True,
                'message': f"📱 Data synced: {data_type}",
                'data': sync_event
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Sync error: {str(e)}"
            }
    
    def _log_sync_event(self, event: Dict):
        """Log synchronization event."""
        try:
            log = []
            if self.sync_log.exists():
                with open(self.sync_log, 'r') as f:
                    log = json.load(f)
            
            log.append(event)
            
            # Keep only last 1000 events
            if len(log) > 1000:
                log = log[-1000:]
            
            with open(self.sync_log, 'w') as f:
                json.dump(log, f, indent=2)
                
        except Exception as e:
            print(f"Error logging sync event: {e}")

class OfflineManager:
    """Manages offline functionality and sync-when-connected."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.offline_queue = data_dir / "offline_queue.json"
    
    def queue_offline_action(self, device_id: str, action: Dict) -> Dict[str, Any]:
        """Queue action for when device comes back online."""
        try:
            offline_action = {
                'device_id': device_id,
                'action': action,
                'queued_at': datetime.now().isoformat(),
                'id': str(uuid.uuid4())
            }
            
            self._add_to_offline_queue(offline_action)
            
            return {
                'success': True,
                'message': "Action queued for offline device",
                'data': offline_action
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Offline queue error: {str(e)}"
            }
    
    def _add_to_offline_queue(self, action: Dict):
        """Add action to offline queue."""
        try:
            queue = []
            if self.offline_queue.exists():
                with open(self.offline_queue, 'r') as f:
                    queue = json.load(f)
            
            queue.append(action)
            
            with open(self.offline_queue, 'w') as f:
                json.dump(queue, f, indent=2)
                
        except Exception as e:
            print(f"Error adding to offline queue: {e}")
    
    def process_offline_queue(self, device_id: str) -> Dict[str, Any]:
        """Process queued actions when device comes back online."""
        try:
            if not self.offline_queue.exists():
                return {'success': True, 'message': "No offline actions", 'data': {'processed': 0}}
            
            with open(self.offline_queue, 'r') as f:
                queue = json.load(f)
            
            device_actions = [action for action in queue if action['device_id'] == device_id]
            remaining_queue = [action for action in queue if action['device_id'] != device_id]
            
            # Process actions for this device
            processed_count = len(device_actions)
            
            # Update queue
            with open(self.offline_queue, 'w') as f:
                json.dump(remaining_queue, f, indent=2)
            
            return {
                'success': True,
                'message': f"Processed {processed_count} offline actions",
                'data': {
                    'processed': processed_count,
                    'actions': device_actions
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Offline processing error: {str(e)}"
            }
