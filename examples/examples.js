import * as wcag from '../wcag2.js';
import * as apca from '../apca.js';

const WCAG_LABELS = ['< 3', '> 3', '> 4.5', '> 7'];
const APCA_LABELS = ['< 45', '> 45', '> 60', '> 75'];

const COLORS = [
	['#888888', '#000000', '#ffffff'],
	['#ff4422', '#000000', '#ffffff'],
	['#44bb44', '#000000', '#ffffff'],
	['#9999ff', '#000000', '#ffffff'],
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
	for (let i = 0; i < 3; i++) {
		if (a < module.levels[i + 2]) {
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
	display.textContent = `${fg} on ${bg}`;
	display.style.color = fg;
	display.style.backgroundColor = bg;

	var wcag_contrast = wcag.contrast(cfg, cbg);
	var wcag_level = getLevel(wcag_contrast, wcag);
	clone.querySelector('.wcag output').textContent = wcag.abs(wcag_contrast).toFixed(1);
	clone.querySelector('.wcag .badge').textContent = WCAG_LABELS[wcag_level];
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
