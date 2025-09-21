# services/scheduler.py
import logging

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self):
        self._running = False

    def start(self):
        """Inicia o agendador (mock)."""
        self._running = True
        logger.info("PostScheduler iniciado")

    def stop(self):
        """Para o agendador (mock)."""
        self._running = False
        logger.info("PostScheduler parado")

    def schedule_post(self, post_data, schedule_time):
        # Mock implementation
        return True
    
    def cancel_scheduled_post(self, post_id):
        # Mock implementation  
        return True
    
    def is_healthy(self):
        return True
