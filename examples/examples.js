import * as wcag from '../wcag2.js';
import * as apca from '../apca.js';

const LEVEL_LABELS = ['XX', 'A', 'AA', 'AAA'];
const APCA_LABELS = ['NOTXT', 'SPOT', 'SUBFL', 'FLUENT', 'BODYTX'];

const COLORS = [
	['#9999ff', '#000000', '#ffffff'],
	['#00bb00', '#000000', '#ffffff'],
	['#ff7373', '#000000', '#ffffff'],
	['#3333FF', '#000000', '#ffffff'],
	['#40631F', '#000000', '#ffffff'],
	['#B80000', '#000000', '#ffffff'],
	['#0F6BFF', '#000000', '#ffffff'],
	['#008A00', '#000000', '#ffffff'],
	['#E62200', '#000000', '#ffffff'],
	['#11bbff', '#220044', '#440022'],
];

var parseColor = function(c) {
	return [
		parseInt(c.substr(1, 2), 16),
		parseInt(c.substr(3, 2), 16),
		parseInt(c.substr(5, 2), 16),
	];
};

var getLevel = function(c, module) {
	var a = module.abs(c);
	for (let i = 0; i < 5; i++) {
		if (a < module.levels[i + 1]) {
			return i;
		}
	}
	return 3;
};

var template = document.querySelector('template');

var addExample = function(fg, bg) {
	var cfg = parseColor(fg);
	var cbg = parseColor(bg);

	var clone = template.content.cloneNode(true);

	var display = clone.querySelector('.display');
	display.textContent = `text ${fg} on ${bg} BG`;
	display.style.color = fg;
	display.style.backgroundColor = bg;

	var wcag_contrast = wcag.contrast(cfg, cbg);
	var wcag_level = getLevel(wcag_contrast, wcag);
	clone.querySelector('.wcag output').textContent = wcag.abs(wcag_contrast).toFixed(1);
	clone.querySelector('.wcag .badge').textContent = LEVEL_LABELS[wcag_level];
	clone.querySelector('.wcag .badge').classList.add(`badge-${wcag_level}`);

	var apca_contrast = apca.contrast(cfg, cbg);
	var apca_level = getLevel(apca_contrast, apca);
	clone.querySelector('.apca output').textContent = apca_contrast.toFixed(0);
	clone.querySelector('.apca .badge').textContent = APCA_LABELS[apca_level];
	clone.querySelector('.apca .badge').classList.add(`badge-${apca_level}`);

	document.body.append(clone);
};

COLORS.forEach(([c1, c2, c3]) => {
	addExample(c1, c2);
	addExample(c2, c1);
	addExample(c1, c3);
	addExample(c3, c1);
});
