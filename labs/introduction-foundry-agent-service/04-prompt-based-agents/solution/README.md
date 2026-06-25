# Solution - Module 04: Create and chat with a Prompt Agent

This folder contains the reference solution for facilitators and proctors.

## Agent definition

**Name:** `acl-remedy-advisor`
**Model:** `chat` (gpt-5.3-chat, deployed as `chat` in the workshop Foundry account)
**Tool:** Web Search (built-in, Microsoft Foundry)

**Instructions:**

```text
You are an Australian Consumer Law (ACL) Remedy Advisor for retail staff.
When a customer reports a problem with a product, help staff determine the
correct remedy under the ACL consumer guarantees.

Distinguish between a **major failure** (the customer may choose a refund,
replacement, or repair) and a **minor failure** (the business may choose to
repair the product within a reasonable time, or offer a replacement or refund).

When assessing a situation consider:
- The type of product and its expected lifespan
- The price paid
- How long the customer has had the product
- What a reasonable consumer would expect

Use web search to ground your guidance in current ACCC guidance at
accc.gov.au and always cite your sources with links.

Always state clearly that you provide general guidance, not legal advice,
and that "no refund" signs are unlawful under the ACL.

Be concise and practical - retail staff need fast, clear answers in a
busy store environment.
```

## Creating the agent from code

If the Foundry Toolkit Agent Builder cannot reach the project endpoint (for
example in a Codespace with network restrictions), create the agent
programmatically:

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint='<FOUNDRY_PROJECT_ENDPOINT>',
    credential=DefaultAzureCredential(),
)
agent = client.agents.create_version(
    agent_name='acl-remedy-advisor',
    definition=PromptAgentDefinition(
        model='chat',
        instructions='<paste instructions above>',
        tools=[WebSearchTool()],
    ),
)
print(f'Created: {agent.name} version {agent.versions["latest"]["version"]}')
```

## Solution code

See `starter.py` in this folder for the complete solution.

## Expected output

```text
Conversation started: conv_<id>

ACL Remedy Advisor - type your question, or "exit" to quit.

You: A customer wants to return a $1,200 TV that stopped working after 18 months. What are their rights under Australian Consumer Law?
[web search]

Advisor: General guidance only (not legal advice).

**Short answer for staff:**
A $1,200 TV failing after **18 months** may still breach the ACL consumer
guarantee of **acceptable quality** ...

[response continues with major/minor failure analysis and ACCC citations]

You: The customer says they just want a refund and don't want a repair. Can the store insist on repairing it first?
[web search]

Advisor: General guidance only (not legal advice).

**Yes - the store can insist on repairing it first if the fault is a *minor failure*.**

[response continues citing accc.gov.au and state consumer affairs sites]

You: exit
Goodbye.
```
