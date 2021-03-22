from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.database import Mysql
from diagrams.programming.framework import Angular, Spring

with Diagram("Utopia Architecture", show=False):

    with Cluster("Frontend"):
        userFrontend = Angular("user-frontend")
        adminFrontend = Angular("admin-frontend")
    with Cluster("Backend"):
        with Cluster("Micro Services"):
            microServices = [
                Spring("user-auth-service"),
                Spring("flight-plane-service"),
                Spring("ticket-payment-service"),
            ]
        orchestrator = Spring("orchestrator")
        discoveryService = Spring("discovery-service")
        db = Mysql("database")

    userFrontend >> Edge() << orchestrator
    adminFrontend >> Edge() << orchestrator
    orchestrator >> Edge() << microServices
    microServices >> Edge(color="blue", style="dashed") << db
    discoveryService >> Edge(color="red", style="dashed") << orchestrator
    discoveryService >> Edge(color="red", style="dashed") << microServices
