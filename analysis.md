# Detailed analysis of APCA

APCA was developed to address some [issues] related to contrast in the
[Web Content Accessibility Guidelines] (WCAG). WCAG is an official W3C
recommendation, a normative part of many laws all over the world, and
generally a good read.

I am a regular web developer with a bachelor's degree in math, but
without any training in the science around visual perception. That's why
I cannot evaluate whether APCA is *better* than WCAG 2.x. Instead this
is a systematic comparison of their mathematical properties.

## The contrast formula

### WCAG 2.x

```js
function gamma(x) {
  if (x < 0.04045) {
    return x / 12.92;
  } else {
    return Math.pow((x + 0.055) / 1.055, 2.4);
  }
}

function sRGBtoY(srgb) {
  var r = gamma(srgb[0] / 255);
  var g = gamma(srgb[1] / 255);
  var b = gamma(srgb[2] / 255);

  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(fg, bg) {
  var yfg = sRGBtoY(fg);
  var ybg = sRGBtoY(bg);

  var c = (ybg + 0.05) / (yfg + 0.05);
  return (c < 1) ? 1 / c : c;
};
```

Colors on the web are defined in the [sRGB color space]. The first part
of this formula is the official formula to convert a sRGB color to
luminance (Y). Doubling sRGB values (e.g. from `#444` to `#888`) does
not actually double the physical amount of light, so the first step is a
non-linear "gamma decoding". Then the red, green, and blue channels are
weighted to sum to the final luminance.

Next, 0.05 is added to both values. I am not exactly sure how to
interpret this parameter. It could model ambient light that is reflected
on the screen (flare).[^1] Or it might model the fact that black on a
screen is not total black. Or it might just be a numerical trick to
avoid deviding by zero. We will discuss the impact of this parameter
later.

Then we look at the ratio of these two values. I hope I can convince you
that these two statements are equivalent:

    ybg / yfg > 4.5
    log(ybg) - log(yfg) > log(4.5)

The first one is sometimes called "simple contrast", and this is what is
used in WCAG 2.x. The second one uses the [Weber-Fechner model] to
convert luminance to perceived lightness (J). Technically, the
Weber-Fechner law is `J = a * log(y) + b`, but `b` vanishes in the
difference and `a` would just scale the whole equation.

Given that the two are equivalent, you can think of this contrast ratio
as a lightness difference. We just convert the values to avoid having to
calculate logarithms.

Finally, the polarity is removed so that the formula has the same
results when the two colors are switched.

All in all this is a pretty solid contrast formula (at least from a
theoretical perspective), as it just reuses parts from well established
standards. The only odd bit is the `0.05` offset.

### APCA

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

  if (ybg > yfg) {
    var c = Math.pow(ybg, 0.56) - Math.pow(yfg, 0.57);
  } else {
    var c = Math.pow(ybg, 0.65) - Math.pow(yfg, 0.62);
  }

  c *= 1.14;

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

We again see a similar structure here: Convert sRGB colors to luminance;
convert luminance to perceived lightness; then calculate the difference.
But there are also some interesting differences.

The conversion from sRGB to luminance deviates from the sRGB standard.
Especially the non-linear part is very different. The author of APCA
provides some motivation for these changes in the article [Regarding
APCA Exponents] and in a [github issue]. The main argument seems to be
that this is supposed to more closely model real-world computer screens.
This step also makes sure that the smallest possible value is
`Math.pow(0.022, 1.414) ~= 0.0045`.

The conversion to lightness uses the more modern [Stevens model]
`J = a * pow(Y, alpha) + b` instead of Weber-Fechner.[^2] Interestingly,
APCA uses four different exponents for light foreground (0.62), dark
foreground (0.57), light background (0.56), and dark background (0.65).
Unfortunately, the three levels of exponents (gamma, alpha, different
exponents for light/dark foreground/background) are not clearly
separated, which makes analysis more complicated.

The final steps do some scaling and shifting that (in my understanding)
only serves to get nice threshold values. Just like the `log()`
conversion in the WCAG formula, this does not affect results as long as
the thresholds are adapted accordingly. Note that the `< 0.1` condition
only affects contrasts that are below any relevant thresholds anyway.

### Normalization

To make it easier to compare the two formulas, I will normalize them:

-   clearly seperate the individual steps of the calculation
-   calculate a difference of lightnesses
-   preserve polarity
-   scale to a range of -1 to 1

WCAG 2.x therefore becomes:

```js
function gamma(x) {
  if (x < 0.04045) {
    return x / 12.92;
  } else {
    return Math.pow((x + 0.055) / 1.055, 2.4);
  }
}

function sRGBtoY(srgb) {
  var r = gamma(srgb[0] / 255);
  var g = gamma(srgb[1] / 255);
  var b = gamma(srgb[2] / 255);

  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function YtoJ(y) {
  return (Math.log(y + 0.05) - Math.log(0.05)) / Math.log(21);
}

function contrast(fg, bg) {
  var yfg = sRGBtoY(fg);
  var ybg = sRGBtoY(bg);

  var jfg = YtoJ(yfg);
  var jbg = YtoJ(ybg);

  return jbg - jfg;
};
```

APCA becomes:

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

function YtoJ(y) {
  return Math.pow(y, 0.6);
}

function contrast(fg, bg) {
  var yfg = sRGBtoY(fg);
  var ybg = sRGBtoY(bg);

  var jfg = YtoJ(yfg);
  var jbg = YtoJ(ybg);

  if (ybg > yfg) {
    return Math.pow(jbg, 0.56 / 0.6) - Math.pow(jfg, 0.57 / 0.6);
  } else {
    return Math.pow(jbg, 0.65 / 0.6) - Math.pow(jfg, 0.62 / 0.6);
  }
};
```

### Comparison

Now that we have aligned the two formulas, we can compare them
numerically:

![contrast comparison]

These are scatter plots based on a random sample of color pairs. The
x-axis corresponds to background luminance, the y-axis corresponds to
foreground luminance (both using the APCA formula). The color of the
dots indicated the differences between the respective formulas.

The plot on the bottom right compares APCA to WCAG 2.x. As we can see,
the biggest differences are in areas where one color is extremely light
or extremely dark. For light colors, APCA predicts an even higher
contrast (difference is in the same direction as contrast polarity). For
dark colors, APCA predicts a lower contrast (difference is inverse to
contrast polarity). The difference goes up to 20%.

The other three plots compare APCA to a modified version of APCA where
one of the steps has been replaced by the corresponding step from
WCAG 2.x. This way we can see that `sRGBtoY` contributes 4% to the
difference, `YtoJ` contributes 15%, and `contrast` contributes 3%.

Since the conversion from luminance to lightness causes the biggest
difference, I took a closer look at it.

![lightness comparison]

I plotted curves for both the Weber-Fechner model (log) and the Stevens
model (pow) with different parameters.

-   Both models produce curves with a concave shape.
-   The log curve with an offset of 0.05 (WCAG 2) is closer to the pow
    curve with an exponent of 1/3 and an offset of 0.0025
-   The log curve with an offset of 0.4 is closer to the pow curves with
    exponents 0.56 and 0.68 and an offset of 0.0045 (similar to APCA)

This shows that a big part of the different results between WCAG 2.x and
APCA are caused by a different choice in parameters. If we were to
change the offset value in WCAG 2.x to 0.4 we would get results much
closer to APCA. And if we were to change the exponents in APCA to 1/3 we
would get results much closer to WCAG 2.x.

Our vision adapts to the lighting conditions. In the dark, we are much
better at discerning dark colors. A lower exponent models these darker
conditions. The most complete (but also most complex) color appearance
model currently available is [CIECAM02]. It uses exponents between 0.31
and 0.72. Given that model, WCAG 2.x is on the lower (darker) end of
possible exponents, while APCA goes to the other (lighter) extreme. This
is consistent with the observation that APCA reports lower contrast for
darker colors.

## Thresholds: How much contrast is enough contrast?

### WCAG 2.x

Smaller text requires more contrast to be legible[^3], so the thresholds should
probably depend on font size.

WCAG 2.x only distinguished two font sizes The thresholds are 4.5:1 for regular
text and 3:1 for large text. If you aim for AAA conformance, the thresholds are
7:1 and 4.5:1. How these thresholds were derived is not completely clear:

> My recollection is that the hard data pointed to a ratio of 4.65:1 as a
> defensible break point. The working group was close to rounding that up to
> 5:1, just to have round numbers. I successfully lobbied for 4.5:1 mostly
> because (1) the empirical data was not overwhelmingly compelling, and (2)
> 4.5:1 allowed the option for white and black (simultaneously) on a middle
> gray.\
> -- <https://github.com/w3c/wcag/issues/695#issuecomment-484187617>

[Large text] is defined as anything above 18 point or 14 point bold. The
definition comes with a lot of notes that explain the limits of that approach
though, e.g. that some fonts are extremely thin and that font size depends on
user settings.

WCAG 2.x also comes with some rules that allow users to adapt font size
to their needs: [1.4.4] requires that users can resize the text,
[1.4.10] requires that they can zoom the whole page, and [1.4.12]
requires that they can adjust text spacing.

So in a way, WCAG 2.x side-steps the issue by handing control over to
the users who have all the facts.

### APCA

APCA on the other has a much more sophisticated threshold system. It
provides a [table] that defines thresholds based on font size, weight
and whether or not the text is body text. It also tries to account for
different fonts. However, that system is complicated and leaves a lot of
wiggle room.

Unfortunately, there is next to no information on how that table was
generated, so there is not mach I can say about it.

## Conclusion

> all models are wrong, but some are useful\
> -- George Box

WCAG faces a difficult challenge: There is no one-size-fits-all solution
for accessibility. Different humans have different needs, and different
situations require different kinds of support.

This is also the case in the context of color contrast: vision
impairments, ambient light, screen settings, font settings, and zoom can
all have a pronounced impact on legibility. None of these are known
beforehand by website authors, so the rules provided by WCAG need to
work regardless of these factors.

Faced with the question whether it wanted to give simple and precise
instructions (that might not be ideal in every situation) or give
nuanced but ultimately vague advise, WCAG went with the former. So today
WCAG provides a list of detailed steps for evaluating a website. Many of
these checks can be automated. It does not always result in perfect
accessibility, but it gives lawmakers a solid baseline.

APCA proposes some changes to the way we calculate color contrasts:

1.  It uses a different luminance calculation that deviates from the
    standards but is supposed to be closer to real world usage.
2.  It uses the more modern Stevens model
3.  It assumes different (lighter) lighting conditions for converting
    luminance to perceptual lightness.
4.  It adds an additional step where different exponents are applied to
    foreground and background.
5.  It uses different scaling. Crucially, this scaling is based on a
    difference rather than a ratio.
6.  It uses a more sophisticated system for thresholds.

I am fine with (2) and (5). I am not sure if they justify breaking
changes, but if we want to come up with a new algorithm then I think
these are ideas we should keep.

Points (1) and (4) need empirical evaluation. Unfortunately, there is
still a [severe lack of publicly available research] on APCA. On
request, APCA's author just provided a [list of unrelated links].

For me, (3) and (6) are the big issues. Even if APCA is a good model to
calculate contrast, many of its innovations just don't work in the
context of WCAG where we need to provide clear guidance without knowing
the viewing conditions.

Granted, the WCAG 2.x algorithm also makes assumptions. But instead of
fighting over which parameters are *correct*, we should discuss how we
can deal with that uncertainty.

[issues]: https://www.bounteous.com/insights/2019/03/22/orange-you-accessible-mini-case-study-color-ratio/
[Web Content Accessibility Guidelines]: https://www.w3.org/TR/WCAG21/
[sRGB color space]: https://en.wikipedia.org/wiki/SRGB
[Weber-Fechner model]: https://en.wikipedia.org/wiki/Weber%27s_Law
[Regarding APCA Exponents]: https://git.apcacontrast.com/documentation/regardingexponents
[github issue]: https://github.com/w3c/wcag3/issues/226
[Stevens model]: https://en.wikipedia.org/wiki/Stevens's_power_law
[contrast comparison]: plots/contrast_comparison.png
[lightness comparison]: plots/lightness_comparison.png
[CIECAM02]: https://en.wikipedia.org/wiki/CIECAM02
[large text]: https://www.w3.org/TR/WCAG21/#dfn-large-scale
[1.4.4]: https://www.w3.org/TR/WCAG21/#resize-text
[1.4.10]: https://www.w3.org/TR/WCAG21/#reflow
[1.4.12]: https://www.w3.org/TR/WCAG21/#text-spacing
[table]: https://git.apcacontrast.com/documentation/README#font-use-lookup-tables
[severe lack of publicly available research]: https://github.com/w3c/silver/issues/574
[list of unrelated links]: https://github.com/w3c/wcag3/issues/29

[^1]: [Hwang AD, Peli E. (2016). New Contrast Metric for Realistic Display Performance Measure.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5489230/)
[^2]: [Monaci, Gianluca & Menegaz, Gloria & Susstrunk, S. & Knoblauch, Kenneth. (2022). Color Contrast Detection in Spatial Chromatic Noise.](https://www.researchgate.net/publication/37435854_Color_Contrast_Detection_in_Spatial_Chromatic_Noise)
[^3]: [Georgeson, M. A., & Sullivan, G. D. (1975). Contrast constancy: deblurring in human vision by spatial frequency channels.](https://pubmed.ncbi.nlm.nih.gov/1206570/)
