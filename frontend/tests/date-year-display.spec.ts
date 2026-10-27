import { expect, ids, test } from './fixtures';

test.describe('Dates', () => {
  test('date-year-display', async ({ page, mockApi }) => {
    await page.clock.setFixedTime(new Date('2026-12-15T12:00:00+03:00'));
    const template = mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)!;
    mockApi.state.tasks.push(
      {
        ...template,
        id: '10000000-0000-4000-8000-000000000091',
        parent_task_id: null,
        title: 'Дата этого года',
        description: null,
        due_to: '2026-03-26'
      },
      {
        ...template,
        id: '10000000-0000-4000-8000-000000000092',
        parent_task_id: null,
        title: 'Дата прошлого года',
        description: null,
        due_to: '2025-03-26'
      },
      {
        ...template,
        id: '10000000-0000-4000-8000-000000000093',
        parent_task_id: null,
        title: 'Дата декабря',
        description: null,
        due_to: '2026-12-20'
      },
      {
        ...template,
        id: '10000000-0000-4000-8000-000000000094',
        parent_task_id: null,
        title: 'Дата января',
        description: null,
        due_to: '2027-01-10'
      }
    );

    // 1. Absolute task dates show a year only outside the current year.
    await mockApi.open('/');
    const currentYear = page.getByTestId('task-row').filter({ hasText: 'Дата этого года' });
    const previousYear = page.getByTestId('task-row').filter({ hasText: 'Дата прошлого года' });
    await expect(currentYear.locator('.task-date')).toHaveText('26 марта');
    await expect(previousYear.locator('.task-date')).toHaveText('26 марта 2025');

    // 2. Calendar headings follow the same rule across New Year.
    await page.getByRole('button', { name: 'Календарь' }).click();
    const december = page.getByTestId('calendar-date-group').filter({ hasText: 'Дата декабря' });
    const january = page.getByTestId('calendar-date-group').filter({ hasText: 'Дата января' });
    await expect(december.getByRole('heading')).not.toContainText('2026');
    await expect(december.getByRole('heading')).toContainText('20 декабря');
    await expect(january.getByRole('heading')).toContainText('10 января 2027');
  });
});
