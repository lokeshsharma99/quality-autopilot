"""
Engineer Agent Tools
====================

Custom tools for the Engineer agent.
"""

import json
import os
from typing import Any

from agno.tools import tool

from contracts.automation_scaffold import AutomationScaffold, ScaffoldConfig, ScaffoldFile


@tool(
    name="run_playwright_script",
    description="Run a Playwright script and return the output. Useful for custom locator extraction or page interaction.",
)
def run_playwright_script(
    script_content: str,
    headless: bool = True,
) -> str:
    """Run a Playwright script and return the output.

    Args:
        script_content: Playwright script to execute
        headless: Whether to run in headless mode

    Returns:
        JSON string with script execution results
    """
    result = {
        "script": script_content,
        "headless": headless,
        "message": "Playwright script execution - use playwright_evaluate for JavaScript execution"
    }
    return json.dumps(result, indent=2)


@tool(
    name="create_scaffold",
    description="Create a BDD+POM automation framework scaffold with features, step definitions, pages, and config files.",
)
def create_scaffold(
    project_name: str,
    base_url: str,
    output_dir: str = "automation",
    browser: str = "chromium",
    headless: bool = True,
) -> str:
    """Create a BDD+POM automation framework scaffold.

    Args:
        project_name: Name of the automation project
        base_url: Base URL of the application under test
        output_dir: Directory where the scaffold will be created
        browser: Browser to use for testing (chromium, firefox, webkit)
        headless: Whether to run tests in headless mode

    Returns:
        JSON string with AutomationScaffold details including created structure and files
    """
    # Create directory structure
    dirs = [
        f"{output_dir}/features",
        f"{output_dir}/step_definitions",
        f"{output_dir}/pages",
        f"{output_dir}/config",
        f"{output_dir}/tests",
        f"{output_dir}/reports",
        f"{output_dir}/hooks",
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Create package.json
    package_json = {
        "name": project_name.lower().replace(" ", "-"),
        "version": "1.0.0",
        "description": f"Automation framework for {project_name}",
        "scripts": {
            "test": "cucumber-js",
            "test:headed": "cucumber-js --profile headed"
        },
        "devDependencies": {
            "@cucumber/cucumber": "^12.8.0",
            "@playwright/test": "^1.42.0",
            "@types/node": "^20.0.0",
            "cucumber-html-reporter": "^9.2.0",
            "ts-node": "^10.9.2",
            "typescript": "^5.4.5"
        }
    }
    
    with open(f"{output_dir}/package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    # Create playwright.config.ts
    playwright_config = f'''import {{ defineConfig, devices }} from '@playwright/test';

export default defineConfig({{
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {{
    baseURL: '{base_url}',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  }},
  projects: [
    {{
      name: '{browser}',
      use: {{ ...devices['Desktop Chrome'] }},
    }},
  ],
}});
'''
    
    with open(f"{output_dir}/playwright.config.ts", "w") as f:
        f.write(playwright_config)
    
    # Create BasePage class
    base_page = '''import { Page, Locator } from '@playwright/test';

export class BasePage {
  constructor(protected page: Page) {}

  async navigate(url: string): Promise<void> {
    await this.page.goto(url);
  }

  async click(locator: Locator): Promise<void> {
    await locator.click();
  }

  async fill(locator: Locator, value: string): Promise<void> {
    await locator.fill(value);
  }

  async getText(locator: Locator): Promise<string> {
    return await locator.textContent() || '';
  }

  async waitForElement(locator: Locator): Promise<void> {
    await locator.waitFor();
  }
}
'''
    
    with open(f"{output_dir}/pages/BasePage.ts", "w") as f:
        f.write(base_page)
    
    # Create example feature file
    example_feature = f'''Feature: {project_name} User Flow

  Scenario: User navigates to home page
    Given user is on the home page
    Then page title should contain "{project_name}"
'''
    
    with open(f"{output_dir}/features/example.feature", "w") as f:
        f.write(example_feature)
    
    # Create example page object
    example_page = f'''import {{ BasePage }} from './BasePage';

export class HomePage extends BasePage {{
  constructor(page: Page) {{
    super(page);
  }}

  get pageTitle(): Locator {{
    return this.page.locator('h1');
  }}
}}
'''
    
    with open(f"{output_dir}/pages/HomePage.ts", "w") as f:
        f.write(example_page)
    
    # Build scaffold structure
    scaffold_structure = ScaffoldStructure(
        directories=dirs,
        files=[
            ScaffoldFile(
                path="package.json",
                description="NPM dependencies and scripts"
            ),
            ScaffoldFile(
                path="playwright.config.ts",
                description="Playwright test configuration"
            ),
            ScaffoldFile(
                path="pages/BasePage.ts",
                description="Base page class with common methods"
            ),
            ScaffoldFile(
                path="pages/HomePage.ts",
                description="Home page object"
            ),
            ScaffoldFile(
                path="features/example.feature",
                description="Example Cucumber feature file"
            )
        ]
    )
    
    scaffold_config = ScaffoldConfig(
        project_name=project_name,
        base_url=base_url,
        output_dir=output_dir,
        browser=browser,
        headless=headless,
    )
    
    result = AutomationScaffold(
        config=scaffold_config,
        structure=scaffold_structure,
        message=f"Successfully created BDD+POM automation scaffold for {project_name}"
    )
    
    return result.model_dump_json(indent=2)
