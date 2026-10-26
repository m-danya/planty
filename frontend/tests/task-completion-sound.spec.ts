import { expect, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-completion-sound', async ({ page, mockApi }) => {
    await page.addInitScript(() => {
      const playedSounds: string[] = [];
      Object.defineProperty(window, '__playedCompletionSounds', { value: playedSounds });
      HTMLMediaElement.prototype.play = function () {
        playedSounds.push(this.currentSrc || this.src);
        return Promise.resolve();
      };
    });
    await mockApi.open('/');

    const playedSounds = () => page.evaluate(() => (
      window as unknown as { __playedCompletionSounds: string[] }
    ).__playedCompletionSounds);

    // 1. Every bundled sound and the localized no-sound option are selectable.
    await page.getByRole('button', { name: 'Настройки профиля' }).click();
    const completionSound = page.getByLabel('Звук выполнения задачи');
    await expect(completionSound).toHaveValue('switch34');
    await expect(completionSound.locator('option')).toHaveText([
      'Без звука',
      "Kenney's switch34",
      "Kenney's switch35",
      "Kenney's switch36",
      "Kenney's glass_002",
      "HaelDB's UI #2",
      "HaelDB's UI #5",
      "HaelDB's UI #8",
      "eqylizer's high-pitched two-note",
      "ConarB13's pop",
      "Feraly's confirm",
      "PaulMorek's positive beep",
      "FunWithSound's glockenspiel success",
      "BIONN's sync blip",
      "CogFireStudios' positive blip",
      "lartti's ding click",
      "Brandon Morris's complete task"
    ]);
    await completionSound.selectOption('eqylizer_two_note');
    expect(await page.evaluate(() => localStorage.getItem('planty.completionSound'))).toBe('eqylizer_two_note');
    await page.getByRole('button', { name: 'Прослушать выбранный звук' }).click();
    await expect.poll(playedSounds).toEqual([
      'http://127.0.0.1:4173/sounds/completion/eqylizer_two_note.ogg'
    ]);

    await completionSound.selectOption('none');
    expect(await page.evaluate(() => localStorage.getItem('planty.completionSound'))).toBe('none');
    await expect(page.getByRole('button', { name: 'Прослушать выбранный звук' })).toBeDisabled();
    await page.getByRole('button', { name: 'Готово' }).click();

    // 2. No completion audio is played when the preference is disabled.
    const todayRow = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await todayRow.getByRole('button', { name: 'Выполнить задачу' }).click();
    expect(await playedSounds()).toHaveLength(1);
    await todayRow.getByRole('button', { name: 'Вернуть задачу' }).click();

    // 3. Otherwise play after completion, but not after restore or a failed request.
    await page.getByRole('button', { name: 'Настройки профиля' }).click();
    await page.getByLabel('Звук выполнения задачи').selectOption('glass_002');
    await page.getByRole('button', { name: 'Готово' }).click();
    await todayRow.getByRole('button', { name: 'Выполнить задачу' }).click();
    await expect.poll(playedSounds).toEqual([
      'http://127.0.0.1:4173/sounds/completion/eqylizer_two_note.ogg',
      'http://127.0.0.1:4173/sounds/completion/glass_002.ogg'
    ]);

    await todayRow.getByRole('button', { name: 'Вернуть задачу' }).click();
    expect(await playedSounds()).toHaveLength(2);

    mockApi.failOnce('POST', '/api/task/toggle_completed', {
      status: 503,
      detail: 'Сервис задач недоступен'
    });
    const overdueRow = page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' });
    await overdueRow.getByRole('button', { name: 'Выполнить задачу' }).click();
    await expect(page.getByRole('status')).toHaveText('Сервис задач недоступен');
    expect(await playedSounds()).toHaveLength(2);
  });
});
