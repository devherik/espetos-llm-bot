Multi-Agent AI Platform Application Structure

This document describes the proposed architecture for a scalable, resilient, and observable multi-agent AI platform. It will serve as a fundamental guide for AI coding partners, ensuring a clear understanding of the project's structure and underlying principles.
1. Foundational Architecture: A Scalable Design

The platform is conceived as a distributed system based on microservices, adopting a hybrid architectural model of Orchestration and Choreography for service communication. This choice is not just a technical preference but a direct enabler of business scalability and agility.

    Orchestration for Core Workflows: The FastAPI Orchestrator service will manage primary, synchronous business logic. It will be responsible for transactional and stateful processes, such as input validation, selecting appropriate agents, dispatching tasks to a worker pool, and handling the final response. This offers centralized control and visibility for user-facing operations.

    Choreography for Decoupled System Events: For asynchronous and non-core operations, the system will utilize event-driven choreography. Upon the completion of a key step, the orchestrator will publish an event to a message bus (e.g., AgentTaskCompleted, KnowledgeBaseUpdated). Other services (like a log aggregator or performance monitoring service) can subscribe to these events and perform their functions independently, decoupling the orchestrator from auxiliary concerns.

This hybrid model mitigates the risks inherent in each pure pattern, resulting in a system that is both manageable and highly scalable. New agents can be developed and deployed as independent services, and new communication capabilities (like Slack or email) can be added without impacting the core agent logic.
2. The Orchestrator: The System Core with FastAPI

The Orchestrator is the central hub of the AI platform, acting as the main API gateway, agent workflow manager, and interface for all external interactions. Built with FastAPI, it must be designed for scalability, maintainability, and resilience. FastAPI offers automatic OpenAPI and JSON Schema generation, making it developer-friendly and easy to document APIs.
2.1 Scalable Project Structure

For applications of significant complexity, consolidating all logic into a single main.py file is unsustainable. FastAPI provides the APIRouter class, which allows for the logical separation of endpoints into modular, self-contained files. The recommended project structure for the FastAPI Orchestrator is organized by business domain or capability, a pillar of Domain-Driven Design, which reduces the cognitive load on developers and more clearly reflects the system's purpose.

The structure is as follows:

/app
├── main.py             # FastAPI application instantiation and router inclusion
├── __init__.py         # Makes 'app' a Python package
│
├── core/
│   ├── __init__.py
│   ├── config.py       # Pydantic settings for environment variables
│   └── security.py     # JWT token logic, password hashing, OAuth2 schemes
│
├── routers/
│   ├── __init__.py
│   ├── agents.py       # Endpoints for /agents (e.g., trigger task, get status)
│   ├── knowledge.py    # Endpoints for /knowledge (e.g., upload doc, manage collections)
│   └── webhooks.py     # Endpoint for receiving incoming messages (e.g., from WhatsApp)
│
├── services/
│   ├── __init__.py
│   ├── agent_service.py # Business logic for enqueuing tasks with Celery
│   └── notification_service.py # Logic for using the response sender adapters
│
├── schemas/
│   ├── __init__.py
│   └── agent.py        # Pydantic models for API request/response validation
│
└── utils/
    ├── __init__.py
    └── custom_exceptions.py # Custom exception handlers

In main.py, the primary function is to create the FastAPI instance and include the routers defined in the routers/ directory. Each file in routers/, such as agents.py, will define an APIRouter instance and attach all related path operations to it. This router can be configured with a specific prefix (e.g., /agents), tags for documentation, and router-level dependencies for authentication. HTTP methods like GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH, and TRACE are supported for path operations.
2.2 Infrastructure for the Orchestrator and Agent Workers

To manage long-running, asynchronous tasks initiated by the orchestrator, the platform will utilize Celery and Redis.

    Celery: Will act as the task queue system for asynchronous processing.

    Redis: Will serve as the message broker for Celery and the result backend for storing the results of completed tasks.

The deployment of all services will be done as containers on a Managed Kubernetes platform (EKS, AKS, or GKE) for robust scalability and management.
3. Agno Agents and ChromaDB Knowledge Bases

The core intelligence of the platform resides in the Agno agents and ChromaDB knowledge bases.
3.1 Deploying Agno Agents as Scalable Workers

The Agno framework is designed for high performance and efficiency; agents are lightweight (approximately 3 microseconds for instantiation and an average memory footprint of 6.5 KiB). This makes them ideal for deployment as containerized worker processes that can be scaled horizontally.

The recommended deployment strategy is to package each distinct agent type (e.g., "FinanceAgent" or "ResearchAgent") into its own dedicated Docker image. These agent containers will be managed as part of the Celery worker pool, orchestrated by Kubernetes. This provides a powerful and flexible execution environment, allowing for:

    Dependency Isolation: Each agent container has its own isolated environment.

    Heterogeneous Scalability: Different types of agents can be scaled independently, with Kubernetes adjusting the number of worker pods based on demand.

    Specialized Hardware Allocation: Allows for routing tasks to Kubernetes nodes with specialized hardware (like GPUs for multimodal agents).

Agno is a full-stack framework for building Multi-Agent Systems with memory, knowledge, and reasoning. It is model-agnostic, with support for over 23 LLM providers, and offers native support for multimodal inputs/outputs (text, image, audio, video). Agno allows for the creation of five levels of Agentic Systems, from agents with tools and instructions to stateful and deterministic agentic workflows.
3.2 Production-Ready ChromaDB Deployment

For a distributed, production-grade microservices architecture, ChromaDB's client-server mode is the only viable option. In this configuration, ChromaDB runs as a standalone server process, and all other services (FastAPI Orchestrator and Agno Agent Workers) connect to it as clients over the network.
3.3 Best Practices for Managing Multiple Knowledge Bases in ChromaDB

Supporting multiple, distinct knowledge bases is a multi-tenancy challenge that ChromaDB's data model, organized into collections and supporting rich metadata, can effectively address.

The recommended strategy involves a two-tiered approach for data isolation and access control:

    Collections for Coarse-Grained Isolation: Each logically separate knowledge base should be implemented as a distinct ChromaDB collection. The collection is the fundamental unit of storage and querying in Chroma. The Agno agent can be configured at initialization to connect to a specific collection, thereby restricting its knowledge scope.

    Metadata for Fine-Grained Filtering: Within a single collection, metadata provides a powerful mechanism for further categorization and filtering. Each document added to a collection can be associated with a dictionary of key-value pairs. This allows for more refined access control and retrieval, ensuring the agent retrieves only documents relevant to its current task and for which it has the appropriate authorization.

This combination enables the robust management of numerous knowledge bases, ensuring that each agent accesses only the necessary information.
4. Unifying Communication Channels: The Response Sender Service

To enable communication with users across various channels (starting with the official WhatsApp API and designed for future expansion), a flexible and extensible system for sending responses is crucial.

The recommended solution is to employ the Adapter Design Pattern. This structural pattern acts as a bridge between two incompatible interfaces, allowing them to work together. The implementation involves three key components:

    Target Interface: A standardized, internal interface that the rest of the application will use (e.g., an abstract base class NotificationSender with a send(recipient_id: str, message_content: dict) method).

    Adaptee: The third-party library or client for the external service (e.g., a WhatsApp API client), which has the incompatible interface to be adapted.

    Adapter: A concrete class that implements the NotificationSender target interface and internally wraps an instance of the Adaptee. The adapter's send method is responsible for translating the standardized input into the specific format and API calls required by the external service.

For example, a WhatsAppAdapter would format the generic message_content into the JSON structure required by the WhatsApp Cloud API. This pattern decouples the core business logic from the specific delivery mechanisms. Adding support for a new channel becomes a simple matter of creating a new adapter class, with no changes needed to the existing orchestration logic, perfectly adhering to the Open/Closed Principle.
4.2 Integration with the WhatsApp Official Cloud API

The WhatsApp Business Platform, accessed via the Cloud API hosted by Meta, requires a structured setup process. The developer guide includes:

    Initial Setup: Creating a Meta Developer Account, a Business App with the "WhatsApp" product, and linking it to a Meta Business Portfolio. This automatically provisions a test WhatsApp Business Account (WABA), a test phone number, and a pre-approved "hello_world" message template.

    Authentication: The API uses Bearer token authentication. For development and testing, a temporary User Access Token can be generated. For production, a long-lived System User Access Token is required, with whatsapp_business_management and whatsapp_business_messaging permissions. Tokens must be stored securely.

    Sending Messages: All messages are sent via POST requests to https://graph.facebook.com/{Version}/{Phone-Number-ID}/messages with a JSON body that specifies the recipient, message type, and content. For business-initiated conversations or replies after 24 hours, using pre-approved message templates is mandatory.

    Receiving Messages with Webhooks: The primary mechanism for receiving user messages is via webhooks. A public HTTPS endpoint on the FastAPI Orchestrator (e.g., /webhooks/whatsapp) must be configured and subscribed to message notifications in the Meta App Dashboard. The FastAPI endpoint is responsible for parsing the incoming JSON payload and initiating the appropriate agent workflow.

5. System-Wide Production Best Practices

Transitioning the platform from a prototype to a production service requires a deliberate focus on non-functional requirements such as security, observability, and monitoring.
5.1 Comprehensive Security Strategy

Security must be integrated into every layer of the application.

    Authentication and Authorization: The API will be secured with OAuth2 and JWTs. FastAPI provides tools to implement this, including OAuth2PasswordBearer.

    Secrets Management: Sensitive credentials (LLM API keys, JWT secret key, database connection strings, WhatsApp API tokens) must be managed using a dedicated secrets management service (e.g., AWS Secrets Manager, Azure Key Vault, Google Cloud Secret Manager, HashiCorp Vault).

5.2 Comprehensive Observability

Observability is a fundamental component of the architecture.

    Structured Logging with Correlation IDs: In a microservices environment, requests traverse multiple services. Structured logging, where log entries are written in a machine-readable format like JSON, is essential for efficient debugging and analysis. A unique Correlation ID should be injected into each request and propagated through all services to trace the journey of a single request. Libraries like structlog are recommended for implementing structured logging in FastAPI.

    Metrics with Prometheus and Grafana: The FastAPI Orchestrator will expose a /metrics endpoint, which is scraped by a Prometheus server. Grafana serves as the unified visualization layer for Prometheus metrics, allowing for real-time monitoring of system performance and health.

    Distributed Tracing with OpenTelemetry: All services (FastAPI, Celery Workers) will be instrumented with OpenTelemetry, sending tracing data to a tracing backend (e.g., Tempo). OpenTelemetry simplifies the collection of traces for applications, helping to monitor performance and diagnose problems in distributed systems. Integration with Agno allows for automatic tracing of agent and tool calls, offering a comprehensive view of agent behavior.

6. Software Architecture Principles Applied to AI Systems

Robust software architecture principles, such as Clean Architecture and SOLID, are crucial for AI systems as they ensure maintainability, scalability, and adaptability.
6.1 Clean Architecture

Clean Architecture protects high-level, stable business logic from low-level, volatile implementation details. In a RAG system, this translates into layers:

    Entities / Core: Business rules and core data structures, independent of frameworks.

    Use Cases (Application Layer): Orchestrates the application logic, defining the sequence of operations through abstract interfaces.

    Interface Adapters: Converts data between formats for Use Cases and for external agencies (UI, database).

    Infrastructure (Outer Layer): Contains volatile details like specific implementations of vector databases (ChromaDB, Pinecone), LLM clients (OpenAI, Groq), etc.

6.2 SOLID Principles for AI Development

The SOLID principles provide guidelines for writing maintainable and scalable object-oriented code:

    S - Single Responsibility Principle (SRP): Each class or module should have only one reason to change. (e.g., a DataLoader only loads documents, a TextChunker only does chunking).

    O - Open/Closed Principle (OCP): Software entities should be open for extension but closed for modification. (e.g., adding a new vector database or LLM without changing the core use case logic).

    L - Liskov Substitution Principle (LSP): Subtypes must be substitutable for their base types. (e.g., any implementation of IKnowledgeRepository should work without breaking the program).

    I - Interface Segregation Principle (ISP): Clients should not be forced to depend on methods they do not use. (e.g., smaller, more specific interfaces like IGenerative, IRetrievable).

    D - Dependency Inversion Principle (DIP): High-level modules should not depend on low-level modules; both should depend on abstractions. This is the pillar that enables the other principles.

Applying these principles is a crucial risk mitigation strategy, as the components of the AI stack are volatile. By interacting with volatile details through stable, abstract interfaces, Clean Architecture and the SOLID principles "future-proof" an AI application.
7. AI-Augmented Development

AI can act as a programming partner, assisting in code generation, refactoring, and testing. Instead of generic requests, prompts that explicitly invoke design principles (e.g., "Refactor this class to adhere to the Single Responsibility Principle") can guide the AI's output to ensure architectural quality. This transforms AI from a simple code generator into a powerful engine for architectural application and standardization.