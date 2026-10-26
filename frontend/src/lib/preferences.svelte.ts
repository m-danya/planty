const AUTO_ARCHIVE_KEY = 'planty.autoArchive';
const SECTION_LAYOUTS_KEY = 'planty.sectionLayouts';
const SECTION_EXPANSION_KEY = 'planty.sectionExpansion';

export type SectionLayout = 'subsections' | 'board';

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

function storedRecord<T>(key: string, isValue: (value: unknown) => value is T): Record<string, T> {
  try {
    const value = JSON.parse(localStorage.getItem(key) ?? '{}') as unknown;
    if (!value || typeof value !== 'object' || Array.isArray(value)) return {};
    return Object.fromEntries(
      Object.entries(value).filter((entry): entry is [string, T] => isValue(entry[1]))
    );
  } catch {
    return {};
  }
}

function sectionLayouts(): Record<string, SectionLayout> {
  return storedRecord(SECTION_LAYOUTS_KEY, (value): value is SectionLayout =>
    value === 'subsections' || value === 'board'
  );
}

export function getSectionLayout(sectionId: string): SectionLayout {
  return sectionLayouts()[sectionId] ?? 'subsections';
}

export function setSectionLayout(sectionId: string, layout: SectionLayout): void {
  localStorage.setItem(SECTION_LAYOUTS_KEY, JSON.stringify({ ...sectionLayouts(), [sectionId]: layout }));
}

function sectionExpansion(): Record<string, boolean> {
  return storedRecord(SECTION_EXPANSION_KEY, (value): value is boolean => typeof value === 'boolean');
}

export function getSectionExpanded(sectionId: string): boolean {
  return sectionExpansion()[sectionId] ?? true;
}

export function setSectionExpanded(sectionId: string, expanded: boolean): void {
  localStorage.setItem(SECTION_EXPANSION_KEY, JSON.stringify({ ...sectionExpansion(), [sectionId]: expanded }));
}
