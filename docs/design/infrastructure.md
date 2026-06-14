# Infrastructure design

This document contains the design rationale for the infrastructure deployed to support the labs in this repository.

## Hosted agents and the container registry

Some modules deploy a **hosted agent** — attendee container code that Foundry runs as a managed endpoint. Provisioning adds one shared **Azure Container Registry (ACR)** and the role assignments hosted agents need, so attendees can complete the module without any manual setup.

### What gets deployed

* A single Azure Container Registry shared by all attendees, with a `ContainerRegistry` connection on the Foundry account. The SKU defaults to `Basic` (override with `AZURE_CONTAINER_REGISTRY_SKU`).
* Each attendee project's managed identity receives **AcrPull** so Foundry can pull the agent image.
* Each attendee receives **AcrPush** on the registry so the Part 1 container path can push an image.
* Each attendee receives a **constrained Role Based Access Control Administrator** role on the Foundry account, conditioned so they can assign **only** the **Foundry User** role and **only** to service principals.

### Why the constrained RBAC Administrator role

Every hosted agent gets its own Microsoft Entra agent identity at deploy time, and that identity needs the **Foundry User** role on the Foundry account to call models at runtime. The identity does not exist until the agent version is created, so the role cannot be pre-assigned in Bicep — the attendee's deploy script assigns it. The constrained Role Based Access Control Administrator role (ABAC-conditioned) lets attendees make exactly that one assignment and nothing else, keeping the grant within least privilege.

### Avoiding attendee collisions

All attendees share one registry. The Part 1 deploy script tags each image with the attendee's project name (`acl-remedy-advisor-hosted-container:<project>`), and every hosted agent is scoped to its own project, so attendees never overwrite each other's images or agents.

### Customise the registry SKU

```bash
# Default is Basic; Standard or Premium raise throughput and storage limits
azd env set AZURE_CONTAINER_REGISTRY_SKU Standard
```
