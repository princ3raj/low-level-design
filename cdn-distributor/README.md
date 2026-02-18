# Enterprise CDN Distributor (LLD)

A robust, production-grade implementation of a Content Delivery Network (CDN) distributor system using Python. This project demonstrates advanced Low-Level Design (LLD) patterns for high reliability, scalability, and resilience.

## 🏗 System Architecture

The system follows a reactive **Observer Pattern**:
1.  **S3 Bucket (Source)**: Managing uploads and notifying the publisher.
2.  **S3 Event Publisher**: Asynchronously broadcasts events to listeners.
3.  **CDN Controller**: The "Brain" that routes content to edge nodes.
4.  **Edge Nodes**: Distributed servers that cache content.

## 🚀 Key Features

### 1. Reliability & Concurrency
*   **Asynchronous Notification**: Uses `ThreadPoolExecutor` to prevent slow listeners from blocking the entire system.
*   **Memory Safety**: Uses `weakref.WeakSet` to prevent memory leaks from "zombie" listeners.
*   **Thread Safety**: Critical sections (registration/unregistration) are protected by `threading.Lock`.
*   **Retry Policy**: Robust retry mechanism with exponential backoff for network operations.

### 2. Advanced Traffic Control
*   **🌍 Region-Aware Routing**: Content tagged with specific regions (e.g., `["US"]`) is only routed to relevant edge nodes, saving bandwidth.
*   **🛡️ Checksum Deduplication**: MD5 checksums prevent re-pushing identical content, optimizing network usage.
*   **🧠 Delta Updates (Simulated)**: Detects version changes to simulate efficient delta transfers.

### 3. Resilience Patterns
*   **🧹 Invalidation Strategy**: Supports a "Pull-on-Demand" model where content is marked stale and fetched only when requested.
*   **🔄 Edge Pull Fallback**: If a "Push" fails or a node crashes, the Edge Node automatically "calls home" (Pull) to fetch the missing content from the Origin.

## 🛠 Project Structure

```
src/
├── cdn/
│   └── controller.py       # Smart router & Origin logic
├── models/
│   ├── content.py          # Content model with checksums
│   ├── observer.py         # Interfaces for Listeners
│   └── retry_policy.py     # Resilience logic
├── s3/
│   ├── publisher.py        # Async event broadcaster
│   └── upload.py           # S3 Bucket simulation
```

## 🏃‍♂️ Usage

Run the client simulation to see all features in action:
```bash
python3 client.py
```

### Simulation Scenarios
1.  **Standard Upload**: Broadcasters to all regions.
2.  **Region-Specific Upload**: Targets only US/IN nodes.
3.  **Deduplication**: Skips redundant uploads.
4.  **Invalidation**: Marks content as stale.
5.  **Edge Pull Fallback**: Simulates data loss and recovery via Origin Pull.
