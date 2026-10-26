const AUTO_ARCHIVE_KEY = 'planty.autoArchive';
const COMPLETION_SOUND_KEY = 'planty.completionSound';
const SECTION_LAYOUTS_KEY = 'planty.sectionLayouts';
const SECTION_EXPANSION_KEY = 'planty.sectionExpansion';

export type SectionLayout = 'subsections' | 'board';

export const COMPLETION_SOUNDS = [
  { id: 'switch34', label: "Kenney's switch34", src: '/sounds/completion/switch34.ogg' },
  { id: 'switch35', label: "Kenney's switch35", src: '/sounds/completion/switch35.ogg' },
  { id: 'switch36', label: "Kenney's switch36", src: '/sounds/completion/switch36.ogg' },
  { id: 'glass_002', label: "Kenney's glass_002", src: '/sounds/completion/glass_002.ogg' },
  { id: 'haeldb_ui_2', label: "HaelDB's UI #2", src: '/sounds/completion/haeldb_ui_2.ogg' },
  { id: 'haeldb_ui_5', label: "HaelDB's UI #5", src: '/sounds/completion/haeldb_ui_5.ogg' },
  { id: 'haeldb_ui_8', label: "HaelDB's UI #8", src: '/sounds/completion/haeldb_ui_8.ogg' },
  {
    id: 'eqylizer_two_note',
    label: "eqylizer's high-pitched two-note",
    src: '/sounds/completion/eqylizer_two_note.ogg'
  },
  { id: 'conarb13_pop', label: "ConarB13's pop", src: '/sounds/completion/conarb13_pop.ogg' },
  { id: 'feraly_confirm', label: "Feraly's confirm", src: '/sounds/completion/feraly_confirm.ogg' },
  {
    id: 'paulmorek_beep_05_positive',
    label: "PaulMorek's positive beep",
    src: '/sounds/completion/paulmorek_beep_05_positive.ogg'
  },
  {
    id: 'funwithsound_success_glockenspiel',
    label: "FunWithSound's glockenspiel success",
    src: '/sounds/completion/funwithsound_success_glockenspiel.ogg'
  },
  { id: 'bionn_sync_blip', label: "BIONN's sync blip", src: '/sounds/completion/bionn_sync_blip.ogg' },
  {
    id: 'cogfirestudios_positive_blip',
    label: "CogFireStudios' positive blip",
    src: '/sounds/completion/cogfirestudios_positive_blip.ogg'
  },
  { id: 'lartti_ding_click', label: "lartti's ding click", src: '/sounds/completion/lartti_ding_click.ogg' },
  {
    id: 'brandon_complete',
    label: "Brandon Morris's complete task",
    src: '/sounds/completion/brandon_complete.ogg'
  }
] as const;

export type CompletionSoundId = 'none' | typeof COMPLETION_SOUNDS[number]['id'];

const DEFAULT_COMPLETION_SOUND: CompletionSoundId = 'switch34';
const preferences = $state<{ autoArchive: boolean; completionSound: CompletionSoundId }>({
  autoArchive: true,
  completionSound: DEFAULT_COMPLETION_SOUND
});

function isCompletionSoundId(value: string | null): value is CompletionSoundId {
  return value === 'none' || COMPLETION_SOUNDS.some((sound) => sound.id === value);
}

export function initPreferences(): void {
  preferences.autoArchive = localStorage.getItem(AUTO_ARCHIVE_KEY) !== 'false';
  const completionSound = localStorage.getItem(COMPLETION_SOUND_KEY);
  preferences.completionSound = isCompletionSoundId(completionSound) ? completionSound : DEFAULT_COMPLETION_SOUND;
}

export function getAutoArchive(): boolean {
  return preferences.autoArchive;
}

export function setAutoArchive(value: boolean): void {
  preferences.autoArchive = value;
  localStorage.setItem(AUTO_ARCHIVE_KEY, String(value));
}

export function getCompletionSound(): CompletionSoundId {
  return preferences.completionSound;
}

export function setCompletionSound(value: CompletionSoundId): void {
  preferences.completionSound = value;
  localStorage.setItem(COMPLETION_SOUND_KEY, value);
}

export function playCompletionSound(): void {
  const sound = COMPLETION_SOUNDS.find((candidate) => candidate.id === preferences.completionSound);
  if (!sound) return;
  void new Audio(sound.src).play().catch(() => undefined);
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
