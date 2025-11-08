const ACTIONS = ['add', 'remove', 'move', 'change', 'resize', 'show', 'hide'];
const TARGETS = ['text', 'image', 'button', 'section', 'card'];
const PROPS = ['color', 'size', 'position'];
const COLORS = ['red', 'blue', 'green', 'black', 'white', 'azure', 'khaki', 'tan', 'thistle'];

export function buildPhraseData(extra = []) {
  return [
    ...extra.map(phrase => ({ phrase, boost: 6.0 })),
    ...ACTIONS.map(phrase => ({ phrase, boost: 2.5 })),
    ...TARGETS.map(phrase => ({ phrase, boost: 2.0 })),
    ...PROPS.map(phrase => ({ phrase, boost: 2.0 })),
    ...COLORS.map(phrase => ({
      phrase,
      boost: ['azure', 'khaki', 'tan', 'thistle'].includes(phrase) ? 5.0 : 3.0,
    })),
  ];
}

export function tryApplyPhrases(recognition, extra = [], phraseBiasSupported) {
  if (phraseBiasSupported === false) {
    return { success: false, supported: false };
  }

  try {
    const hasProp = 'phrases' in recognition;
    const PhraseCtor = globalThis.SpeechRecognitionPhrase;

    if (!hasProp || !PhraseCtor) {
      return { success: false, supported: false };
    }

    recognition.phrases = buildPhraseData(extra).map(
      ({ phrase, boost }) => new PhraseCtor(phrase, boost),
    );

    return { success: true, supported: true };
  } catch {
    return { success: false, supported: false };
  }
}


