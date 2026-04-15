import type { Message } from "./types";

type BrowserAudioContext = AudioContext & {
  createBiquadFilter: () => BiquadFilterNode;
};

type WindowWithAudioContext = Window & {
  AudioContext?: typeof AudioContext;
  webkitAudioContext?: typeof AudioContext;
};

let notificationAudioContext: BrowserAudioContext | null = null;
let unlockInstalled = false;

export function countAssistantMessages(messages: Message[]): number {
  return messages.reduce(
    (count, msg) => count + (msg.role === "assistant" ? 1 : 0),
    0,
  );
}

function getAudioContextCtor(): typeof AudioContext | undefined {
  const browserWindow = window as WindowWithAudioContext;
  return browserWindow.AudioContext || browserWindow.webkitAudioContext;
}

function getNotificationAudioContext(): BrowserAudioContext | null {
  const AudioContextCtor = getAudioContextCtor();
  if (!AudioContextCtor) {
    return null;
  }
  if (!notificationAudioContext) {
    notificationAudioContext = new AudioContextCtor() as BrowserAudioContext;
  }
  return notificationAudioContext;
}

function detachUnlockListeners(unlockAudio: () => void): void {
  document.removeEventListener("pointerdown", unlockAudio, true);
  document.removeEventListener("keydown", unlockAudio, true);
  document.removeEventListener("touchstart", unlockAudio, true);
}

export function ensureNotificationAudioUnlocked(): void {
  if (unlockInstalled) {
    return;
  }
  unlockInstalled = true;

  const unlockAudio = () => {
    const audioContext = getNotificationAudioContext();
    if (!audioContext) {
      detachUnlockListeners(unlockAudio);
      return;
    }

    void audioContext.resume().then(() => {
      if (audioContext.state === "running") {
        detachUnlockListeners(unlockAudio);
      }
    }).catch(() => {
      // Keep listeners installed so the next user gesture can retry.
    });
  };

  document.addEventListener("pointerdown", unlockAudio, true);
  document.addEventListener("keydown", unlockAudio, true);
  document.addEventListener("touchstart", unlockAudio, true);
}

function triggerSoftChime(audioContext: BrowserAudioContext): void {
  const startTime = audioContext.currentTime;
  const mainOscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();

  mainOscillator.type = "sine";

  mainOscillator.frequency.setValueAtTime(1420, startTime);
  mainOscillator.frequency.exponentialRampToValueAtTime(1180, startTime + 0.08);

  gain.gain.setValueAtTime(0.0001, startTime);
  gain.gain.linearRampToValueAtTime(0.018, startTime + 0.004);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.11);

  mainOscillator.connect(gain);
  gain.connect(audioContext.destination);

  mainOscillator.start(startTime);
  mainOscillator.stop(startTime + 0.12);
}

export function playNotificationSound(): void {
  const audioContext = getNotificationAudioContext();
  if (!audioContext) {
    return;
  }

  if (audioContext.state === "running") {
    triggerSoftChime(audioContext);
    return;
  }

  void audioContext.resume().then(() => {
    if (audioContext.state === "running") {
      triggerSoftChime(audioContext);
    }
  }).catch(() => {
    // Browser autoplay restrictions are expected until the user interacts.
  });
}
