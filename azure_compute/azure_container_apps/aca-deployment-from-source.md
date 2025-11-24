# Azure Container Apps - Deployment from Source Code

## Overview

Azure Container Apps (ACA) provides multiple ways to deploy containerized applications. One of the most convenient methods is deploying directly from source code using a Dockerfile.

## Deployment Methods

### Using `az containerapp up` with Source Code

The `az containerapp up` command is a convenient way to build and deploy container apps directly from source code. When you have a Dockerfile in your repository, you can use this command to:

1. Build the container image from the Dockerfile
2. Push the image to a container registry
3. Create or update the container app
4. Deploy the application

**Command:**
```bash
az containerapp up --source .
```

The `--source .` parameter tells the command to use the current directory (which should contain the Dockerfile) as the source for building the container image.

### Other Container App Commands

- **`az containerapp env create`**: Creates a Container Apps environment (the infrastructure boundary for container apps), but doesn't deploy an app
- **`az containerapp create`**: Creates a container app, but requires additional parameters:
  - `--image`: Requires a pre-built container image reference (e.g., from ACR or Docker Hub)
  - `--containername`: Not a valid parameter for this command

## Practice Question

**Scenario:**
Your company is developing an application that includes a backend web API service. The development team has decided to use Azure Container Apps to host the API. They have a Dockerfile in the root of their repository that defines the containerized app.

**Question:**
You need to deploy the container app using the Dockerfile. What should you do?

**Options:**

1. ❌ Use the `az containerapp env create` command with the `--name` parameter.
   - **Incorrect**: This command only creates the Container Apps environment, not the actual container app.

2. ❌ Use the `az containerapp create` command with the `--image` parameter.
   - **Incorrect**: This requires a pre-built container image. It doesn't build from a Dockerfile.

3. ❌ Use the `az containerapp create` command with the `--containername` parameter.
   - **Incorrect**: This parameter doesn't exist for this command and doesn't fulfill the requirement.

4. ✅ Use the `az containerapp up` command with the `--source .` parameter.
   - **Correct**: This command builds and deploys the container app using the Dockerfile in the root of the repository.

## Key Takeaways

- **`az containerapp up`** is the simplest way to deploy from source code with a Dockerfile
- The command handles the entire workflow: build, push, and deploy
- The `--source` parameter specifies the directory containing the Dockerfile
- This approach is ideal for rapid development and deployment scenarios

## Additional Resources

- [Quickstart: Build and deploy from local source code to Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/quickstart-code-to-cloud)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)

## Related Topics

- Azure Container Registry (ACR) integration
- Container Apps environments
- Dockerfile best practices
- CI/CD pipelines with Azure Container Apps
