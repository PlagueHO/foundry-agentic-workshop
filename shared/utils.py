"""Reusable workshop helper utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class WorkshopContext:
    resource_group: str
    foundry_resource: str
    project_name: str


def load_context() -> WorkshopContext:
    return WorkshopContext(
        resource_group=os.getenv('AZURE_RESOURCE_GROUP', 'rg-foundry-hol'),
        foundry_resource=os.getenv('FOUNDRY_RESOURCE_NAME', ''),
        project_name=os.getenv('FOUNDRY_PROJECT_NAME', ''),
    )
