# 08 Integrate Foundry IQ knowledge bases

**Estimated time:** TBD

## Objectives

- Configure a Foundry IQ knowledge base backed by Azure AI Search.
- Connect two knowledge sources: retail products and retail policies.
- Attach the knowledge base to the agent and validate grounded answers.

## Steps

- [ ] Confirm the AI Search indices provisioned in Module 00 exist:
  - [ ] The retail products index (`AZURE_SEARCH_PRODUCT_INDEX_NAME`).
  - [ ] The retail policies index (`AZURE_SEARCH_DOCUMENT_INDEX_NAME`).
- [ ] In the Build tab, open **Knowledge** and create a Foundry IQ knowledge base.
- [ ] Add the first knowledge source:
  - [ ] Connect the retail products index.
  - [ ] Confirm fields map correctly, including the vector field.
- [ ] Add the second knowledge source:
  - [ ] Connect the retail policies index.
  - [ ] Confirm fields map correctly, including the vector field.
- [ ] Attach the knowledge base to the `retail-assistant` agent.
- [ ] Update the agent instructions to prefer knowledge for product and policy
   questions.
- [ ] Run grounded queries, for example:
  - [ ] "What is the return window for opened electronics?"
  - [ ] "Recommend a product for a home barista and cite the source."

## Validation

- Both knowledge sources appear in the knowledge base and are attached to the
  agent.
- Product and policy questions return grounded answers drawn from the indices.
- Responses reference retrieved content rather than only model memory.

## Troubleshooting

- If a source has no results, confirm the seed scripts populated the indices
  and that the index names match the environment values.
- If retrieval is poor, confirm the vector field is mapped and the embedding
  dimensions match the index schema.
- If access fails, confirm your role grants access to the AI Search resource
  and the project.
