const AUTO_ARCHIVE_KEY = 'planty.autoArchive';

const preferences = $state({ autoArchive: true });

export function initPreferences(): void {
  preferences.autoArchive = localStorage.getItem(AUTO_ARCHIVE_KEY) !== 'false';
}

export function getAutoArchive(): boolean {
  return preferences.autoArchive;
}

export function setAutoArchive(value: boolean): void {
  preferences.autoArchive = value;
  localStorage.setItem(AUTO_ARCHIVE_KEY, String(value));
}
