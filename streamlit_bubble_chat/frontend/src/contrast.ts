/* ─── Auto-contrast (APCA — Accessible Perceptual Contrast Algorithm) ─── */
/*
 * Inline implementation of APCA 0.0.98G-4g (W3 Licensed).
 * APCA is a perceptual contrast algorithm that accounts for the
 * asymmetry between dark-on-light and light-on-dark text, producing
 * correct contrast values across any theme without theme detection.
 *
 * Reference: https://github.com/Myndex/apca-w3
 * Constants: SA98G group "G-4g", monitor exponent 2.4
 */

/** Linearize an sRGB 0-255 channel and compute luminance Y. */
function sRGBtoY(r: number, g: number, b: number): number {
  const f = (c: number) => Math.pow(c / 255, 2.4);
  return 0.2126729 * f(r) + 0.7151522 * f(g) + 0.0721750 * f(b);
}

/** APCA contrast (Lc) — text Y vs background Y.  Returns signed float. */
function apcaLc(txtY: number, bgY: number): number {
  const blkThrs = 0.022, blkClmp = 1.414;

  // Soft-clamp near-black
  txtY = txtY > blkThrs ? txtY : txtY + Math.pow(blkThrs - txtY, blkClmp);
  bgY  = bgY  > blkThrs ? bgY  : bgY  + Math.pow(blkThrs - bgY,  blkClmp);

  if (Math.abs(bgY - txtY) < 0.0005) return 0;

  let sapc: number;
  if (bgY > txtY) {
    // Normal polarity: dark text on light bg (BoW) → positive
    sapc = (Math.pow(bgY, 0.56) - Math.pow(txtY, 0.57)) * 1.14;
    return sapc < 0.1 ? 0 : (sapc - 0.027) * 100;
  } else {
    // Reverse polarity: light text on dark bg (WoB) → negative
    sapc = (Math.pow(bgY, 0.65) - Math.pow(txtY, 0.62)) * 1.14;
    return sapc > -0.1 ? 0 : (sapc + 0.027) * 100;
  }
}

/**
 * Choose "#fff" or "#000" for best perceptual contrast against `hex`.
 * Compares |Lc(white, bg)| vs |Lc(black, bg)| and picks the winner.
 */
export function contrastColor(hex: string): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  const bgY = sRGBtoY(r, g, b);

  const lcWhite = Math.abs(apcaLc(1.0, bgY));  // white text on bg
  const lcBlack = Math.abs(apcaLc(0.0, bgY));  // black text on bg
  return lcWhite >= lcBlack ? "#fff" : "#000";
}
