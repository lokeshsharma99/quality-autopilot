import { Page } from '@playwright/test';

/**
 * BasePage — abstract base class for all Page Object Models.
 *
 * Rules enforced here:
 * - No hardcoded sleeps (use Playwright auto-waiting)
 * - Locator priority: data-testid > role > text > css (last resort)
 * - All public methods must be async
 */
export abstract class BasePage {
  protected page: Page;
  readonly baseUrl: string;

  constructor(page: Page, baseUrl: string = '') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  /** Navigate to the page's route. Override in subclass. */
  abstract navigate(): Promise<void>;

  // ---------------------------------------------------------------------------
  // Locator helpers (priority: testid > role > text)
  // ---------------------------------------------------------------------------

  protected byTestId(testId: string) {
    return this.page.getByTestId(testId);
  }

  protected byRole(role: Parameters<Page['getByRole']>[0], options?: Parameters<Page['getByRole']>[1]) {
    return this.page.getByRole(role, options);
  }

  protected byText(text: string, options?: Parameters<Page['getByText']>[1]) {
    return this.page.getByText(text, options);
  }

  protected byLabel(label: string) {
    return this.page.getByLabel(label);
  }

  protected byPlaceholder(placeholder: string) {
    return this.page.getByPlaceholder(placeholder);
  }

  // ---------------------------------------------------------------------------
  // Common actions
  // ---------------------------------------------------------------------------

  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async getTitle(): Promise<string> {
    return this.page.title();
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }
}
