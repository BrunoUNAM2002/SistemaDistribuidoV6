"""
Background notification monitor for real-time updates.
Runs in separate thread to monitor database changes and cluster events.
"""
import threading
import time
import logging
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from models import VisitaEmergencia, Doctor, Cama

console = Console()
logger = logging.getLogger(__name__)


class NotificationMonitor:
    """
    Background thread that monitors system events and displays notifications.

    Monitors:
    - New emergency visits created
    - Visits completed/closed
    - Bully leader changes
    - Resource availability changes (doctors, beds)
    """

    def __init__(self, app, bully_manager, check_interval=10):
        """
        Initialize notification monitor.

        Args:
            app: Flask application instance
            bully_manager: BullyNode instance for cluster monitoring
            check_interval: Seconds between checks (default 10)
        """
        self.app = app
        self.bully_manager = bully_manager
        self.check_interval = check_interval

        # Threading control
        self._stop_event = threading.Event()
        self._thread = None

        # State tracking
        self._last_visit_count = 0
        self._last_completed_count = 0
        self._last_leader_id = None
        self._last_doctors_available = 0
        self._last_beds_available = 0
        self._last_check_time = None

        # Notification queue (for future use)
        self._notifications = []

        logger.info("NotificationMonitor initialized")

    def start(self):
        """Start background monitoring thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("NotificationMonitor already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="NotificationMonitor",
            daemon=True
        )
        self._thread.start()
        logger.info("NotificationMonitor thread started")

    def stop(self):
        """Stop monitoring thread gracefully."""
        if self._thread is None:
            return

        logger.info("Stopping NotificationMonitor...")
        self._stop_event.set()
        self._thread.join(timeout=5)

        if self._thread.is_alive():
            logger.warning("NotificationMonitor thread did not stop gracefully")
        else:
            logger.info("NotificationMonitor stopped")

    def is_running(self):
        """Check if monitor is running."""
        return self._thread is not None and self._thread.is_alive()

    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)."""
        logger.info("NotificationMonitor loop started")

        # Initialize state on first run
        self._initialize_state()

        while not self._stop_event.is_set():
            try:
                # Check for changes
                self._check_visits()
                self._check_leader_changes()
                self._check_resources()

                # Update last check time
                self._last_check_time = datetime.utcnow()

            except Exception as e:
                logger.error(f"Error in notification monitor: {e}", exc_info=True)

            # Sleep with interruptible wait
            self._stop_event.wait(self.check_interval)

        logger.info("NotificationMonitor loop ended")

    def _initialize_state(self):
        """Initialize state tracking on first run."""
        try:
            with self.app.app_context():
                self._last_visit_count = VisitaEmergencia.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    estado='activa'
                ).count()

                self._last_completed_count = VisitaEmergencia.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    estado='completada'
                ).count()

                self._last_doctors_available = Doctor.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    disponible=True,
                    activo=True
                ).count()

                self._last_beds_available = Cama.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    ocupada=False
                ).count()

                self._last_leader_id = self.bully_manager.get_current_leader()
                self._last_check_time = datetime.utcnow()

                logger.info(
                    f"State initialized: visits={self._last_visit_count}, "
                    f"completed={self._last_completed_count}, "
                    f"leader={self._last_leader_id}"
                )

        except Exception as e:
            logger.error(f"Error initializing state: {e}", exc_info=True)

    def _check_visits(self):
        """Check for new or completed visits."""
        try:
            with self.app.app_context():
                # Check for new active visits
                current_active = VisitaEmergencia.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    estado='activa'
                ).count()

                if current_active > self._last_visit_count:
                    new_count = current_active - self._last_visit_count
                    self._show_notification(
                        f"[bold green]+{new_count} Nueva{'s' if new_count > 1 else ''} Visita{'s' if new_count > 1 else ''}[/bold green]",
                        f"Se {'han' if new_count > 1 else 'ha'} registrado {new_count} visita{'s' if new_count > 1 else ''} de emergencia",
                        "green"
                    )
                    self._last_visit_count = current_active

                # Check for completed visits (since last check)
                if self._last_check_time:
                    recently_completed = VisitaEmergencia.query.filter(
                        VisitaEmergencia.id_sala == self.app.config['NODE_ID'],
                        VisitaEmergencia.estado == 'completada',
                        VisitaEmergencia.fecha_cierre >= self._last_check_time
                    ).all()

                    if recently_completed:
                        for visita in recently_completed:
                            self._show_notification(
                                f"[bold blue]✓ Visita Completada[/bold blue]",
                                f"Folio: {visita.folio} - Paciente: {visita.paciente.nombre}",
                                "blue"
                            )

        except Exception as e:
            logger.error(f"Error checking visits: {e}", exc_info=True)

    def _check_leader_changes(self):
        """Check for Bully leader changes."""
        try:
            current_leader = self.bully_manager.get_current_leader()

            if self._last_leader_id is not None and current_leader != self._last_leader_id:
                # Leader changed!
                is_new_leader = (current_leader == self.app.config['NODE_ID'])

                if is_new_leader:
                    self._show_notification(
                        "[bold yellow]👑 NUEVO LÍDER DEL CLUSTER[/bold yellow]",
                        f"Este nodo (Nodo {current_leader}) es ahora el líder del cluster",
                        "yellow"
                    )
                else:
                    self._show_notification(
                        "[bold cyan]Cambio de Líder[/bold cyan]",
                        f"Nuevo líder: Nodo {current_leader}",
                        "cyan"
                    )

                self._last_leader_id = current_leader

        except Exception as e:
            logger.error(f"Error checking leader: {e}", exc_info=True)

    def _check_resources(self):
        """Check for significant resource availability changes."""
        try:
            with self.app.app_context():
                # Check doctors availability
                current_doctors = Doctor.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    disponible=True,
                    activo=True
                ).count()

                total_doctors = Doctor.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    activo=True
                ).count()

                # Notify if doctors become critically low (<=1)
                if current_doctors <= 1 and self._last_doctors_available > 1:
                    self._show_notification(
                        "[bold red]⚠ Doctores Limitados[/bold red]",
                        f"Solo {current_doctors} doctor{'es' if current_doctors != 1 else ''} "
                        f"disponible{'s' if current_doctors != 1 else ''} de {total_doctors}",
                        "red"
                    )

                # Notify if doctors become available again
                if current_doctors > 1 and self._last_doctors_available <= 1:
                    self._show_notification(
                        "[bold green]✓ Doctores Disponibles[/bold green]",
                        f"{current_doctors} doctores ahora disponibles",
                        "green"
                    )

                self._last_doctors_available = current_doctors

                # Check beds availability
                current_beds = Cama.query.filter_by(
                    id_sala=self.app.config['NODE_ID'],
                    ocupada=False
                ).count()

                total_beds = Cama.query.filter_by(
                    id_sala=self.app.config['NODE_ID']
                ).count()

                # Notify if beds become critically low (<=1)
                if current_beds <= 1 and self._last_beds_available > 1:
                    self._show_notification(
                        "[bold red]⚠ Camas Limitadas[/bold red]",
                        f"Solo {current_beds} cama{'s' if current_beds != 1 else ''} "
                        f"disponible{'s' if current_beds != 1 else ''} de {total_beds}",
                        "red"
                    )

                # Notify if beds become available
                if current_beds > 1 and self._last_beds_available <= 1:
                    self._show_notification(
                        "[bold green]✓ Camas Disponibles[/bold green]",
                        f"{current_beds} camas ahora disponibles",
                        "green"
                    )

                self._last_beds_available = current_beds

        except Exception as e:
            logger.error(f"Error checking resources: {e}", exc_info=True)

    def _show_notification(self, title, message, border_style="cyan"):
        """
        Display notification to console.

        Args:
            title: Notification title
            message: Notification message
            border_style: Border color
        """
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            notification_panel = Panel(
                f"{message}\n\n[dim]{timestamp}[/dim]",
                title=f"🔔 {title}",
                border_style=border_style,
                width=60
            )

            # Print with newline separation
            console.print("\n")
            console.print(notification_panel)
            console.print("\n")

            # Log notification
            logger.info(f"Notification: {title} - {message}")

        except Exception as e:
            logger.error(f"Error showing notification: {e}", exc_info=True)

    def get_status(self):
        """
        Get monitor status information.

        Returns:
            dict: Status information
        """
        return {
            'running': self.is_running(),
            'last_check': self._last_check_time.isoformat() if self._last_check_time else None,
            'active_visits': self._last_visit_count,
            'completed_visits': self._last_completed_count,
            'current_leader': self._last_leader_id,
            'doctors_available': self._last_doctors_available,
            'beds_available': self._last_beds_available
        }


def create_notification_monitor(app, bully_manager, check_interval=10):
    """
    Factory function to create and configure notification monitor.

    Args:
        app: Flask application
        bully_manager: BullyNode instance
        check_interval: Check interval in seconds

    Returns:
        NotificationMonitor: Configured monitor instance
    """
    monitor = NotificationMonitor(app, bully_manager, check_interval)
    return monitor
