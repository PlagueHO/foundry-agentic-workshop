# Module 02: Foundry portal walkthrough

## Objectives

- Orient yourself in the Microsoft Foundry portal layout.
- Explore models on the Discover tab and compare candidates.
- Understand the Build tab surfaces you will use in later steps.

## Steps

1. Open the Microsoft Foundry portal and sign in with your workshop account.
1. Start on the **Home** tab and review the overall layout: the left
   navigation, the active project selector, and recent activity.
1. Open the **Discover** tab.
   1. Browse the available models in the model catalog.
   1. Open a model card to review its description, capabilities, and limits.
   1. Use **Compare** to place two models side by side and review context
      window, modality, and pricing differences.
   1. Note where **Agents** and **Tools** appear in Discover. You will return
      to these in later steps; no configuration is needed now.
1. Open the **Build** tab and locate each surface you will use later:
   1. **Models** and deployed models for this project.
   1. **Tools** available to agents.
   1. **Knowledge** sources, including Azure AI Search connections.
   1. **Memory** for conversation and thread state.
   1. **Guardrails** and content safety policies.
   1. **Agents** overview, where prompt-based and hosted agents are listed.

## Validation

- You can name the three primary tabs (Home, Discover, Build) and what each is
  for.
- You located the deployed `chat` and `embedding` models for your project on
  the Build tab.
- You can find the Knowledge and Agents surfaces you will use in later steps.

## Troubleshooting

- If you cannot see your project, confirm the active project selector matches
  the project assigned to you in Module 00.
- If models are missing from Build, confirm provisioning completed and that
  `azd env get-values` shows the expected Foundry resource.
- If a tab is empty, refresh the portal and confirm your role grants read
  access to the project.
