# contracts/site_manifesto.py
"""Pydantic models for Site Manifesto - UI structure and locators from Discovery Agent."""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


# ---------------------------------------------------------------------------
# UI Component
# ---------------------------------------------------------------------------

class UIComponent(BaseModel):
    """Represents a single interactable UI element on a page."""
    
    component_id: str = Field(..., description="Unique identifier for the component")
    component_type: str = Field(..., description="Type of component (button, input, link, etc.)")
    aria_role: Optional[str] = Field(None, description="ARIA role for accessibility")
    aria_label: Optional[str] = Field(None, description="ARIA label for accessibility")
    text: Optional[str] = Field(None, description="Visible text content")
    
    # Locator strategies (ordered by priority)
    data_testid: Optional[str] = Field(None, description="data-testid locator (highest priority)")
    role_locator: Optional[str] = Field(None, description="Playwright role-based locator")
    text_locator: Optional[str] = Field(None, description="Text-based locator")
    css_selector: Optional[str] = Field(None, description="CSS selector (fallback)")
    xpath: Optional[str] = Field(None, description="XPath (last resort)")
    
    # Metadata
    accessibility_tree_hash: str = Field(..., description="Hash of accessibility tree for change detection")
    is_interactable: bool = Field(True, description="Whether the element is interactable")
    is_auth_gated: bool = Field(False, description="Whether this component requires authentication")

    model_config = ConfigDict(json_schema_extra={"example": {"component_id": "login-button", "component_type": "button"}})


# ---------------------------------------------------------------------------
# Page Entry
# ---------------------------------------------------------------------------

class PageEntry(BaseModel):
    """Represents a single page in the AUT with its components."""
    
    page_id: str = Field(..., description="Unique identifier for the page")
    url: str = Field(..., description="Full URL of the page")
    route: str = Field(..., description="Route path (e.g., /login)")
    title: str = Field(..., description="Page title")
    
    # Page classification
    is_auth_gated: bool = Field(False, description="Whether page requires authentication")
    is_public: bool = Field(True, description="Whether page is publicly accessible")
    page_type: str = Field(..., description="Type of page (home, login, dashboard, etc.)")
    
    # Components on this page
    components: List[UIComponent] = Field(default_factory=list, description="List of UI components")
    
    # Metadata
    accessibility_tree_hash: str = Field(..., description="Hash of full page accessibility tree")
    crawled_at: str = Field(..., description="Timestamp when page was crawled")

    model_config = ConfigDict(json_schema_extra={"example": {"page_id": "login-page", "url": "https://example.com/login"}})


# ---------------------------------------------------------------------------
# Site Manifesto
# ---------------------------------------------------------------------------

class SiteManifesto(BaseModel):
    """Complete map of the AUT's UI structure, pages, and locators."""
    
    manifesto_id: str = Field(..., description="Unique identifier for this manifesto")
    aut_base_url: str = Field(..., description="Base URL of the Application Under Test")
    aut_name: str = Field(..., description="Name of the AUT")
    
    # Pages
    pages: List[PageEntry] = Field(default_factory=list, description="All discovered pages")
    
    # Statistics
    total_pages: int = Field(default=0, description="Total number of pages discovered")
    total_components: int = Field(default=0, description="Total number of components across all pages")
    
    # Crawl metadata
    crawled_at: str = Field(..., description="Timestamp when manifesto was generated")
    crawl_duration_seconds: float = Field(..., description="Time taken to crawl the site")
    
    # Quality metrics
    ghost_references: int = Field(default=0, description="Count of ghost references (should be 0)")
    auth_handshake_success: bool = Field(False, description="Whether authentication handshake succeeded")
    
    # Additional metadata
    crawler_version: str = Field("1.0.0", description="Version of the crawler that generated this manifesto")
    notes: Optional[str] = Field(None, description="Additional notes about the crawl")

    model_config = ConfigDict(json_schema_extra={"example": {"manifesto_id": "manifesto-001", "aut_base_url": "https://example.com"}})
    
    def calculate_statistics(self) -> None:
        """Calculate total pages and components from the pages list."""
        self.total_pages = len(self.pages)
        self.total_components = sum(len(page.components) for page in self.pages)
