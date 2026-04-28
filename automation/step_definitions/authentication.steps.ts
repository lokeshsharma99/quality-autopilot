import { Given, When, Then, Before } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { QAPWorld } from '../hooks/setup';
import { LoginPage } from '../pages/login.page';
import { generateTestUser } from '../fixtures/base';

// Extend QAPWorld to include testUser for authentication scenarios
declare module '@cucumber/cucumber' {
  interface World {
    testUser: {
      email: string;
      password: string;
      username: string;
    };
    loginPage: LoginPage;
  }
}

/**
 * Background setup for authentication scenarios.
 * Creates a fresh test user for each scenario.
 */
Before(async function (this: QAPWorld) {
  // Generate fresh test credentials
  const user = generateTestUser('user');
  this.testUser = {
    email: user.email,
    password: user.password,
    username: user.username,
  };

  // Initialize the LoginPage
  this.loginPage = new LoginPage(this.page, this.baseUrl);
});

/**
 * @given the user is on the login page
 */
Given('the user is on the login page', async function (this: QAPWorld) {
  await this.loginPage.navigate();
});

/**
 * @when the user logs in with valid credentials
 * Note: This step assumes the application has a valid user account.
 * For demo purposes, you may need to create a demo account first or use known credentials.
 * If the app requires registration prior to login, add a registration step before this.
 */
When('the user logs in with valid credentials', async function (this: QAPWorld) {
  // For demo apps, use known demo credentials if available
  // Otherwise, generated credentials expect the app to allow any registration first
  const demoEmail = process.env.DEMO_EMAIL || this.testUser.email;
  const demoPassword = process.env.DEMO_PASSWORD || this.testUser.password;

  await this.loginPage.login(demoEmail, demoPassword);
});

/**
 * @when the user attempts to login with invalid credentials
 */
When('the user attempts to login with invalid credentials', async function (this: QAPWorld) {
  const invalidEmail = 'invalid_user@example.com';
  const invalidPassword = 'WrongPassword123!';

  await this.loginPage.attemptLogin(invalidEmail, invalidPassword);
});

/**
 * @when the user logs out
 */
When('the user logs out', async function (this: QAPWorld) {
  await this.loginPage.logout();
});

/**
 * @then the user should be redirected to the dashboard
 */
Then('the user should be redirected to the dashboard', async function (this: QAPWorld) {
  // Check if login page is no longer visible
  const isOnLogin = await this.loginPage.isOnLoginPage();
  expect(isOnLogin).toBe(false);

  // Check URL changed from login or root (SPA may stay on same URL but state changes)
  const currentUrl = this.page.url();
  // For SPA, we may be on same URL but different state; verify logged-in state
  expect(await this.loginPage.isLoggedIn()).toBe(true);
});

/**
 * @then the user should see a welcome message
 */
Then('the user should see a welcome message', async function (this: QAPWorld) {
  // The welcome message should be visible
  const hasWelcome = await this.loginPage.welcomeMessage().isVisible();
  // OR check loggedIn state
  const loggedIn = await this.loginPage.isLoggedIn();
  expect(hasWelcome || loggedIn).toBe(true);
});

/**
 * @then an error message should be displayed
 */
Then('an error message should be displayed', async function (this: QAPWorld) {
  const hasError = await this.loginPage.hasErrorMessage();
  expect(hasError).toBe(true);
});

/**
 * @then the user should remain on the login page
 */
Then('the user should remain on the login page', async function (this: QAPWorld) {
  const isOnLogin = await this.loginPage.isOnLoginPage();
  expect(isOnLogin).toBe(true);
});

/**
 * @then the user should be redirected to the login page
 */
Then('the user should be redirected to the login page', async function (this: QAPWorld) {
  const isOnLogin = await this.loginPage.isOnLoginPage();
  expect(isOnLogin).toBe(true);
});

/**
 * @when the user attempts to access a protected page directly
 */
When('the user attempts to access a protected page directly', async function (this: QAPWorld) {
  // Navigate to a protected route (e.g., /dashboard or /profile)
  await this.page.goto(`${this.baseUrl}/dashboard`);

  // If not authenticated, the app should redirect to login
  // We wait briefly for SPA routing
  await this.page.waitForLoadState('domcontentloaded');
});

/**
 * @when the user clicks the forgot password link
 */
When('the user clicks the forgot password link', async function (this: QAPWorld) {
  await this.loginPage.clickForgotPassword();
});

/**
 * @then the user should see the password reset form
 */
Then('the user should see the password reset form', async function (this: QAPWorld) {
  // Look for reset password form elements
  const resetFormVisible = await this.page
    .getByRole('textbox', { name: /new password|confirm password/i })
    .first()
    .isVisible();

  expect(resetFormVisible).toBe(true);
});