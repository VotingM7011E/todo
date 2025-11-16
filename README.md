### ⚠️ Known Issue: Stateless Backend with Multiple Replicas

When running multiple backend replicas, each pod stores todos **in-memory**. Because Kubernetes load-balances requests across pods, refreshing the page may show an empty list if the request hits a different pod.

#### Why this happens
- The backend uses a Python list (`todos = []`) inside the container.
- No shared state between pods → each replica has its own isolated data.

#### How to fix it
To make the backend truly scalable, use a shared data store:
- **Option 1:** Add a database (PostgreSQL, MySQL, MongoDB).
- **Option 2:** Use a distributed cache (Redis).
- **Option 3:** Mount a PersistentVolume (not ideal for concurrent writes).

For production, **Option 1 or 2 is recommended**. This ensures all replicas share the same data and avoids inconsistent states.