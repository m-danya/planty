export type Locale = 'ru' | 'en';

const messages = {
  ru: {
    search: 'Поиск', calendar: 'Календарь', archive: 'Архив', sections: 'Разделы', logout: 'Выйти',
    settings: 'Настройки профиля', language: 'Язык интерфейса', russian: 'Русский', english: 'Английский', done: 'Готово',
    autoArchive: 'Автоматически переносить выполненные задачи в архив',
    todoistImport: 'Импорт из Todoist', todoistImportHint: 'Выберите ZIP-архив резервной копии Todoist.',
    chooseTodoistBackup: 'Выбрать архив Todoist', eraseCurrentData: 'Стереть все текущие данные',
    importTodoist: 'Импортировать данные из Todoist', importing: 'Импортируем…',
    todoistImported: 'Импортировано проектов: {projects}, задач: {tasks}', todoistImportFailed: 'Не удалось импортировать архив Todoist',
    addSection: 'Добавить раздел', closeMenu: 'Закрыть меню', closeSidebar: 'Закрыть боковую панель',
    tasks: 'Задачи', task_one: 'задача', task_few: 'задачи', task_many: 'задач',
    loading: 'Загрузка', openMenu: 'Открыть меню', addTask: 'Добавить задачу',
    searchTasks: 'Поиск по задачам', nothingFound: 'Ничего не найдено', overdue: 'Просрочено',
    noMonthTasks: 'На ближайший месяц задач нет.', archiveEmpty: 'Архив пуст',
    createSectionFirst: 'Создайте раздел, чтобы добавить первую задачу.',
    moveTask: 'Переместить задачу', newSection: 'Новый раздел', parentSection: 'Родительский раздел',
    topLevel: 'Верхний уровень', cancel: 'Отмена', move: 'Переместить', save: 'Сохранить', delete: 'Удалить',
    rename: 'Переименовать', deleteSection: 'Удалить раздел?', renameSection: 'Переименовать раздел',
    moveSection: 'Переместить раздел', sectionName: 'Название',
    deleteSectionHint: 'Можно удалить только пустой раздел без подразделов. Это действие нельзя отменить.',
    taskTitle: 'Название задачи', taskPlaceholder: 'Что нужно сделать? Например: позвонить завтра',
    description: 'Описание', taskDescription: 'Описание задачи', moreOptions: 'Дополнительные параметры',
    flag: 'Флаг', taskSection: 'Раздел задачи', dismiss: 'Отменить', saveTask: 'Сохранить задачу',
    dateDetails: 'Параметры срока', dueDate: 'Дата', dueTime: 'Время', repeat: 'Повторение', schedule: 'Расчёт следующей даты',
    fixedSchedule: 'По расписанию — от предыдущего срока', flexibleSchedule: 'Гибко — от дня выполнения',
    noRepeat: 'Не повторяется', sourcePhrase: 'Распознанная фраза', flexibleHelp: 'Поставьте ! после слова «каждый», например «каждый! день», чтобы отсчитывать новый срок от дня выполнения.',
    sectionSuggestions: 'Разделы', selectSectionHint: 'Введите # или № и начало названия раздела',
    dragTask: 'Перетащить задачу', expandSubtasks: 'Раскрыть подзадачи', collapseSubtasks: 'Свернуть подзадачи',
    restoreTask: 'Вернуть задачу', completeTask: 'Выполнить задачу', otherSection: 'В другой раздел',
    addSubtask: 'Создать подзадачу', restoreArchive: 'Вернуть из архива', toArchive: 'В архив',
    dragSection: 'Перетащить раздел', today: 'Сегодня', tomorrow: 'Завтра',
    assignTo: 'Назначить на:', todayLower: 'сегодня', tomorrowLower: 'завтра',
    assignOtherDay: 'Назначить на другой день', chooseDueDate: 'Выбрать дату', taskScheduled: 'Срок задачи изменён',
    previousMonth: 'Предыдущий месяц', nextMonth: 'Следующий месяц', closeCalendar: 'Закрыть календарь',
    login: 'Войти', register: 'Зарегистрироваться', registration: 'Регистрация', signIn: 'Вход',
    welcome: 'С возвращением', createAccount: 'Создать аккаунт', email: 'Электронная почта', password: 'Пароль', wait: 'Подождите…',
    loginSubtitle: 'Войдите, чтобы продолжить работу', registerSubtitle: 'Начните наводить порядок в делах',
    haveAccount: 'У меня уже есть аккаунт', brandLine: 'Спокойное место для задач, планов и всего, что хочется успеть.',
    invalidCredentials: 'Неверный адрес электронной почты или пароль', serverUnavailable: 'Не удалось связаться с сервером',
    somethingWrong: 'Что-то пошло не так', loadFailed: 'Не удалось загрузить данные', taskSaved: 'Задача сохранена',
    taskArchived: 'Задача перемещена в архив', taskMoved: 'Задача перемещена', sectionMoved: 'Раздел перемещён',
    sectionSaved: 'Раздел сохранён', sectionDeleted: 'Раздел удалён', deleteTaskPrompt: 'Удалить задачу',
    cannotNestTask: 'Нельзя перенести задачу внутрь её подзадачи', cannotNestSection: 'Нельзя перенести раздел внутрь его подраздела'
  },
  en: {
    search: 'Search', calendar: 'Calendar', archive: 'Archive', sections: 'Sections', logout: 'Log out',
    settings: 'Profile settings', language: 'Interface language', russian: 'Russian', english: 'English', done: 'Done',
    autoArchive: 'Automatically move completed tasks to the archive',
    todoistImport: 'Import from Todoist', todoistImportHint: 'Choose a Todoist backup ZIP archive.',
    chooseTodoistBackup: 'Choose Todoist backup', eraseCurrentData: 'Erase all current data',
    importTodoist: 'Import data from Todoist', importing: 'Importing…',
    todoistImported: 'Imported projects: {projects}, tasks: {tasks}', todoistImportFailed: 'Could not import the Todoist backup',
    addSection: 'Add section', closeMenu: 'Close menu', closeSidebar: 'Close sidebar',
    tasks: 'Tasks', task_one: 'task', task_few: 'tasks', task_many: 'tasks', loading: 'Loading',
    openMenu: 'Open menu', addTask: 'Add task', searchTasks: 'Search tasks', nothingFound: 'Nothing found',
    overdue: 'Overdue', noMonthTasks: 'No tasks in the next month.', archiveEmpty: 'Archive is empty',
    createSectionFirst: 'Create a section to add your first task.', moveTask: 'Move task', newSection: 'New section',
    parentSection: 'Parent section', topLevel: 'Top level', cancel: 'Cancel', move: 'Move', save: 'Save', delete: 'Delete',
    rename: 'Rename', deleteSection: 'Delete section?', renameSection: 'Rename section', moveSection: 'Move section',
    sectionName: 'Name', deleteSectionHint: 'Only an empty section without subsections can be deleted. This cannot be undone.',
    taskTitle: 'Task name', taskPlaceholder: 'What needs doing? For example: call tomorrow', description: 'Description',
    taskDescription: 'Task description', moreOptions: 'More options', flag: 'Flag', taskSection: 'Task section',
    dismiss: 'Cancel', saveTask: 'Save task', dateDetails: 'Due date details', dueDate: 'Date', dueTime: 'Time', repeat: 'Repeat',
    schedule: 'Next date calculation', fixedSchedule: 'Fixed — from the previous due date',
    flexibleSchedule: 'Flexible — from completion day', noRepeat: 'Does not repeat', sourcePhrase: 'Recognized phrase',
    flexibleHelp: 'Add ! after “every”, for example “every! day”, to count the next due date from completion day.',
    sectionSuggestions: 'Sections', selectSectionHint: 'Type # or № and the beginning of a section name', dragTask: 'Drag task',
    expandSubtasks: 'Expand subtasks', collapseSubtasks: 'Collapse subtasks', restoreTask: 'Restore task',
    completeTask: 'Complete task', otherSection: 'Move to another section', addSubtask: 'Create subtask',
    restoreArchive: 'Restore from archive', toArchive: 'Archive', dragSection: 'Drag section', today: 'Today', tomorrow: 'Tomorrow',
    assignTo: 'Schedule for:', todayLower: 'today', tomorrowLower: 'tomorrow',
    assignOtherDay: 'Schedule for another day', chooseDueDate: 'Choose date', taskScheduled: 'Task due date changed',
    previousMonth: 'Previous month', nextMonth: 'Next month', closeCalendar: 'Close calendar',
    login: 'Log in', register: 'Register', registration: 'Registration', signIn: 'Sign in', welcome: 'Welcome back',
    createAccount: 'Create account', email: 'Email', password: 'Password', wait: 'Please wait…', loginSubtitle: 'Sign in to continue',
    registerSubtitle: 'Start getting your work organized', haveAccount: 'I already have an account',
    brandLine: 'A calm place for tasks, plans, and everything you want to get done.',
    invalidCredentials: 'Invalid email or password', serverUnavailable: 'Could not reach the server',
    somethingWrong: 'Something went wrong', loadFailed: 'Could not load data', taskSaved: 'Task saved',
    taskArchived: 'Task moved to archive', taskMoved: 'Task moved', sectionMoved: 'Section moved',
    sectionSaved: 'Section saved', sectionDeleted: 'Section deleted', deleteTaskPrompt: 'Delete task',
    cannotNestTask: 'A task cannot be moved into its own subtask', cannotNestSection: 'A section cannot be moved into its own subsection'
  }
} as const;

export type MessageKey = keyof typeof messages.ru;
const language = $state<{ locale: Locale }>({ locale: 'ru' });

export function initLocale(): void {
  const saved = localStorage.getItem('planty.locale');
  language.locale = saved === 'en' ? 'en' : 'ru';
  document.documentElement.lang = language.locale;
}

export function setLocale(locale: Locale): void {
  language.locale = locale;
  localStorage.setItem('planty.locale', locale);
  document.documentElement.lang = locale;
}

export function getLocale(): Locale {
  return language.locale;
}

export function t(key: MessageKey): string {
  return messages[language.locale][key];
}

export function localizedError(message: string, fallback: string): string {
  if (language.locale === 'en') return message;
  return /[а-яё]/iu.test(message) ? message : fallback;
}

export function taskCountLabel(count: number): string {
  if (language.locale === 'en') return `${count} ${count === 1 ? 'task' : 'tasks'}`;
  const mod10 = count % 10;
  const mod100 = count % 100;
  const word = mod10 === 1 && mod100 !== 11 ? messages.ru.task_one
    : mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14) ? messages.ru.task_few
    : messages.ru.task_many;
  return `${count} ${word}`;
}

export function localizedSectionTitle(title: string): string {
  if (language.locale === 'ru') return title.replace(/\bInbox\b/u, 'Входящие');
  return title.replace(/Входящие/gu, 'Inbox');
}
