# Redis Replication, Sentinel & Cluster

## 1. Overview

Redis provides replication and high-availability features to help applications remain available when servers fail and to support larger workloads.

This document covers three related concepts:

- **Replication:** Copies data from a primary Redis server to replica servers.
- **Sentinel:** Monitors Redis servers and coordinates automatic failover in a primary-and-replica deployment.
- **Redis Cluster:** Distributes data across multiple primary nodes and supports replica-based failover.

These concepts were studied theoretically as the final topic of the Redis Advanced Project roadmap. A multi-node replication, Sentinel, or Cluster deployment was not implemented in this project.

## 2. Why Do We Need High Availability?

Imagine a Django application that depends on a single Redis server for caching, sessions, or rate limiting.

If that server fails, Redis-backed operations may become unavailable until the service recovers.

### Problems without replication and failover

- A failed primary may interrupt application access to Redis.
- A single server may become a capacity bottleneck.
- Recovery may require manual intervention.
- A large dataset may exceed the practical capacity of one primary.
- An application may experience downtime while the Redis service is restored.

Replication, Sentinel, and Cluster address different parts of these problems.

## 3. Redis Replication

### What is replication?

Redis replication copies data from a primary server to one or more replica servers.

The primary normally handles writes, while replicas maintain copies of the primary's dataset and can serve reads when the application architecture permits it.

### How replication works

1. The application sends a write command to the primary.
2. The primary executes the command.
3. The primary propagates data changes to its replicas.
4. The replicas apply those changes and update their copies.
5. If the primary fails, an eligible replica may be promoted by a configured failover mechanism.

```text
             Application
                  |
                  v
           Primary Redis
             /       \
            v         v
       Replica A   Replica B
```

### Important concepts

| Concept | Meaning |
|---|---|
| Primary | The server normally responsible for writes |
| Replica | A server maintaining a copy of the primary's data |
| Replication lag | The delay before a replica receives and applies updates |
| Failover | The process of promoting a replica when the primary fails |
| Read scaling | Directing suitable read requests to replicas |

Redis replication is asynchronous by default. A replica can temporarily return older data, and recent writes may be missing if the primary fails before those writes reach the promoted replica.

### Important commands

| Command | Purpose |
|---|---|
| `INFO replication` | Displays replication status and role information |
| `ROLE` | Shows the server's current role |
| `REPLICAOF host port` | Configures a server to replicate from the specified primary |
| `REPLICAOF NO ONE` | Configures a replica to stop replicating and become a primary |

These commands are documented for learning purposes; they were not used to deploy a multi-node replication environment in this project.

## 4. Redis Sentinel

### What is Sentinel?

Redis Sentinel is a monitoring and failover system for Redis deployments that use a primary and replicas.

Sentinel monitors server availability, coordinates failure detection, helps select a replica for promotion, and allows clients to discover the current primary.

### What problem does Sentinel solve?

Replication creates copies of data, but replication alone does not automatically decide which replica should become the primary after a failure.

Sentinel helps automate this recovery process.

### Sentinel execution flow

1. Sentinels monitor the primary and replicas.
2. A Sentinel detects that the primary is not responding.
3. Sentinel instances coordinate to determine whether the primary is objectively down.
4. If the necessary quorum and failover conditions are satisfied, a Sentinel coordinates failover.
5. An eligible replica is promoted to primary.
6. Other replicas are reconfigured to replicate from the new primary.
7. The application discovers the new primary and reconnects.

```text
           Sentinel Instances
           /       |       \
          v        v        v
       Monitor Redis servers
                  |
                  v
          Primary failure
                  |
                  v
        Failure confirmation
                  |
                  v
        Promote an eligible replica
                  |
                  v
         Application reconnects
```

### Important Sentinel concepts

| Concept | Meaning |
|---|---|
| Monitoring | Checking the availability of Redis servers |
| Subjectively down (SDOWN) | A Sentinel considers a server unavailable based on its own observations |
| Objectively down (ODOWN) | The required quorum agrees that the primary is unavailable |
| Quorum | The configured number of Sentinel votes needed to establish objective failure |
| Leader election | Selects a Sentinel to coordinate the failover |
| Failover | Promotes a replica and updates the replication configuration |
| Discovery | Allows clients to find the current primary |

Quorum and authorization to carry out failover are related but distinct. A quorum does not by itself guarantee that a failover can always finish.

### Sentinel commands

| Command | Purpose |
|---|---|
| `SENTINEL MASTERS` | Lists monitored primaries |
| `SENTINEL MASTER name` | Displays details about a monitored primary |
| `SENTINEL REPLICAS name` | Lists replicas of a monitored primary |
| `SENTINEL GET-MASTER-ADDR-BY-NAME name` | Returns the current primary's address and port |
| `SENTINEL CKQUORUM name` | Checks whether quorum and failover authorization conditions are satisfied |
| `SENTINEL FAILOVER name` | Requests a manual failover for a monitored primary |

These commands must be sent to a Sentinel instance that supports the relevant command. They are not ordinary Redis-server commands.

### When should Sentinel be used?

Use Sentinel when:

- One primary can handle the required workload.
- You need automatic failover for a primary-and-replica deployment.
- You want monitoring and primary discovery.
- You do not need Cluster's built-in data sharding.

A common production architecture runs multiple Sentinel instances across separate failure domains so that losing one machine does not remove all monitoring and quorum capability.

## 5. Redis Cluster

### What is Redis Cluster?

Redis Cluster distributes a dataset across multiple primary nodes. This distribution is called **sharding**.

Cluster can also use replicas for redundancy and failover. It addresses both data distribution and availability.

### What problem does Cluster solve?

Replication alone does not divide a dataset across multiple primaries. Replicas generally hold copies of their primary's dataset.

When a workload or dataset becomes too large for one primary, Cluster can distribute different keys across multiple primary nodes.

### How sharding works

```text
                 Application
                      |
                      v
              Cluster-aware client
                /      |      \
               v       v       v
          Primary A Primary B Primary C
             |         |         |
          Replica A Replica B Replica C
```

Each primary owns a portion of the keyspace. Its replica maintains a copy and may be promoted if the primary fails and failover conditions are satisfied.

### Hash slots

Redis Cluster uses **16,384 hash slots** to distribute keys.

Conceptually:

1. Redis calculates a hash slot for a key.
2. Each primary owns particular hash slots.
3. The key is stored on the primary responsible for that slot.
4. A cluster-aware client routes commands to the correct node.
5. If a command reaches the wrong node, Redis may return a `MOVED` response identifying the correct destination.

### Hash tags

Hash tags let related keys be placed in the same hash slot.

For example:

```text
cart:{user123}:items
cart:{user123}:total
```

Redis uses the text inside `{}` to calculate the hash slot for these keys. Both keys therefore map to the same slot, supporting operations that require related keys to share a slot.

Using the same hash tag for too many keys can concentrate traffic on one shard.

### Cluster commands

| Command | Purpose |
|---|---|
| `CLUSTER INFO` | Displays cluster health and state information |
| `CLUSTER NODES` | Lists cluster nodes, roles, and slot assignments |
| `CLUSTER KEYSLOT key` | Calculates the hash slot for a key |
| `CLUSTER SLOTS` | Displays slot ranges and their assigned nodes on supported versions |
| `CLUSTER SHARDS` | Displays shard and node information on supported versions |
| `CLUSTER REPLICATE node-id` | Configures a cluster node as a replica of the specified primary, subject to cluster conditions |
| `CLUSTER FAILOVER` | Requests failover from a replica under supported conditions |

These commands require a Redis Cluster-capable deployment. They were not used to create a live cluster in this project.

## 6. Sentinel vs Cluster

| Feature | Replication + Sentinel | Redis Cluster |
|---|---|---|
| Main purpose | High availability for a primary-based deployment | Sharding plus high availability |
| Number of primaries | One active primary for the monitored deployment | Multiple primaries |
| Data distribution | Replicas copy their primary's dataset | Keys are divided across primary shards |
| Failover management | Sentinel coordinates promotion | Cluster coordinates replica promotion |
| Scaling dataset across primaries | Not provided by Sentinel itself | Supported through sharding |
| Client requirement | Sentinel-aware primary discovery | Cluster-aware routing and redirects |
| Operational complexity | Generally simpler | Generally more complex |

### Which should you choose?

- **Replication alone:** When extra data copies or read scaling are useful, but automatic failover is not required.
- **Replication + Sentinel:** When one primary has enough capacity and automatic failover is required.
- **Redis Cluster:** When the dataset or workload needs to be distributed across multiple primaries as well as support failover.

## 7. Important Limitations

### Failover is not instantaneous

Applications may experience brief interruptions while a failure is detected and a replica is promoted.

### Recent writes may be lost

Because replication is asynchronous by default, a promoted replica may not have received every recent write.

### Replication is not a backup

Accidental deletions or incorrect updates can propagate to replicas. Persistence and a separate backup strategy may still be required.

### Cluster requires client support

Applications must use a Redis Cluster-aware client that handles key routing, redirects, and changes in cluster topology.

### Availability depends on deployment

A single machine running several processes does not provide the same resilience as distributing components across independent failure domains.

## 8. Practical Status in This Project

This topic was completed at the **theory level**.

The following concepts were studied:

- Primary and replica roles
- Replication and replication lag
- Automatic failover
- Sentinel monitoring and quorum
- Sentinel leader election and primary discovery
- Cluster sharding and hash slots
- Differences between Sentinel and Cluster
- Use cases and limitations

**Not implemented:** A multi-node replication deployment, Sentinel failover environment, or Redis Cluster deployment.

The existing development environment uses Memurai on Windows. Support for Sentinel and Cluster varies by Redis-compatible server and version, so these features should be tested in a suitable Redis Open Source environment before attempting a hands-on deployment.

## 9. Key Takeaways

1. **Replication copies data:** It provides redundancy and can support read scaling, but does not independently guarantee automatic failover.
2. **Sentinel manages failover:** It monitors a primary-based deployment and coordinates promotion of a replica when conditions permit.
3. **Cluster distributes data:** It shards keys across multiple primaries and supports replica-based failover, with additional operational and client requirements.

