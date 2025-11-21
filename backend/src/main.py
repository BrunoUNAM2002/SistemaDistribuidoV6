#!/usr/bin/env python3
"""
Entry point for console-based distributed medical emergency system.
No web server - pure terminal interface.
"""
import signal
import sys
import logging
import logging.handlers
import os
from rich.console import Console
from rich.panel import Panel

from app_factory import create_app
from bully import BullyNode
from console.auth import login
from console.menus import main_menu
from console.notifications import create_notification_monitor
from config import Config

console = Console()

class GracefulKiller:
    """Handle SIGINT and SIGTERM for graceful shutdown"""
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)

    def _exit_gracefully(self, signum, frame):
        console.print("\n[yellow]Cerrando sistema gracefully...[/yellow]")
        self.kill_now = True

def setup_logging(node_id):
    """Setup rotating file logger"""
    log_dir = '../logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = logging.Formatter(
        fmt='[%(asctime)s] [Node-%(node_id)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=f'{log_dir}/node_{node_id}.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)

    # Add node_id filter
    class NodeIdFilter(logging.Filter):
        def filter(self, record):
            record.node_id = node_id
            return True

    file_handler.addFilter(NodeIdFilter())
    root_logger.addHandler(file_handler)

    # Silence noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def main():
    """Main entry point"""
    # Create Flask app (no web server)
    app = create_app()
    node_id = app.config['NODE_ID']

    # Setup logging
    setup_logging(node_id)
    logger = logging.getLogger(__name__)

    console.print(Panel(
        f"[bold cyan]Sistema de Emergencias Médicas Distribuido[/bold cyan]\n"
        f"Nodo: [yellow]{node_id}[/yellow]",
        title="🏥 Inicializando",
        border_style="cyan"
    ))

    # Initialize Bully system
    console.print("[dim]Iniciando sistema Bully...[/dim]")
    logger.info("Initializing Bully node")

    # Get cluster configuration
    cluster_nodes = {}
    for nodo_info in Config.OTROS_NODOS:
        if nodo_info['id'] != node_id:
            cluster_nodes[nodo_info['id']] = {
                'tcp_port': nodo_info['tcp_port'],
                'udp_port': 6000 + nodo_info['id'] - 1,  # UDP ports: 6000-6003
                'host': 'localhost'
            }

    bully_manager = BullyNode(
        node_id=node_id,
        cluster_nodes=cluster_nodes,
        tcp_port=5555 + node_id - 1,
        udp_port=6000 + node_id - 1
    )
    bully_manager.start()
    logger.info(f"Bully system started on ports TCP:{5555 + node_id - 1}, UDP:{6000 + node_id - 1}")

    # Initialize notification monitor
    console.print("[dim]Iniciando monitor de notificaciones...[/dim]")
    notification_monitor = create_notification_monitor(app, bully_manager, check_interval=10)
    notification_monitor.start()
    logger.info("Notification monitor started")

    # Setup graceful shutdown
    killer = GracefulKiller()

    console.print("[green]✓[/green] Sistema iniciado\n")

    # Login loop
    try:
        while not killer.kill_now:
            user = login(app)

            if user is None:
                break

            # Run main menu (role-based)
            continue_session = True
            while continue_session and not killer.kill_now:
                continue_session = main_menu(app, bully_manager, user)

            if killer.kill_now:
                break

            console.print("\n[yellow]Sesión cerrada[/yellow]\n")

    finally:
        # Cleanup
        console.print("\n[dim]Deteniendo monitor de notificaciones...[/dim]")
        notification_monitor.stop()
        logger.info("Notification monitor stopped")

        console.print("[dim]Deteniendo sistema Bully...[/dim]")
        bully_manager.stop()
        logger.info("Bully system stopped")

        console.print("[green]✓ Sistema cerrado correctamente[/green]")

if __name__ == '__main__':
    main()
