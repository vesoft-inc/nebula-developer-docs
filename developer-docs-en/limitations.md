# Capabilities and limits

Before deploying, check whether {{nebula.short_name}}'s fixed configuration meets your learning, development, or testing needs.

!!! note "Scope"

    This page describes the planned {{nebula.short_name}} boundaries. These docs are a preview. The supported scope must be confirmed for the released product version.

## Deployment limits

| Item | {{nebula.short_name}} scope | What this means for you |
| --- | --- | --- |
| Deployment | Docker Compose only | Use the Docker Compose file supplied for {{nebula.short_name}} |
| Hosts | One host; only one Host can be added | You cannot expand this instance by adding hosts |
| Service groups | One, pre-initialized | You do not need to create a service group |
| Meta services | One | Multiple Meta services are not supported |
| Data partitions | One | You cannot distribute data by adding partitions |
| Replicas | One; the count cannot be changed | You cannot add replicas for failover |
| Cluster synchronization | Not supported | You cannot configure cluster synchronization between instances |

The Meta service manages database metadata, such as graph definitions. A data partition is a logical unit for dividing graph data. A replica is a copy of the data. You do not need to change these settings to get started.

!!! warning "One host and one replica do not provide high availability"

    If the host or its storage fails, another replica cannot take over. Do not use {{nebula.short_name}} for workloads that require high availability.

## Product license file and sign-in

You do not need to request or configure a product license file. Database sign-in is separate from the product license file, so you still need a username and password to connect.

## Support details not yet confirmed

The following details are not established in this preview. Do not assume these features are unrestricted or available:

- **Multiple users and access permissions:** Data isolation between users is not promised.
- **Data capacity:** The limit, measurement method, and behavior at the limit have not been published. An unpublished limit does not mean unlimited capacity.
- **Clients and tools:** SDKs, connectors, visualization tools, and AI tools each need a verified compatible version.
- **Updates:** No verified upgrade or downgrade path is available yet.

{{nebula.short_name}} images support AMD64 (x86_64) and ARM64 processor architectures. The operating system and installation files must match the release. Check [Deploy with Docker Compose](get-started/deploy.md) before deploying.
