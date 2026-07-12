---
description: 'YAML front matter rules for numbered lab module README files'
applyTo: 'labs/*/*/README.md'
---

# Lab module front matter

Every numbered lab module README must begin with a YAML front matter block.

## Required schema

```yaml
---
title: 'NN. Module title'
description: 'One-sentence description of the module.'
lastUpdated: '2026-07-13'
track: 'introduction-foundry-agent-service'
module: 1
slug: '01-module-name'
estimatedTimeMinutes: 15
difficulty: 'beginner'
prerequisites: []
audience:
  - 'attendee'
technologies:
  - 'Microsoft Foundry'
tags:
  - 'foundry'
status: 'active'
contentType: 'lab'
---
```

## Authoring rules

- Keep the front matter at the beginning of the file, before the H1.
- Set `track`, `module`, and `slug` from the README path.
- Set `title` to the visible H1 value exactly.
- Set `lastUpdated` to the date the module content was last updated, using `YYYY-MM-DD` format.
- Set `estimatedTimeMinutes` to the numeric value in the visible estimated-time line.
- Use `difficulty` values `beginner`, `intermediate`, or `advanced`.
- Use `status` values `active` or `draft`.
- Use `contentType: 'lab'` for numbered lab modules.
- Use lowercase kebab-case for `tags`.
- Keep the visible H1 and estimated-time line in the Markdown body for GitHub readability.
- Do not add this front matter to nested solution READMEs or track-level READMEs.
