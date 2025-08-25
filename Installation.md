
---

### Installation Instructions

1. **Docker Operations**

   * Build the Docker image.
   * Push the Docker image to the configured container registry.

2. **Kubernetes Setup**

   * Initialize Kubernetes within the Docker environment.
   * Deploy resources using:

     ```bash
     kubectl apply -f retainai.yml
     ```

3. **Cluster Verification**

   * Confirm node status:

     ```bash
     kubectl get nodes
     ```
   * Verify pods and services:

     ```bash
     kubectl get pods,services
     ```

4. **Application Access**

   * Configure application service ports using Ngrok.

5. **Twilio Configuration**

   * Update the Twilio settings with the Ngrok URL for external access.

---