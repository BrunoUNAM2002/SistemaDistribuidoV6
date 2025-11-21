"""
Bully Algorithm - Simplified Version

Implementación clásica del algoritmo Bully para elección de líder
en sistemas distribuidos.

Características:
- Elección por ID (mayor ID gana)
- Detección de fallos por heartbeat timeout
- Comunicación TCP (elecciones) + UDP (heartbeats)
- Sin Machine Learning, sin Byzantine tolerance, sin event sourcing

Autor: Claude (Sonnet 4.5)
Versión: 1.0 - Simplified
"""

from .bully_node import BullyNode, NodeState
from .communication import CommunicationManager, Message

__all__ = ['BullyNode', 'NodeState', 'CommunicationManager', 'Message']
__version__ = '1.0.0'
