# System Architecture

![System Diagram]

Here's a brief explanation of how the system is designed:
- **Task Distribution (RabbitMQ)**: At the core of the system is RabbitMQ, which holds the pending tasks and handles task distribution. It ensures that tasks are queued reliably.
- **Worker Cluster (Horizontal Scaling)**: We have a cluster of Worker Nodes that fetch and process these tasks from RabbitMQ. This cluster is horizontally scaled, meaning we can add more nodes as the load increases.
- **Persistent Storage (SQL Database)**: Once the workers finish processing the tasks, they save the results directly into our SQL Database.
- **Results/Dashboard**: The results from the SQL database are then fed into the Results/Dashboard for end-user visibility.
- **Monitoring Stack**: To keep track of the system's health and performance, the worker nodes send logs and health metrics to our Monitoring Stack. This stack consists of Prometheus (acting as the Metrics Collector) and Grafana (for Visualization). The monitoring stack also feeds data to our Dashboard.
- **Failover Mechanism**: If a task fails or a worker node goes down, the system communicates with our Failover Mechanism (triggering a "Redeliver on Failure" action), which then communicates back to RabbitMQ to requeue or handle the failed tasks appropriately.

This setup ensures that our system can handle high throughput with auto-scaling workers, while maintaining strict monitoring and automatic failover capabilities!
