import * as apca from '../apca.js';
import * as wcag2 from '../wcag2.js';

var fgInput = document.querySelector('#fgInput');
var bgInput = document.querySelector('#bgInput');
var swapButton = document.querySelector('#swap');
var apcaGradient = document.querySelector('#apcaGradient');
var apcaOutput = document.querySelector('#apcaOutput');
var wcag2Gradient = document.querySelector('#wcag2Gradient');
var wcag2Output = document.querySelector('#wcag2Output');

var alphaBlend = function(fg, bg) {
  return [
    fg[0] * fg[3] + bg[0] * (1 - fg[3]),
    fg[1] * fg[3] + bg[1] * (1 - fg[3]),
    fg[2] * fg[3] + bg[2] * (1 - fg[3]),
  ];
};

var contrastAlpha = function(afg, abg, contrast) {
  var bgBlack = alphaBlend(abg, [0, 0, 0]);
  var fgBlack = alphaBlend(afg, bgBlack);
  var cBlack = contrast(fgBlack, bgBlack);

  var bgWhite = alphaBlend(abg, [255, 255, 255]);
  var fgWhite = alphaBlend(afg, bgWhite);
  var cWhite = contrast(fgWhite, bgWhite);

  return [
    Math.min(cBlack, cWhite),
    Math.max(cBlack, cWhite),
  ];
};

var score = function(range, levels) {
  var biggerThan = function(t) {
    if (range[0] > t) {
      return 1;
    } else if (range[1] > t) {
      return (range[1] - t) / (range[1] - range[0]);
    } else {
      return 0;
    }
  };

  var result = [];
  var sum = 0;
  levels.forEach(level => {
    var v = biggerThan(-level) - biggerThan(level);
    result.push(v - sum);
    sum = v;
  });
  result.push(1 - sum);

  return result;
};

var makeGradient = function(scores) {
  const colors = [
    'hsl(0, 100%, 40%)',
    'hsl(40, 100%, 45%)',
    'hsl(80, 60%, 45%)',
    'hsl(95, 60%, 41%)',
  ];

  var stops = [];
  var prevScore = 0;
  var scale = x => x * 70 + 15;  // compensate for border radius

  for (var i = 0; i < scores.length; i++) {
    if (scores[i] > 0) {
      var newScore = prevScore + scores[i];
      stops.push(`${colors[i]} ${scale(prevScore)}%`, `${colors[i]} ${scale(newScore)}%`);
      prevScore = newScore;
    }
  }

  return `linear-gradient(135deg, ${stops.join(', ')})`;
};

var parseColor = function(s) {
  var rgba = s.match(/rgba?\(([\d.]+), ([\d.]+), ([\d.]+)(?:, ([\d.]+))?\)/);
  if (!rgba) {
    return null;
  }
  rgba.shift();
  if (rgba[3] === undefined) {
    rgba[3] = 1;
  }
  rgba = rgba.map(x => parseFloat(x, 10));
  return rgba;
};

var setColor = function(input, key) {
  var old = getComputedStyle(document.body)[key];
  document.body.style[key] = input.value;
  var value = getComputedStyle(document.body)[key];
  return value !== old;
};

var formatRange = function(range, places) {
  var avg = (range[0] + range[1]) / 2;
  var delta = avg - range[0];
  if (delta.toFixed(places) === (0).toFixed(places)) {
    return `${avg.toFixed(places)}`;
  } else {
    return `${avg.toFixed(places)} ±${delta.toFixed(places)}`;
  }
};

var oninput = function() {
  // NOTE: | to prevent lazy evaluation
  if (setColor(bgInput, 'backgroundColor') | setColor(fgInput, 'color')) {
    var fgUrl = encodeURIComponent(fgInput.value);
    var bgUrl = encodeURIComponent(bgInput.value);
    location.hash = `${fgUrl}-on-${bgUrl}`;

    var bg = parseColor(getComputedStyle(document.body).backgroundColor);
    var fg = parseColor(getComputedStyle(document.body).color);

    var apcaRange = contrastAlpha(fg, bg, apca.contrast);
    apcaGradient.style.backgroundImage = makeGradient(score(apcaRange, apca.levels));
    apcaOutput.textContent = formatRange(apcaRange, 0);

    var wcag2Range = contrastAlpha(fg, bg, wcag2.contrast);
    wcag2Gradient.style.backgroundImage = makeGradient(score(wcag2Range.map(Math.log), wcag2.levels.map(Math.log)));
    wcag2Output.textContent = formatRange(wcag2.getAbsRange(wcag2Range), 1);
  }
};

var onhashchange = function() {
  var colors = location.hash.slice(1).split('-on-');
  fgInput.value = decodeURIComponent(colors[0]);
  bgInput.value = decodeURIComponent(colors[1]);
  oninput();
};

var onswap = function() {
  var tmp = bgInput.value;
  bgInput.value = fgInput.value;
  fgInput.value = tmp;
  oninput();
};

fgInput.addEventListener('input', oninput);
bgInput.addEventListener('input', oninput);
swapButton.addEventListener('click', onswap);
window.addEventListener('hashchange', onhashchange);

if (location.hash) {
  onhashchange();
} else {
  oninput();
}
