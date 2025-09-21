# services/monitoring.py
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio
import aiohttp
from dataclasses import dataclass
from models.database import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict
    timestamp: datetime

@dataclass
class ServiceHealth:
    name: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    last_check: datetime
    error_message: str = None

class SystemMonitor:
    def __init__(self):
        self.db = DatabaseManager()
        self.metrics_history = []
        self.service_status = {}
        self.alerts = []
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 5.0  # seconds
        }
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return None
    
    async def check_service_health(self, service_name: str, endpoint: str) -> ServiceHealth:
        """Check health of a specific service"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, timeout=10) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        status = 'healthy'
                        if response_time > self.thresholds['response_time']:
                            status = 'degraded'
                    else:
                        status = 'unhealthy'
                    
                    return ServiceHealth(
                        name=service_name,
                        status=status,
                        response_time=response_time,
                        last_check=datetime.now(),
                        error_message=None if status != 'unhealthy' else f"HTTP {response.status}"
                    )
        
        except Exception as e:
            return ServiceHealth(
                name=service_name,
                status='unhealthy',
                response_time=time.time() - start_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def monitor_all_services(self):
        """Monitor all registered services"""
        services = {
            'main_app': 'http://localhost:5000/health',
            'ai_service': 'http://localhost:5000/api/health/ai',
            'video_processor': 'http://localhost:5000/api/health/video',
            'scheduler': 'http://localhost:5000/api/health/scheduler'
        }
        
        for service_name, endpoint in services.items():
            health = await self.check_service_health(service_name, endpoint)
            self.service_status[service_name] = health
            
            # Check if alert needed
            if health.status == 'unhealthy':
                self.create_alert(f"Service {service_name} is unhealthy", 'error')
            elif health.status == 'degraded':
                self.create_alert(f"Service {service_name} is degraded", 'warning')
    
    def check_system_alerts(self, metrics: SystemMetrics):
        """Check for system-level alerts"""
        if metrics.cpu_usage > self.thresholds['cpu_usage']:
            self.create_alert(f"High CPU usage: {metrics.cpu_usage:.1f}%", 'warning')
        
        if metrics.memory_usage > self.thresholds['memory_usage']:
            self.create_alert(f"High memory usage: {metrics.memory_usage:.1f}%", 'warning')
        
        if metrics.disk_usage > self.thresholds['disk_usage']:
            self.create_alert(f"High disk usage: {metrics.disk_usage:.1f}%", 'error')
    
    def create_alert(self, message: str, severity: str):
        """Create monitoring alert"""
        alert = {
            'id': f"alert_{int(time.time())}",
            'message': message,
            'severity': severity,
            'timestamp': datetime.now(),
            'resolved': False
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT [{severity}]: {message}")
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts.pop(0)
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        current_metrics = self.collect_system_metrics()
        
        return {
            'system_metrics': {
                'cpu_usage': current_metrics.cpu_usage if current_metrics else 0,
                'memory_usage': current_metrics.memory_usage if current_metrics else 0,
                'disk_usage': current_metrics.disk_usage if current_metrics else 0,
                'network_io': current_metrics.network_io if current_metrics else {}
            },
            'services': {name: {
                'status': health.status,
                'response_time': health.response_time,
                'last_check': health.last_check.isoformat(),
                'error_message': health.error_message
            } for name, health in self.service_status.items()},
            'recent_alerts': [
                {
                    'message': alert['message'],
                    'severity': alert['severity'],
                    'timestamp': alert['timestamp'].isoformat(),
                    'resolved': alert['resolved']
                } for alert in self.alerts[-10:]  # Last 10 alerts
            ],
            'uptime': self.get_uptime(),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_delta = timedelta(seconds=int(uptime_seconds))
            return str(uptime_delta)
        except:
            return "Unknown"