# The missing introduction to APCA

## What is APCA?

The [Accessible Perceptual Contrast Algorithm (APCA)](https://git.apcacontrast.com/)
is a new algorithm to estimate the visual contrast between two colors.
It was developed to address some issues in earlier algorithms, especially for
dark colors.

APCA was created by Andrew Somers (Myndex) and is currently being proposed for
the next major version of the [W3C Accessibility Guidelines
(WCAG)](https://www.w3.org/TR/wcag-3.0/).

An interactive demo is available at <https://xi.github.io/apca-introduction/tool/>.

## Algorithm

```js
function sRGBtoY(srgb) {
  var r = Math.pow(srgb[0] / 255, 2.4);
  var g = Math.pow(srgb[1] / 255, 2.4);
  var b = Math.pow(srgb[2] / 255, 2.4);
  var y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b;

  if (y < 0.022) {
    y += Math.pow(0.022 - y, 1.414);
  }
  return y;
}

function contrast(fg, bg) {
  var yfg = sRGBtoY(fg);
  var ybg = sRGBtoY(bg);
  var c = 1.14;

  if (ybg > yfg) {
    c *= Math.pow(ybg, 0.56) - Math.pow(yfg, 0.57);
  } else {
    c *= Math.pow(ybg, 0.65) - Math.pow(yfg, 0.62);
  }

  if (Math.abs(c) < 0.1) {
    return 0;
  } else if (c > 0) {
    c -= 0.027;
  } else {
    c += 0.027;
  }

  return c * 100;
};
```

([Source](https://github.com/Myndex/SAPC-APCA/blob/master/documentation/APCA-W3-LaTeX.md))

## Migrating from WCAG 2.x

- WCAG 2.x produces a ratio between 1:1 and 21:1. APCA produces a value roughly
  between -100 and 100.
- Unlike WCAG 2.x, APCA reports different values when you switch foreground and
  background.
- The result of APCA is negative for light text on dark background. You will
  usually work with the absolute value though.
- WCAG 2.x defined three thresholds: 3:1, 4.5:1, and 7:1. These roughly
  correspond to 45, 60, and 75 in APCA.

## Examples

[![Visual comparison of WCAG 2.x and APCA](https://blog.datawrapper.de/wp-content/uploads/2022/01/Artboard-448-copy-2-1006x1024.png)](https://blog.datawrapper.de/color-contrast-check-data-vis-wcag-apca/)

## Status

WCAG is an important standard that is a normative part of many laws all over
the world. If APCA will be part of WCAG 3.0 it will have a huge impact.
However, currently both WCAG 3.0 and APCA are still in early development.
Neither is officially recommended by the W3C yet.

## Why this document

The original author has published a lot of information on APCA. So why did I
create this introduction?

For one it was born out of my personal frustration with the original
documentation. Some important pieces of information (e.g. the actual algorithm)
get buried under all that text.

The original documentation also contains absolute statements like "APCA is
perceptually uniform" and that the old algorithm produces "invalid results".
This in my opinion is wrong as perceptual uniformity is an ideal that can never
be reached completely. So I felt like there was room for a more balanced
introduction.

If you want to dig deeper, I recommend to start with the [original WCAG
issue](https://github.com/w3c/wcag/issues/695) and the [documentation
README](https://git.apcacontrast.com/documentation/README).
