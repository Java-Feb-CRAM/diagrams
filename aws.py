from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import (
    EC2,
    ECR,
    EC2ContainerRegistryRegistry,
    EC2ElasticIpAddress,
    EC2Instance,
    ElasticContainerService,
    ElasticContainerServiceContainer,
    ElasticContainerServiceService,
    Fargate,
)
from diagrams.aws.database import Database, RDSInstance, RDSMysqlInstance
from diagrams.aws.management import Cloudformation, CloudformationTemplate, Cloudtrail, Cloudwatch
from diagrams.aws.network import VPC, CloudFront, ElbNetworkLoadBalancer, PrivateSubnet, PublicSubnet
from diagrams.aws.security import SecretsManager
from diagrams.aws.storage import SimpleStorageServiceS3Bucket
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.vcs import Github
from diagrams.programming.framework import Angular, Spring
from diagrams.programming.language import Bash, Java, TypeScript

with Diagram("AWS Architecture", show=False, direction="TB"):
    with Cluster("AWS"):
        elasticIpJenkins = EC2ElasticIpAddress("54.161.35.241")
        elasticIpSonar = EC2ElasticIpAddress("54.172.12.154")
        elasticIpDiscovery = EC2ElasticIpAddress("3.219.82.3")
        elasticIpOrchestrator = EC2ElasticIpAddress("54.243.106.97")
        ecrDiscovery = EC2ContainerRegistryRegistry("utopia-discovery-server")
        ecrFlightPlane = EC2ContainerRegistryRegistry("utopia-flight-plane")
        ecrOrchestrator = EC2ContainerRegistryRegistry("utopia-orchestrator")
        ecrTicketPayment = EC2ContainerRegistryRegistry("utopia-ticket-payment")
        ecrUserAuth = EC2ContainerRegistryRegistry("utopia-user-auth")
        ECR("ECR") - [
            ecrDiscovery,
            ecrFlightPlane,
            ecrOrchestrator,
            ecrTicketPayment,
            ecrUserAuth,
        ]
        ticketPaymentService = ElasticContainerServiceService("TicketPaymentMS")
        discoveryService = ElasticContainerServiceService("DiscoveryMS")
        orchestratorService = ElasticContainerServiceService("OrchestratorMS")
        flightPlaneService = ElasticContainerServiceService("FlightPlaneMS")
        ecrDiscovery - discoveryService
        ecrFlightPlane - flightPlaneService
        ecrOrchestrator - orchestratorService
        ecrTicketPayment - ticketPaymentService
        taskTicketPayment = ElasticContainerServiceContainer("TicketPayment Task")
        taskDiscovery = ElasticContainerServiceContainer("Discovery Task")
        taskOrchestrator = ElasticContainerServiceContainer("Orchestrator Task")
        taskFlightPlane = ElasticContainerServiceContainer("FlightPlane Task")
        springTicketPayment = Spring("Ticket/Payment MS")
        springDiscovery = Spring("Eureka Discovery Server")
        springOrchestrator = Spring("Orchestrator")
        springFlightPlane = Spring("Flight/Plane MS")
        elasticIpDiscovery - [springFlightPlane, springOrchestrator, springTicketPayment]
        taskTicketPayment - springTicketPayment
        taskDiscovery - springDiscovery
        taskOrchestrator - springOrchestrator
        taskFlightPlane - springFlightPlane
        ElasticContainerService("UtopiaCluster") - [
            ticketPaymentService,
            discoveryService,
            orchestratorService,
            flightPlaneService,
        ]
        ticketPaymentService - taskTicketPayment
        discoveryService - taskDiscovery
        orchestratorService - taskOrchestrator
        flightPlaneService - taskFlightPlane
        with Cluster("utopia VPC"):
            with Cluster("utopia_public Subnet"):
                discoveryLB = ElbNetworkLoadBalancer("Discovery-LB")
                discoveryLB - discoveryService
                ElbNetworkLoadBalancer("Misc-LB") - [flightPlaneService, ticketPaymentService]
                orchestratorLB = ElbNetworkLoadBalancer("Orchestrator-LB")
                orchestratorLB - orchestratorService
                ec2Jenkins = EC2Instance("Jenkins")
                jenkins = Jenkins("Jenkins")
                ec2Jenkins - jenkins
                ec2Sonar = EC2Instance("SonarQube")
            with Cluster("utopia_private Subnet"):
                RDSMysqlInstance("utopia-prod") - [springFlightPlane, springOrchestrator, springTicketPayment, jenkins]
        elasticIpJenkins - ec2Jenkins
        elasticIpSonar - ec2Sonar
        elasticIpDiscovery - discoveryLB
        elasticIpOrchestrator - orchestratorLB
        SecretsManager("Secrets Manager") - [
            taskDiscovery,
            taskFlightPlane,
            taskOrchestrator,
            taskTicketPayment,
            jenkins,
        ]
        jenkins - [ecrDiscovery, ecrFlightPlane, ecrOrchestrator, ecrTicketPayment, ecrUserAuth, ec2Sonar]
        s3admin = SimpleStorageServiceS3Bucket("ut-frontend-admin")
        s3user = SimpleStorageServiceS3Bucket("ut-frontend-user")
        CloudFront("ut-frontend-admin") - s3admin - Angular("Admin") - elasticIpOrchestrator
        CloudFront("ut-frontend-user") - s3user - Angular("User") - elasticIpOrchestrator
        jenkins - [s3admin, s3user]
        jenkins - Cloudformation("CloudFormation") - [
            CloudformationTemplate("UtopiaOrchestrator Stack") - orchestratorService,
            CloudformationTemplate("UtopiaDiscovery Stack") - discoveryService,
            CloudformationTemplate("UtopiaTicketPayment Stack") - ticketPaymentService,
            CloudformationTemplate("UtopiaFlightPlane Stack") - flightPlaneService,
        ]
        Cloudwatch("CloudWatch") - orchestratorService, discoveryService, ticketPaymentService, flightPlaneService
