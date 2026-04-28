import { Before, After, World, setWorldConstructor, IWorldOptions } from '@cucumber/cucumber';
import { Browser, BrowserContext, Page, chromium, firefox } from '@playwright/test';

// ---------------------------------------------------------------------------
// World
// ---------------------------------------------------------------------------
export class QAPWorld extends World {
  browser!: Browser;
  context!: BrowserContext;
  page!: Page;
  baseUrl: string;
  headless: boolean;
  browserName: string;

  constructor(options: IWorldOptions) {
    super(options);
    this.baseUrl = (options.parameters as Record<string, unknown>).baseUrl as string || 'https://gds-demo-app.vercel.app';
    this.headless = (options.parameters as Record<string, unknown>).headless as boolean ?? true;
    this.browserName = (options.parameters as Record<string, unknown>).browser as string || 'chromium';
  }
}

setWorldConstructor(QAPWorld);

// ---------------------------------------------------------------------------
// Lifecycle hooks
// ---------------------------------------------------------------------------
Before(async function (this: QAPWorld) {
  const launchOptions = { headless: this.headless };

  if (this.browserName === 'firefox') {
    this.browser = await firefox.launch(launchOptions);
  } else {
    this.browser = await chromium.launch(launchOptions);
  }

  this.context = await this.browser.newContext({
    baseURL: this.baseUrl,
    viewport: { width: 1280, height: 720 },
  });

  this.page = await this.context.newPage();
});

After(async function (this: QAPWorld, scenario) {
  // Capture screenshot on failure
  if (scenario.result?.status === 'FAILED') {
    const screenshot = await this.page.screenshot({ fullPage: true });
    this.attach(screenshot, 'image/png');
  }

  await this.page.close();
  await this.context.close();
  await this.browser.close();
});
