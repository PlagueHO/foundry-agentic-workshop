# Step 00: Workshop setup and access verification

## Objectives

- Confirm your local tooling is installed and ready.
- Sign in to Azure and confirm access to your assigned Foundry project.
- Verify the pre-provisioned environment so you can focus on agents.

## Steps

1. Open this workshop in VS Code Insiders.
1. Confirm prerequisites are installed:
   1. The Foundry Toolkit for VS Code extension.
   1. The Azure CLI (`az`) and the Azure Developer CLI (`azd`).
   1. Python 3.13 or later.
1. Install the shared Python dependencies from `shared/requirements.txt`.
1. Sign in and select your subscription:
   1. Run `az login`.
   1. Confirm the active subscription matches the workshop subscription.
1. Load the environment values your proctor provisioned:
   1. Run `azd env get-values` and confirm the Foundry and AI Search values are
      present.
   1. Confirm your assigned Foundry project name.
1. Run the shared health check with `python scripts/health-check.py` and confirm
   it reports a healthy environment.

## Validation

- `az login` succeeds and the active subscription is correct.
- `azd env get-values` shows the Foundry endpoint, project name, and AI Search
  values.
- `python scripts/health-check.py` reports a healthy environment.

## Troubleshooting

- Verify Azure login (`az login`) and subscription context.
- Confirm access to the assigned Foundry project.
- Re-run shared health checks from `scripts/health-check.py`.
