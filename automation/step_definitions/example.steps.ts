import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { HomePage } from '../pages/HomePage';

let homePage: HomePage;

Given('I navigate to the homepage', async function () {
  const baseURL = process.env.BASE_URL || 'http://localhost:3000';
  homePage = new HomePage(this.page);
  await homePage.navigate(baseURL);
});

Then('I should see the page title', async function () {
  const title = await homePage.getPageTitle();
  expect(title).toBeTruthy();
});

When('I search for {string}', async function (searchTerm: string) {
  await homePage.search(searchTerm);
});

Then('I should see search results', async function () {
  const resultsVisible = await homePage.areSearchResultsVisible();
  expect(resultsVisible).toBe(true);
});
