from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import random
import asyncio
from fastapi import HTTPException

@dataclass
class ServiceNode:
    host: str
    port: int
    healthy: bool = True
    last_health_check: datetime = datetime.now()
    active_connections: int = 0

class LoadBalancer:
    def __init__(self):
        self.nodes: List[ServiceNode] = []
        self.health_check_interval: int = 30  # seconds

    def add_node(self, host: str, port: int) -> None:
        """Add a new service node to the load balancer pool."""
        node = ServiceNode(host=host, port=port)
        self.nodes.append(node)

    def remove_node(self, host: str, port: int) -> None:
        """Remove a service node from the pool."""
        self.nodes = [n for n in self.nodes if not (n.host == host and n.port == port)]

    async def get_next_node(self) -> Optional[ServiceNode]:
        """Get the next available node using least connections algorithm."""
        healthy_nodes = [n for n in self.nodes if n.healthy]
        if not healthy_nodes:
            raise HTTPException(status_code=503, detail="No healthy nodes available")

        # Use least connections algorithm
        selected_node = min(healthy_nodes, key=lambda x: x.active_connections)
        selected_node.active_connections += 1
        return selected_node

    def release_node(self, node: ServiceNode) -> None:
        """Release a node after request completion."""
        if node.active_connections > 0:
            node.active_connections -= 1

    async def check_node_health(self, node: ServiceNode) -> bool:
        """Check if a node is healthy by attempting a connection."""
        try:
            # Implement actual health check logic here
            # For example, try to connect to the node's health check endpoint
            await asyncio.sleep(0.1)  # Simulated health check
            node.healthy = True
            node.last_health_check = datetime.now()
            return True
        except Exception:
            node.healthy = False
            return False

    async def health_check_loop(self) -> None:
        """Continuously check the health of all nodes."""
        while True:
            for node in self.nodes:
                await self.check_node_health(node)
            await asyncio.sleep(self.health_check_interval)

    def get_status(self) -> Dict:
        """Get the current status of all nodes."""
        return {
            "total_nodes": len(self.nodes),
            "healthy_nodes": len([n for n in self.nodes if n.healthy]),
            "nodes": [
                {
                    "host": n.host,
                    "port": n.port,
                    "healthy": n.healthy,
                    "active_connections": n.active_connections
                }
                for n in self.nodes
            ]
        }