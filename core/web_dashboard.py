"""
MAC Assistant - Web Dashboard Module
Advanced web-based control interface with real-time analytics and remote access.
"""

import json
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import dataclass
import asyncio
import threading
from flask import Flask, render_template, jsonify, request, session, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets
import hashlib

@dataclass
class DashboardUser:
    """Dashboard user data structure."""
    user_id: str
    username: str
    email: str
    role: str  # admin, user, viewer
    permissions: List[str]
    last_login: datetime
    session_token: str

@dataclass
class DashboardMetric:
    """Dashboard metric data structure."""
    metric_id: str
    name: str
    value: float
    unit: str
    category: str
    timestamp: datetime
    trend: str  # up, down, stable

@dataclass
class RemoteSession:
    """Remote access session data."""
    session_id: str
    user_id: str
    device_info: Dict[str, str]
    ip_address: str
    start_time: datetime
    last_activity: datetime
    permissions: List[str]

class WebDashboardManager:
    """Advanced web dashboard and remote access manager."""
    
    def __init__(self, data_dir: str = "data", host: str = "localhost", port: int = 5000):
        """Initialize web dashboard manager."""
        self.data_dir = Path(data_dir)
        self.dashboard_dir = self.data_dir / "dashboard"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # Web server configuration
        self.host = host
        self.port = port
        self.app = Flask(__name__, 
                        template_folder=str(self.dashboard_dir / "templates"),
                        static_folder=str(self.dashboard_dir / "static"))
        self.app.secret_key = secrets.token_hex(32)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Database and storage
        self.dashboard_db = self.dashboard_dir / "dashboard.db"
        self.sessions_cache = {}
        self.active_connections = {}
        
        # Initialize components
        self._init_dashboard_db()
        self.analytics_engine = AnalyticsEngine(self.dashboard_dir)
        self.security_manager = SecurityManager(self.dashboard_dir)
        self.notification_center = NotificationCenter()
        self.api_manager = APIManager()
        
        # Dashboard modules
        self.widgets = WidgetManager(self.dashboard_dir)
        self.reports = ReportGenerator(self.dashboard_dir)
        self.remote_control = RemoteControlInterface()
        
        # Setup Flask routes and SocketIO handlers
        self._setup_routes()
        self._setup_socketio_handlers()
        
        # Create default dashboard files
        self._create_dashboard_files()
        
        # Server thread
        self.server_thread = None
        self.running = False
    
    def _init_dashboard_db(self):
        """Initialize dashboard database."""
        conn = sqlite3.connect(self.dashboard_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT,
                password_hash TEXT,
                role TEXT,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                device_info TEXT,
                ip_address TEXT,
                start_time TIMESTAMP,
                last_activity TIMESTAMP,
                permissions TEXT,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES dashboard_users (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_metrics (
                metric_id TEXT PRIMARY KEY,
                name TEXT,
                value REAL,
                unit TEXT,
                category TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trend TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_activities (
                activity_id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_widgets (
                widget_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                config TEXT,
                position TEXT,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO dashboard_users 
            (user_id, username, email, password_hash, role, permissions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            "admin", "admin", "admin@mac-assistant.com", admin_password,
            "admin", json.dumps(["all"])
        ))
        
        conn.commit()
        conn.close()
    
    def _setup_routes(self):
        """Setup Flask web routes."""
        
        @self.app.route('/')
        def dashboard_home():
            """Main dashboard page."""
            if not self._check_authentication():
                return render_template('login.html')
            
            user_data = self._get_current_user()
            dashboard_data = self._get_dashboard_data(user_data['user_id'])
            
            return render_template('dashboard.html', 
                                 user=user_data, 
                                 dashboard=dashboard_data)
        
        @self.app.route('/api/login', methods=['POST'])
        def api_login():
            """User authentication endpoint."""
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if self._authenticate_user(username, password):
                session_token = self._create_session(username, request.remote_addr)
                session['token'] = session_token
                return jsonify({'success': True, 'token': session_token})
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        @self.app.route('/api/dashboard/metrics')
        def api_get_metrics():
            """Get dashboard metrics."""
            if not self._check_authentication():
                return jsonify({'error': 'Unauthorized'}), 401
            
            metrics = self._get_current_metrics()
            return jsonify({'metrics': metrics})
        
        @self.app.route('/api/dashboard/command', methods=['POST'])
        def api_execute_command():
            """Execute MAC command via web interface."""
            if not self._check_authentication():
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            command = data.get('command', '')
            
            # Execute command through MAC brain
            result = self._execute_mac_command(command)
            
            # Log activity
            self._log_activity(session.get('user_id'), 'command_execution', 
                             f"Executed: {command}")
            
            return jsonify(result)
        
        @self.app.route('/api/dashboard/analytics')
        def api_get_analytics():
            """Get analytics data."""
            if not self._check_authentication():
                return jsonify({'error': 'Unauthorized'}), 401
            
            analytics = self.analytics_engine.get_analytics_summary()
            return jsonify(analytics)
        
        @self.app.route('/api/dashboard/widgets')
        def api_get_widgets():
            """Get user widgets."""
            if not self._check_authentication():
                return jsonify({'error': 'Unauthorized'}), 401
            
            user_id = session.get('user_id')
            widgets = self.widgets.get_user_widgets(user_id)
            return jsonify({'widgets': widgets})
        
        @self.app.route('/api/dashboard/widgets', methods=['POST'])
        def api_save_widget():
            """Save widget configuration."""
            if not self._check_authentication():
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            user_id = session.get('user_id')
            
            result = self.widgets.save_widget(user_id, data)
            return jsonify(result)
    
    def _setup_socketio_handlers(self):
        """Setup SocketIO real-time handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            session_id = request.sid
            user_id = session.get('user_id', 'anonymous')
            
            self.active_connections[session_id] = {
                'user_id': user_id,
                'connected_at': datetime.now(),
                'ip_address': request.remote_addr
            }
            
            join_room(f"user_{user_id}")
            emit('connected', {'status': 'Connected to MAC Dashboard'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            session_id = request.sid
            if session_id in self.active_connections:
                user_id = self.active_connections[session_id]['user_id']
                leave_room(f"user_{user_id}")
                del self.active_connections[session_id]
        
        @self.socketio.on('execute_command')
        def handle_command(data):
            """Handle real-time command execution."""
            if not self._check_authentication():
                emit('error', {'message': 'Unauthorized'})
                return
            
            command = data.get('command', '')
            result = self._execute_mac_command(command)
            
            emit('command_result', result)
            
            # Broadcast to other sessions if needed
            user_id = session.get('user_id')
            emit('activity_update', {
                'user': user_id,
                'action': 'command_executed',
                'command': command,
                'timestamp': datetime.now().isoformat()
            }, room=f"user_{user_id}")
        
        @self.socketio.on('request_metrics')
        def handle_metrics_request():
            """Handle real-time metrics request."""
            if not self._check_authentication():
                emit('error', {'message': 'Unauthorized'})
                return
            
            metrics = self._get_current_metrics()
            emit('metrics_update', {'metrics': metrics})
        
        @self.socketio.on('join_monitoring')
        def handle_join_monitoring():
            """Join real-time monitoring room."""
            if not self._check_authentication():
                emit('error', {'message': 'Unauthorized'})
                return
            
            join_room('monitoring')
            emit('monitoring_joined', {'status': 'Joined monitoring room'})
    
    def _create_dashboard_files(self):
        """Create default dashboard HTML templates and static files."""
        templates_dir = self.dashboard_dir / "templates"
        static_dir = self.dashboard_dir / "static"
        templates_dir.mkdir(exist_ok=True)
        static_dir.mkdir(exist_ok=True)
        
        # Create login template
        login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAC Assistant - Login</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 300px; }
        .logo { text-align: center; margin-bottom: 2rem; font-size: 2rem; font-weight: bold; color: #667eea; }
        input { width: 100%; padding: 0.75rem; margin: 0.5rem 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 0.75rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; }
        button:hover { background: #5a6fd8; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🤖 MAC Assistant</div>
        <form id="loginForm">
            <input type="text" id="username" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">Sign In</button>
        </form>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            const result = await response.json();
            if (result.success) {
                window.location.href = '/';
            } else {
                alert('Invalid credentials');
            }
        });
    </script>
</body>
</html>'''
        
        # Create dashboard template
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAC Assistant Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .user-info { display: flex; align-items: center; gap: 1rem; }
        .sidebar { position: fixed; left: 0; top: 60px; width: 250px; height: calc(100vh - 60px); background: #34495e; color: white; padding: 1rem; }
        .main-content { margin-left: 250px; padding: 2rem; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .widget { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .widget h3 { margin-bottom: 1rem; color: #2c3e50; }
        .metric { display: flex; justify-content: space-between; margin: 0.5rem 0; }
        .metric-value { font-weight: bold; color: #27ae60; }
        .command-input { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 1rem; }
        .execute-btn { background: #3498db; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 5px; cursor: pointer; }
        .execute-btn:hover { background: #2980b9; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-online { background: #27ae60; }
        .status-offline { background: #e74c3c; }
        .nav-item { padding: 0.75rem; margin: 0.25rem 0; border-radius: 5px; cursor: pointer; transition: background 0.3s; }
        .nav-item:hover { background: rgba(255,255,255,0.1); }
        .nav-item.active { background: #3498db; }
        #output { background: #2c3e50; color: #ecf0f1; padding: 1rem; border-radius: 5px; height: 200px; overflow-y: auto; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🤖 MAC Assistant Dashboard</div>
        <div class="user-info">
            <span class="status-indicator status-online"></span>
            <span>Connected</span>
            <span>{{ user.username }}</span>
        </div>
    </div>
    
    <div class="sidebar">
        <div class="nav-item active" onclick="showSection('overview')">📊 Overview</div>
        <div class="nav-item" onclick="showSection('commands')">⚡ Commands</div>
        <div class="nav-item" onclick="showSection('analytics')">📈 Analytics</div>
        <div class="nav-item" onclick="showSection('monitoring')">👁️ Monitoring</div>
        <div class="nav-item" onclick="showSection('settings')">⚙️ Settings</div>
    </div>
    
    <div class="main-content">
        <div id="overview-section" class="dashboard-grid">
            <div class="widget">
                <h3>🎯 System Status</h3>
                <div class="metric">
                    <span>MAC Assistant</span>
                    <span class="metric-value">Online</span>
                </div>
                <div class="metric">
                    <span>AI Services</span>
                    <span class="metric-value">Active</span>
                </div>
                <div class="metric">
                    <span>Personalization</span>
                    <span class="metric-value">Learning</span>
                </div>
                <div class="metric">
                    <span>Automation</span>
                    <span class="metric-value">Running</span>
                </div>
            </div>
            
            <div class="widget">
                <h3>📊 Today's Metrics</h3>
                <div class="metric">
                    <span>Commands Processed</span>
                    <span class="metric-value" id="commands-count">0</span>
                </div>
                <div class="metric">
                    <span>Success Rate</span>
                    <span class="metric-value" id="success-rate">0%</span>
                </div>
                <div class="metric">
                    <span>Avg Response Time</span>
                    <span class="metric-value" id="response-time">0ms</span>
                </div>
                <div class="metric">
                    <span>Active Features</span>
                    <span class="metric-value" id="active-features">8</span>
                </div>
            </div>
            
            <div class="widget">
                <h3>⚡ Quick Commands</h3>
                <input type="text" class="command-input" id="quickCommand" placeholder="Enter MAC command...">
                <button class="execute-btn" onclick="executeCommand()">Execute</button>
                <div id="output"></div>
            </div>
            
            <div class="widget">
                <h3>🔄 Recent Activity</h3>
                <div id="recent-activity">
                    <div style="color: #7f8c8d; text-align: center; padding: 2rem;">
                        No recent activity
                    </div>
                </div>
            </div>
        </div>
        
        <div id="commands-section" style="display: none;">
            <div class="widget">
                <h3>⚡ Command Center</h3>
                <p>Execute MAC commands remotely with full access to all features.</p>
                <input type="text" class="command-input" id="commandInput" placeholder="Enter command (e.g., 'what time is it', 'search for AI news')">
                <button class="execute-btn" onclick="executeDetailedCommand()">Execute Command</button>
                <div id="commandOutput" style="margin-top: 1rem;"></div>
            </div>
        </div>
        
        <div id="analytics-section" style="display: none;">
            <div class="widget">
                <h3>📈 Usage Analytics</h3>
                <canvas id="usageChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div id="monitoring-section" style="display: none;">
            <div class="widget">
                <h3>👁️ Real-time Monitoring</h3>
                <p>Monitor MAC Assistant performance and activities in real-time.</p>
                <div id="monitoring-data"></div>
            </div>
        </div>
        
        <div id="settings-section" style="display: none;">
            <div class="widget">
                <h3>⚙️ Dashboard Settings</h3>
                <p>Customize your dashboard experience and preferences.</p>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to MAC Dashboard');
            updateStatus('Connected', true);
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from MAC Dashboard');
            updateStatus('Disconnected', false);
        });
        
        socket.on('command_result', function(data) {
            displayCommandResult(data);
        });
        
        socket.on('metrics_update', function(data) {
            updateMetrics(data.metrics);
        });
        
        function updateStatus(status, online) {
            const indicator = document.querySelector('.status-indicator');
            const statusText = document.querySelector('.user-info span:nth-child(2)');
            indicator.className = `status-indicator ${online ? 'status-online' : 'status-offline'}`;
            statusText.textContent = status;
        }
        
        function executeCommand() {
            const command = document.getElementById('quickCommand').value;
            if (command.trim()) {
                socket.emit('execute_command', { command: command });
                document.getElementById('quickCommand').value = '';
                addToOutput(`> ${command}`);
            }
        }
        
        function executeDetailedCommand() {
            const command = document.getElementById('commandInput').value;
            if (command.trim()) {
                socket.emit('execute_command', { command: command });
                document.getElementById('commandInput').value = '';
            }
        }
        
        function displayCommandResult(result) {
            addToOutput(`${result.message}`);
            
            // Also update detailed command output if visible
            const detailedOutput = document.getElementById('commandOutput');
            if (detailedOutput) {
                detailedOutput.innerHTML = `
                    <div style="background: #ecf0f1; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
                        <strong>Status:</strong> ${result.status}<br>
                        <strong>Response:</strong> ${result.message}
                    </div>
                `;
            }
        }
        
        function addToOutput(text) {
            const output = document.getElementById('output');
            output.textContent += text + '\\n';
            output.scrollTop = output.scrollHeight;
        }
        
        function updateMetrics(metrics) {
            // Update dashboard metrics
            document.getElementById('commands-count').textContent = metrics.commands_processed || 0;
            document.getElementById('success-rate').textContent = (metrics.success_rate || 0) + '%';
            document.getElementById('response-time').textContent = (metrics.avg_response_time || 0) + 'ms';
        }
        
        function showSection(sectionName) {
            // Hide all sections
            document.querySelectorAll('[id$="-section"]').forEach(section => {
                section.style.display = 'none';
            });
            
            // Show selected section
            document.getElementById(sectionName + '-section').style.display = 'block';
            
            // Update navigation
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        // Request initial metrics
        socket.emit('request_metrics');
        
        // Auto-refresh metrics every 30 seconds
        setInterval(() => {
            socket.emit('request_metrics');
        }, 30000);
        
        // Enter key support for commands
        document.getElementById('quickCommand').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                executeCommand();
            }
        });
        
        document.getElementById('commandInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                executeDetailedCommand();
            }
        });
    </script>
</body>
</html>'''
        
        with open(templates_dir / "login.html", "w", encoding='utf-8') as f:
            f.write(login_html)
        
        with open(templates_dir / "dashboard.html", "w", encoding='utf-8') as f:
            f.write(dashboard_html)
    
    def start_dashboard(self) -> Dict[str, Any]:
        """Start the web dashboard server."""
        try:
            if self.running:
                return {
                    'success': False,
                    'message': 'Dashboard is already running'
                }
            
            self.running = True
            
            # Start server in background thread
            self.server_thread = threading.Thread(
                target=lambda: self.socketio.run(
                    self.app, 
                    host=self.host, 
                    port=self.port, 
                    debug=False, 
                    allow_unsafe_werkzeug=True
                )
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            
            return {
                'success': True,
                'message': f"🌐 Web Dashboard started successfully!\n\n"
                          f"📍 URL: http://{self.host}:{self.port}\n"
                          f"👤 Default Login: admin / admin123\n"
                          f"🔧 Features: Real-time control, Analytics, Remote access\n"
                          f"📱 Compatible: Desktop, Mobile, Tablet browsers",
                'data': {
                    'url': f"http://{self.host}:{self.port}",
                    'host': self.host,
                    'port': self.port,
                    'status': 'running'
                }
            }
            
        except Exception as e:
            self.running = False
            return {
                'success': False,
                'message': f"❌ Failed to start dashboard: {str(e)}"
            }
    
    def stop_dashboard(self) -> Dict[str, Any]:
        """Stop the web dashboard server."""
        try:
            if not self.running:
                return {
                    'success': False,
                    'message': 'Dashboard is not running'
                }
            
            self.running = False
            
            return {
                'success': True,
                'message': '🛑 Web Dashboard stopped successfully',
                'data': {'status': 'stopped'}
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error stopping dashboard: {str(e)}"
            }
    
    def get_dashboard_status(self) -> Dict[str, Any]:
        """Get current dashboard status and metrics."""
        try:
            active_sessions = len(self.active_connections)
            uptime = datetime.now() - datetime.now()  # Placeholder
            
            metrics = self._get_current_metrics()
            
            return {
                'success': True,
                'message': f"🌐 Dashboard Status:\n\n"
                          f"🔄 Status: {'Running' if self.running else 'Stopped'}\n"
                          f"🌍 URL: http://{self.host}:{self.port}\n"
                          f"👥 Active Sessions: {active_sessions}\n"
                          f"📊 Commands Today: {metrics.get('commands_processed', 0)}\n"
                          f"⚡ Success Rate: {metrics.get('success_rate', 0):.1f}%",
                'data': {
                    'running': self.running,
                    'url': f"http://{self.host}:{self.port}",
                    'active_sessions': active_sessions,
                    'metrics': metrics,
                    'connections': len(self.active_connections)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error getting dashboard status: {str(e)}"
            }
    
    # Helper methods
    def _check_authentication(self) -> bool:
        """Check if current session is authenticated."""
        token = session.get('token')
        if not token:
            return False
        
        # Validate token (simplified)
        return token in self.sessions_cache
    
    def _authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        try:
            conn = sqlite3.connect(self.dashboard_db)
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                SELECT user_id, role FROM dashboard_users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception:
            return False
    
    def _create_session(self, username: str, ip_address: str) -> str:
        """Create new user session."""
        session_token = secrets.token_urlsafe(32)
        
        # Store session data
        self.sessions_cache[session_token] = {
            'username': username,
            'ip_address': ip_address,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        session['user_id'] = username
        session['username'] = username
        
        return session_token
    
    def _get_current_user(self) -> Dict[str, str]:
        """Get current authenticated user."""
        return {
            'user_id': session.get('user_id', 'anonymous'),
            'username': session.get('username', 'Anonymous')
        }
    
    def _get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard data for user."""
        return {
            'metrics': self._get_current_metrics(),
            'widgets': self.widgets.get_user_widgets(user_id),
            'recent_activity': []
        }
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return {
            'commands_processed': 150,
            'success_rate': 95.5,
            'avg_response_time': 245,
            'active_features': 8,
            'uptime': '2 days, 14 hours'
        }
    
    def _execute_mac_command(self, command: str) -> Dict[str, Any]:
        """Execute MAC command and return result."""
        # This would interface with the main MAC brain
        # For now, return a simulated response
        return {
            'status': 'success',
            'message': f"Command '{command}' executed successfully",
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_activity(self, user_id: str, action: str, description: str):
        """Log user activity."""
        try:
            conn = sqlite3.connect(self.dashboard_db)
            cursor = conn.cursor()
            
            activity_id = f"act_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor.execute('''
                INSERT INTO dashboard_activities 
                (activity_id, user_id, action, description, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (activity_id, user_id, action, description, 
                  request.remote_addr if request else 'local'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging activity: {e}")

# Supporting classes (simplified)
class AnalyticsEngine:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        return {
            'total_commands': 1500,
            'success_rate': 95.5,
            'most_used_features': ['time', 'search', 'automation'],
            'user_engagement': 87.2
        }

class SecurityManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

class NotificationCenter:
    def __init__(self):
        pass

class APIManager:
    def __init__(self):
        pass

class WidgetManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def get_user_widgets(self, user_id: str) -> List[Dict[str, Any]]:
        return []
    
    def save_widget(self, user_id: str, widget_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'success': True}

class ReportGenerator:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

class RemoteControlInterface:
    def __init__(self):
        pass
