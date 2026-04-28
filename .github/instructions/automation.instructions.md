---
applyTo: "automation/**/*.ts"
---

# Automation Framework — Copilot Instructions

These instructions apply to all TypeScript files under `automation/`.

## Framework Stack

- **BDD**: Cucumber (`@cucumber/cucumber`)
- **Browser**: Playwright (`@playwright/test`)
- **Pattern**: Page Object Model (POM)
- **Language**: TypeScript strict mode

## Directory Layout

```
automation/
├── features/            ← .feature files (Gherkin, authored by Scribe agent)
├── step_definitions/    ← Cucumber step implementations (.ts)
├── pages/               ← Playwright Page Object Models (.ts)
├── hooks/               ← Before/After hooks (.ts)
├── fixtures/            ← Test data fixtures (.ts)
├── config/              ← AUT-specific config (.ts)
├── cucumber.conf.ts     ← Cucumber runner config
├── playwright.config.ts ← Playwright browser config
└── tsconfig.json        ← TypeScript config (strict: true)
```

## Page Object Model Rules

```typescript
// pages/LoginPage.ts — one class per page, no logic, no assertions
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    // ✅ Use data-testid, role, or text strategies ONLY
    this.emailInput    = page.getByTestId('email-input');
    this.passwordInput = page.getByTestId('password-input');
    this.submitButton  = page.getByRole('button', { name: 'Sign in' });
    // ❌ NEVER: page.locator('.btn-primary')  — fragile CSS
    // ❌ NEVER: page.locator('//button[1]')   — fragile XPath
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    // ✅ Playwright auto-waits — no sleep/waitForTimeout needed
  }
}
```

## Step Definition Rules

```typescript
// step_definitions/login.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

Given('the user is on the login page', async function () {
  const loginPage = new LoginPage(this.page);
  await this.page.goto(process.env.BASE_URL + '/login');
});

When('the user logs in with {string} and {string}', async function (email: string, password: string) {
  const loginPage = new LoginPage(this.page);
  await loginPage.login(email, password);
});
```

## Locator Strategy Priority

1. `getByTestId('data-testid-value')` — preferred
2. `getByRole('button', { name: 'Submit' })` — semantic
3. `getByText('exact text')` — visible text
4. `getByLabel('Field label')` — form inputs
5. ❌ `locator('.css-class')` — NEVER
6. ❌ `locator('//xpath')` — NEVER

## Test Data

- **Never hardcode** test data in step definitions or POMs.
- Import fixtures from `fixtures/` directory.
- Test data comes from the Data Agent's `RunContext` contract.
- Use environment variables (`process.env.BASE_URL`, `process.env.TEST_USER_EMAIL`).

## Absolute Prohibitions

| Never do this | Do this instead |
|---------------|----------------|
| `page.waitForTimeout(2000)` | Playwright auto-waiting |
| `await new Promise(r => setTimeout(r, 1000))` | `await page.waitForSelector(...)` |
| CSS selectors (`.class`, `#id`) | `getByTestId`, `getByRole`, `getByText` |
| XPath selectors | Semantic locator strategies |
| Hardcoded credentials in test files | `process.env.TEST_USER_EMAIL` |
| Business logic inside Page Objects | POMs are navigation + interaction only |
| Assertions inside Page Objects | Assertions belong in step definitions |

## Configuration

```typescript
// playwright.config.ts — base settings
import { defineConfig } from '@playwright/test';
export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'https://demo.nopcommerce.com/',
    headless: process.env.HEADLESS !== 'false',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
});
```

## Running Tests

```bash
# All tests
npm test

# Headed (visible browser)
npm run test:headed

# Single feature
npx cucumber-js features/login.feature \
  --require hooks/**/*.ts \
  --require step_definitions/**/*.ts \
  --require-module ts-node/register
```
