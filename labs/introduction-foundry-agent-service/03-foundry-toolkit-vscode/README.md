# 03. Foundry Toolkit for VS Code

## Objectives

- Confirm the Foundry Toolkit for VS Code extension is installed and signed in.
- Connect the toolkit to your existing Foundry project.
- Tour the toolkit UI and how it interacts with agents and models.

## Steps

1. Open the Extensions view in VS Code and confirm the **Foundry Toolkit**
   extension is installed and enabled.
1. Open the Foundry Toolkit view from the Activity Bar.
1. Sign in with your workshop account if prompted, and confirm the toolkit
   reports an authenticated session.
1. Connect to your existing Foundry project:
   1. Select your subscription and resource group.
   1. Select the Foundry resource and the project assigned to you in Module 00.
1. Tour the toolkit surfaces:
   1. **Models** lists the deployed models available to the project.
   1. **Agents** lists prompt-based and hosted agents.
   1. **Tools** and **Knowledge** show what agents can call and retrieve.
1. Open the playground or chat surface and confirm you can select the deployed
   `chat` model.

## Validation

- The toolkit shows an authenticated session for your workshop account.
- The connected project matches the one assigned to you in Module 00.
- You can list the deployed models and any existing agents for the project.

## Troubleshooting

- If sign-in fails, run `az login` in the integrated terminal and retry the
  toolkit sign-in.
- If the project is missing, confirm `FOUNDRY_RESOURCE_NAME` and
  `FOUNDRY_PROJECT_NAME` with `azd env get-values`.
- If models do not appear, confirm provisioning completed and your role grants
  access to the project.
