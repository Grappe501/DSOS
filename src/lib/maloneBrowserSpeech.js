/**
 * Browser-native speech recognition (Web Speech API). Chrome/Edge typically supported; Firefox often not.
 * Voice Phase 3: input transport only — same Malone path as typing after transcript is submitted.
 */

/** @returns {typeof SpeechRecognition | null} */
export function getSpeechRecognitionConstructor() {
  if (typeof window === "undefined") {
    return null;
  }
  const w = window;
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

export function isBrowserSttSupported() {
  return typeof getSpeechRecognitionConstructor() === "function";
}

/**
 * @param {{ lang?: string, continuous?: boolean, interimResults?: boolean }} [options]
 * @returns {InstanceType<typeof SpeechRecognition> | null}
 */
export function createSpeechRecognition(options = {}) {
  const Ctor = getSpeechRecognitionConstructor();
  if (!Ctor) {
    return null;
  }
  const { lang = "en-US", continuous = true, interimResults = true } = options;
  const rec = new Ctor();
  rec.lang = lang;
  rec.continuous = continuous;
  rec.interimResults = interimResults;
  rec.maxAlternatives = 1;
  return rec;
}
