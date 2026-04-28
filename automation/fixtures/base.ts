/**
 * Test data factory types for Quality Autopilot automation framework.
 *
 * All PII fields use synthetic data (no real user data).
 * Generated users are unique per test run to prevent collisions.
 */

export interface TestUser {
  username: string;
  email: string;       // synthetic, unique per run
  password: string;
  role: 'admin' | 'user' | 'guest';
}

export interface RunContext {
  ticketId: string;
  testUsers: TestUser[];
  environment: string;
  baseUrl: string;
}

/** Generate a synthetic, unique email for test isolation. */
export function generateTestEmail(prefix: string = 'test'): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 9999);
  return `${prefix}.${timestamp}.${random}@qap.test`;
}

/** Generate a synthetic test user. */
export function generateTestUser(role: TestUser['role'] = 'user'): TestUser {
  const timestamp = Date.now();
  return {
    username: `qap_user_${timestamp}`,
    email: generateTestEmail(role),
    password: `QAP_Test_${timestamp}!`,
    role,
  };
}
