"""
Azure DevOps Tools
==================

Custom tools for Azure DevOps integration.
Note: Most Azure DevOps operations are now handled via Azure MCP server.
This file retains only the create_work_item tool for HITL approval.
"""

import base64
import os
from typing import Optional

import httpx
from agno.approval import approval
from agno.tools import tool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure DevOps configuration
AZURE_DEVOPS_URL = os.getenv("AZURE_DEVOPS_URL")
AZURE_DEVOPS_EMAIL = os.getenv("AZURE_DEVOPS_EMAIL")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")


def get_auth_headers() -> dict:
    """Get authentication headers for Azure DevOps API."""
    # Azure DevOps requires base64-encoded credentials for Basic auth
    auth_string = f"{AZURE_DEVOPS_EMAIL}:{AZURE_DEVOPS_PAT}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    return {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json",
    }


@approval
@tool(requires_confirmation=True)
def create_work_item(
    project: str,
    title: str,
    description: str,
    work_item_type: str = "Bug",
    assigned_to: Optional[str] = None,
) -> str:
    """Create an Azure DevOps work item/ticket with RCA findings.

    Args:
        project (str): Azure DevOps project name
        title (str): Work item title
        description (str): Work item description with RCA findings
        work_item_type (str): Type of work item (default: "Bug")
        assigned_to (str): Optional user email to assign the work item to

    Returns:
        str: Created work item ID and URL

    Note:
        This tool requires HITL approval before execution.
        Other Azure DevOps operations (pipeline runs, logs, etc.) are handled via Azure MCP.
    """
    if not AZURE_DEVOPS_URL or not AZURE_DEVOPS_PAT:
        return "Error: Azure DevOps credentials not configured. Set AZURE_DEVOPS_URL and AZURE_DEVOPS_PAT in .env"

    try:
        # Get the work item type ID
        url = f"{AZURE_DEVOPS_URL}/{project}/_apis/wit/workitemtypes/{work_item_type}?api-version=7.0"
        response = httpx.get(url, headers=get_auth_headers())
        response.raise_for_status()
        type_info = response.json()

        # Create the work item
        url = f"{AZURE_DEVOPS_URL}/{project}/_apis/wit/workitems/${work_item_type}?api-version=7.0"
        headers = get_auth_headers()
        headers["Content-Type"] = "application/json-patch+json"

        body = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
        ]

        if assigned_to:
            body.append(
                {"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to}
            )

        response = httpx.patch(url, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()

        work_item_id = result["id"]
        work_item_url = f"{AZURE_DEVOPS_URL}/{project}/_workitems/edit/{work_item_id}"

        return f"Work item created successfully. ID: {work_item_id}, URL: {work_item_url}"
    except Exception as e:
        return f"Error creating work item: {str(e)}"
