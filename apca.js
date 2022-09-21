export const levels = [0,15,22,30,37.5,45,52.5,60,67.5,75,82.5,90,110];
export const arraySize = levels.length;

const tests = [
  [[136, 136, 136], [255, 255, 255], 63.056469930209424],
  [[255, 255, 255], [136, 136, 136], -68.54146436644962],
  [[  0,   0,   0], [170, 170, 170], 58.146262578561334],
  [[170, 170, 170], [  0,   0,   0], -56.24113336839742],
  [[ 17,  34,  51], [221,  51, 255], 91.66830811481631],
  [[221,  51, 255], [ 17,  34,  51], -93.06770049484275],
  [[ 17,  34,  51], [ 68,  68,  68], 8.32326136957393],
  [[ 68,  68,  68], [ 17,  34,  51], -7.526878460278154],
];

var sRGBtoY = function(srgb) {
  var r = Math.pow(srgb[0] / 255, 2.4);
  var g = Math.pow(srgb[1] / 255, 2.4);
  var b = Math.pow(srgb[2] / 255, 2.4);
  var y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b;

  if (y < 0.022) {
    y += Math.pow(0.022 - y, 1.414);
  }
  return y;
};

export var contrast = function(fg, bg) {
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

export var abs = function(c) {
  return Math.abs(c);
};

var runTests = function() {
  tests.forEach(function(test) {
    var actual = contrast(test[0], test[1]);
    var expected = test[2];
    if (Math.abs(actual - expected) > 0.00001) {
      console.log(test, actual);
    }
  });
};
