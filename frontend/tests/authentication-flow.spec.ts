import { expect, test } from './fixtures';

test.describe('Authentication', () => {
  test('authentication-flow', async ({ page, mockApi }) => {
    // 1. Open the login page as a logged-out user and reject credentials.
    mockApi.state.authenticated = false;
    mockApi.failOnce('POST', '/api/auth/login', {
      status: 400,
      detail: 'LOGIN_BAD_CREDENTIALS'
    });
    await mockApi.open('/');
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole('heading', { name: 'С возвращением' })).toBeVisible();

    await page.getByLabel('Электронная почта').fill('new@example.ru');
    await page.getByLabel('Пароль').fill('password123');
    await page.getByRole('button', { name: 'Войти' }).click();
    await expect(page.getByRole('alert')).toHaveText('Неверный адрес электронной почты или пароль');
    await expect(page).toHaveURL(/\/login$/);

    // 2. Register and log in through the same form.
    await page.getByRole('button', { name: 'Создать аккаунт' }).click();
    await expect(page.getByRole('heading', { name: 'Создать аккаунт' })).toBeVisible();
    await page.getByRole('button', { name: 'Зарегистрироваться' }).click();

    await expect(page.getByRole('heading', { name: '📥 Входящие' })).toBeVisible();
    expect(mockApi.requests('POST', '/api/auth/register').at(-1)?.body).toEqual({
      email: 'new@example.ru',
      password: 'password123'
    });
    expect(mockApi.requests('POST', '/api/auth/login').at(-1)?.body).toEqual({
      username: 'new@example.ru',
      password: 'password123'
    });

    // 3. Log out and verify that authenticated visitors cannot stay on login.
    await page.getByRole('button', { name: 'Выйти' }).click();
    await expect(page).toHaveURL(/\/login$/);
    expect(mockApi.state.authenticated).toBe(false);

    mockApi.state.authenticated = true;
    await page.goto('/login');
    await expect(page).toHaveURL(/\/?(?:\?section=.*)?$/);
    await expect(page.getByRole('heading', { name: '📥 Входящие' })).toBeVisible();
  });
});
