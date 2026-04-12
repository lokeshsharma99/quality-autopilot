import { Page } from '@playwright/test';
import { BasePage } from '../../../common/pages/BasePage';

/**
 * Home Page Object Model
 */
export class HomePage extends BasePage {
  // Locators
  private readonly searchInput = '#search-input';
  private readonly searchButton = '#search-button';
  private readonly searchResults = '.search-results';

  constructor(page: Page) {
    super(page);
  }

  /**
   * Get page title
   */
  async getPageTitle(): Promise<string> {
    return await this.page.title();
  }

  /**
   * Search for a product
   */
  async search(searchTerm: string): Promise<void> {
    await this.fill(this.searchInput, searchTerm);
    await this.click(this.searchButton);
    await this.waitForVisible(this.searchResults);
  }

  /**
   * Check if search results are visible
   */
  async areSearchResultsVisible(): Promise<boolean> {
    return await this.isVisible(this.searchResults);
  }
}
