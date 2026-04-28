import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

/**
 * LoginPage — Page Object Model for the authentication page.
 *
 * Locator strategy priority:
 * 1. data-testid (preferred)
 * 2. role (button, textbox, checkbox)
 * 3. aria-label / aria-labelledby
 * 4. placeholder
 * 5. label text
 * 6. visible text (last resort)
 *
 * This page handles user authentication for the Universal Credit application.
 */
export class LoginPage extends BasePage {
  // ---------------------------------------------------------------------------
  // Locators — Email / Username field
  // ---------------------------------------------------------------------------
  /**
   * Priority order:
   * 1. data-testid (common patterns)
   * 2. role with accessible name
   * 3. aria-label / aria-labelledby
   * 4. placeholder attribute
   * 5. label text
   * 6. CSS selector (last resort)
   */
  private readonly emailInput = () =>
    // 1. data-testid patterns (common naming)
    this.byTestId('email') ||
    this.byTestId('login-email') ||
    this.byTestId('username') ||
    this.byTestId('login-username') ||
    // 2. role + name (covers label text and aria-label)
    this.page.getByRole('textbox', { name: /email|username|user/i }) ||
    // 3. explicit label with for attribute
    this.page.getByLabel(/email|username|user/i) ||
    // 4. placeholder text
    this.page.getByPlaceholder(/email|username|user/i) ||
    // 5. CSS fallbacks
    this.page.locator('input[type="email"], input[name*="email"], input[name*="username"], input[id*="email"], input[id*="username"]');

  // ---------------------------------------------------------------------------
  // Locators — Password field
  // ---------------------------------------------------------------------------
  /**
   * Priority order:
   * 1. data-testid
   * 2. role
   * 3. label
   * 4. placeholder
   * 5. CSS fallback
   */
  private readonly passwordInput = () =>
    // 1. data-testid patterns
    this.byTestId('password') ||
    this.byTestId('login-password') ||
    this.byTestId('pwd') ||
    // 2. role + name
    this.page.getByRole('textbox', { name: /password/i }) ||
    // 3. label association
    this.page.getByLabel(/password/i) ||
    // 4. placeholder
    this.page.getByPlaceholder(/password/i) ||
    // 5. CSS fallback
    this.page.locator('input[type="password"], input[name*="password"], input[id*="password"]');

  // ---------------------------------------------------------------------------
  // Locators — Submit button
  // ---------------------------------------------------------------------------
  /**
   * Priority order:
   * 1. data-testid
   * 2. role (button)
   * 3. text content
   * 4. CSS fallback
   */
  private readonly submitButton = () =>
    // 1. data-testid patterns
    this.byTestId('submit') ||
    this.byTestId('login-submit') ||
    this.byTestId('signin') ||
    this.byTestId('login-button') ||
    // 2. button role with accessible name
    this.page.getByRole('button', { name: /sign in|log in|login|submit/i }) ||
    // 3. text content (exact or partial)
    this.page.getByText(/sign in|log in|login|signin|submit/i, { exact: false }) ||
    // 4. CSS fallback
    this.page.locator('button[type="submit"], input[type="submit"], button:has-text("Sign in"), button:has-text("Log in")');

  // ---------------------------------------------------------------------------
  // Locators — Error message container
  // ---------------------------------------------------------------------------
  /**
   * Priority order:
   * 1. data-testid with error patterns
   * 2. role="alert"
   * 3. CSS class patterns
   */
  private readonly errorMessage = () =>
    // 1. data-testid patterns
    this.byTestId('error') ||
    this.byTestId('login-error') ||
    this.byTestId('error-message') ||
    // 2. ARIA role alert
    this.page.getByRole('alert') ||
    // 3. CSS selectors and data attributes
    this.page.locator('[role="alert"], .error-message, .error, .alert-danger, .alert, [data-testid*="error"], [class*="error"]');

  // ---------------------------------------------------------------------------
  // Locators — Welcome message after login
  // ---------------------------------------------------------------------------
  /**
   * Priority order:
   * 1. data-testid
   * 2. visible text
   * 3. CSS fallback
   */
  private readonly welcomeMessage = () =>
    // 1. data-testid patterns
    this.byTestId('welcome') ||
    this.byTestId('welcome-message') ||
    this.byTestId('user-greeting') ||
    // 2. hello, username etc
    this.page.getByText(/welcome|hello|hi|sign in successful|logged in/i, { exact: false }) ||
    // 3. CSS fallback
    this.page.locator('.welcome-message, .welcome, .greeting, [data-testid*="welcome"]');

  // ---------------------------------------------------------------------------
  // Locators — Logout button
  // ---------------------------------------------------------------------------
  /**
   * Priority order:
   * 1. data-testid
   * 2. role (button or link)
   * 3. visible text
   * 4. CSS fallback
   */
  private readonly logoutButton = () =>
    // 1. data-testid patterns
    this.byTestId('logout') ||
    this.byTestId('logout-button') ||
    this.byTestId('signout') ||
    // 2. button/link role with name
    this.page.getByRole('button', { name: /logout|sign out|log out|signout/i }) ||
    this.page.getByRole('link', { name: /logout|sign out|log out/i }) ||
    // 3. text content
    this.page.getByText(/logout|sign out|log out|signout/i, { exact: false }) ||
    // 4. CSS fallback
    this.page.locator('a[href*="logout"], a[href*="signout"], button[data-testid*="logout"], button[data-testid*="signout"], a:has-text("Log out"), a:has-text("Sign out"), button:has-text("Log out")');

  // ---------------------------------------------------------------------------
  // Locators — Forgot password link
  // ---------------------------------------------------------------------------
  /**
   * Priority order:
   * 1. data-testid
   * 2. role (link)
   * 3. text content
   * 4. CSS fallback
   */
  private readonly forgotPasswordLink = () =>
    // 1. data-testid patterns
    this.byTestId('forgot-password') ||
    this.byTestId('forgotPassword') ||
    this.byTestId('reset-password') ||
    // 2. link role with name
    this.page.getByRole('link', { name: /forgot password|reset password|forgotten password/i }) ||
    // 3. text content
    this.page.getByText(/forgot password|reset password|forgotten password/i, { exact: false }) ||
    // 4. CSS fallback
    this.page.locator('a[href*="forgot"], a[href*="reset"], a:has-text("Forgot password"), a:has-text("Reset password")');

  constructor(page: Page, baseUrl: string) {
    super(page, baseUrl);
  }

  /**
   * Navigate to the login page.
   * The app uses client-side routing, so we navigate to baseUrl and the login component is rendered on the landing page.
   */
  async navigate(): Promise<void> {
    await this.page.goto(this.baseUrl);
    // Wait for the page to load and for the React app to render the login form
    await this.page.waitForLoadState('domcontentloaded');
    // Wait for the email input to be visible, indicating the login component is rendered
    try {
      await expect(this.emailInput()).toBeVisible({ timeout: 10000 });
    } catch (error) {
      // If the email input is not found or not visible, the page might be different
      console.warn('Login page email input not immediately visible - page may have different structure');
    }
  }

  /**
   * Perform login with provided credentials.
   */
  async login(email: string, password: string): Promise<void> {
    await this.emailInput().fill(email);
    await this.passwordInput().fill(password);
    await this.submitButton().click();
    // Wait for navigation or state change after login
    await this.waitForLoad();
  }

  /**
   * Attempt login with credentials that are expected to fail.
   */
  async attemptLogin(email: string, password: string): Promise<void> {
    await this.emailInput().fill(email);
    await this.passwordInput().fill(password);
    await this.submitButton().click();
    // Do not wait for full load - we expect to stay on the page with error
    await this.page.waitForLoadState('domcontentloaded');
  }

  /**
   * Check if the login page is currently displayed.
   */
  async isOnLoginPage(): Promise<boolean> {
    try {
      // Check for presence of email/password fields or login button
      const emailVisible = await this.emailInput().isVisible();
      const passwordVisible = await this.passwordInput().isVisible();
      const submitVisible = await this.submitButton().isVisible();
      return emailVisible && passwordVisible && submitVisible;
    } catch {
      return false;
    }
  }

  /**
   * Check if an error message is displayed after failed login.
   */
  async hasErrorMessage(): Promise<boolean> {
    try {
      const errorEl = this.errorMessage();
      const isVisible = await errorEl.isVisible();
      const hasText = (await errorEl.textContent())?.trim().length > 0;
      return isVisible && hasText;
    } catch {
      return false;
    }
  }

  /**
   * Get the error message text.
   */
  async getErrorMessage(): Promise<string> {
    try {
      return (await this.errorMessage().textContent())?.trim() || '';
    } catch {
      return '';
    }
  }

  /**
   * Check if the user is logged in (welcome message or logout button present).
   */
  async isLoggedIn(): Promise<boolean> {
    try {
      // Check for logout button or welcome message
      const logoutVisible = await this.logoutButton().isVisible();
      const welcomeVisible = await this.welcomeMessage().isVisible();
      return logoutVisible || welcomeVisible;
    } catch {
      return false;
    }
  }

  /**
   * Log out the current user.
   */
  async logout(): Promise<void> {
    await this.logoutButton().click();
    await this.waitForLoad();
  }

  /**
   * Click the forgot password link.
   */
  async clickForgotPassword(): Promise<void> {
    await this.forgotPasswordLink().click();
  }
}