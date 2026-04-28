/**
 * AUT configuration for the Quality Autopilot automation framework.
 *
 * All values read from environment variables with safe defaults.
 * Never hardcode credentials here.
 */
export const config = {
  baseUrl: process.env.BASE_URL || 'https://gds-demo-app.vercel.app',
  headless: process.env.HEADLESS !== 'false',
  browser: (process.env.BROWSER as 'chromium' | 'firefox' | 'webkit') || 'chromium',
  timeout: parseInt(process.env.TIMEOUT_MS || '30000', 10),
  auth: {
    username: process.env.AUT_AUTH_USER || '',
    password: process.env.AUT_AUTH_PASS || '',
  },
} as const;
