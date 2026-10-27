import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-markdown', async ({ page, mockApi }) => {
    const task = mockApi.state.tasks.find((candidate) => candidate.id === ids.todayTask)!;
    task.title = '**Важная** *задача* ~~устарела~~ [Документы](https://example.com/docs)';
    task.description = '- Первый пункт\n- *Второй* пункт [локально](/help)\n\n[опасная](javascript:alert(1))';

    // 1. Render the supported Markdown subset without turning unsafe URLs into links.
    await mockApi.open('/');

    const row = page.getByTestId('task-row').filter({ hasText: 'Важная задача' });
    await expect(row.locator('.task-title strong')).toHaveText('Важная');
    await expect(row.locator('.task-title em')).toHaveText('задача');
    await expect(row.locator('.task-title del')).toHaveText('устарела');
    const externalLink = row.locator('.task-title').getByRole('link', { name: 'Документы' });
    await expect(externalLink).toHaveAttribute('href', 'https://example.com/docs');
    await expect(externalLink).toHaveAttribute('rel', 'noopener noreferrer');
    await expect(row.locator('.task-description li')).toHaveText(['Первый пункт', 'Второй пункт локально']);
    await expect(row.locator('.task-description li').nth(1).locator('em')).toHaveText('Второй');
    await expect(row.locator('.task-description').getByRole('link', { name: 'локально' })).toHaveAttribute('href', '/help');
    await expect(row.locator('.task-description').getByRole('link', { name: 'опасная' })).toHaveCount(0);
    await expect(row.locator('.task-description')).toContainText('[опасная](javascript:alert(1))');

    // 2. Edit the raw source and save a list in the title and inline Markdown in the description.
    await row.locator('.task-title').click();
    const editor = page.getByTestId('edit-task');
    await expect(editor.getByLabel('Название задачи')).toHaveValue(task.title);
    await expect(editor.getByLabel('Описание задачи')).toHaveValue(task.description);

    const updatedTitle = '- **Первый** заголовок\n- Второй заголовок';
    const firstDescriptionItem = '  - *Курсив* и [ссылка](mailto:user@example.com)';
    const updatedDescription = `${firstDescriptionItem}\n  - **Второй** пункт`;
    await editor.getByLabel('Название задачи').fill(updatedTitle);
    const description = editor.getByLabel('Описание задачи');
    await description.fill(firstDescriptionItem);
    await expect(description).toBeFocused();
    await expect(description).toHaveCSS('outline-style', 'none');
    await description.press('End');
    await description.press('Enter');
    await expect(description).toHaveValue(`${firstDescriptionItem}\n  - `);
    await description.pressSequentially('**Второй** пункт');
    await expect(description).toHaveValue(updatedDescription);
    await description.press('Control+Enter');

    expect(mockApi.requests('PATCH', '/api/task').at(-1)?.body).toMatchObject({
      title: updatedTitle,
      description: updatedDescription
    });
    const updatedRow = page.getByTestId('task-row').filter({ hasText: 'Первый заголовок' });
    await expect(updatedRow.locator('.task-title li')).toHaveText(['Первый заголовок', 'Второй заголовок']);
    await expect(updatedRow.locator('.task-title strong')).toHaveText('Первый');
    await expect(updatedRow.locator('.task-description li')).toHaveText(['Курсив и ссылка', 'Второй пункт']);
    await expect(updatedRow.locator('.task-description em')).toHaveText('Курсив');
    await expect(updatedRow.locator('.task-description strong')).toHaveText('Второй');
    await expect(updatedRow.locator('.task-description').getByRole('link', { name: 'ссылка' }))
      .toHaveAttribute('href', 'mailto:user@example.com');

    // 3. Ctrl+Enter also creates a task while its description is focused.
    await page.keyboard.press('q');
    const creator = page.getByTestId('new-task');
    await creator.getByLabel('Название задачи').fill('Новая **Markdown** задача');
    await creator.getByLabel('Описание задачи').fill('*Создана* сочетанием клавиш');
    await creator.getByLabel('Описание задачи').press('Control+Enter');

    expect(mockApi.requests('POST', '/api/task').at(-1)?.body).toMatchObject({
      title: 'Новая **Markdown** задача',
      description: '*Создана* сочетанием клавиш'
    });
    const createdRow = page.getByTestId('task-row').filter({ hasText: 'Новая Markdown задача' });
    await expect(createdRow.locator('.task-title strong')).toHaveText('Markdown');
    await expect(createdRow.locator('.task-description em')).toHaveText('Создана');
  });
});
