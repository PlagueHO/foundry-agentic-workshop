## Change type

<!-- Check every type that applies. At least one must be selected. -->

- [ ] Bug or fix - corrects a defect, broken step, or inaccuracy in existing content
- [ ] Lab improvement or addition - improves clarity, adds a step, screenshot, concept, or validation to an existing module
- [ ] New module - adds a new numbered module to an existing lab series
- [ ] New lab - adds an entirely new lab series under `labs/`
- [ ] Infrastructure - changes to Bicep, `azure.yaml`, or provisioning scripts
- [ ] Documentation - changes to the VitePress docs site, guides, or quickstarts
- [ ] Scripts - changes to `scripts/`, `shared/`, or `tools/`
- [ ] CI / tooling - changes to GitHub Actions workflows, linting config, or dev tooling
- [ ] Other - describe below

## Related issues

<!-- Link every issue this PR resolves or relates to. -->

Closes #

## Summary

<!-- One paragraph describing what changed and why. -->

## Modules or files affected

<!-- List the lab modules, scripts, or infra files this PR changes. -->

-

## Validation performed

<!-- Describe what you ran or tested to confirm the change is correct. -->

- [ ] `pnpm run lint:md` passes (required for any `.md` change)
- [ ] `az bicep build --file infra/main.bicep` and `az bicep lint --file infra/main.bicep` pass (required for any Bicep change)
- [ ] `python -m compileall labs scripts shared` passes (required for any Python change)
- [ ] Manually walked through affected lab steps as an attendee
- [ ] Ran affected solution script(s) end-to-end

## Checklist

- [ ] No secrets, tokens, keys, or connection strings are committed.
- [ ] `shared/.env.example` is updated if new environment variables are introduced.
- [ ] Change is scoped to the stated intent - no unrelated refactoring included.
- [ ] Docs site regenerated via `pnpm run docs:generate-labs` if any lab README was added or renamed.
