#!/usr/bin/env node
import { randomInt, randomUUID } from "node:crypto";

const families = [
  {
    family: "Field Note",
    composition: ["marginal annotations", "offset editorial column", "stacked note fragments"],
    measure: ["420px", "460px", "520px"],
    palette: ["warm paper + mineral accent", "ivory + botanical accent", "newsprint + terracotta"],
    type: ["editorial serif + sans", "humanist sans + mono"],
    radius: ["sharp 0-2px", "machined 4-7px"],
    surface: ["paper rules", "whitespace + one inset frame"],
    motif: ["single emoji annotation", "stamp", "tiny index"],
    motion: ["quiet fade + clipped underline", "short rise + annotation float"],
  },
  {
    family: "Lab Instrument",
    composition: ["stacked live readout", "artifact-first control surface", "offset instrument panel"],
    measure: ["440px", "500px", "560px"],
    palette: ["cool fog + cobalt", "warm neutral + semantic colors", "bone + pine"],
    type: ["grotesk + mono", "humanist sans + mono"],
    radius: ["machined 4-7px", "balanced 8-12px"],
    surface: ["inset hairlines", "subtle layered rings"],
    motif: ["readout marks", "colored state dots", "measurement ticks"],
    motion: ["trace + press compression", "state morph + short stagger"],
  },
  {
    family: "Pocket Console",
    composition: ["framed command surface", "log-first console", "command rail + output pane"],
    measure: ["480px", "540px", "620px"],
    palette: ["charcoal + amber", "off-black + ice blue", "smoke + muted coral"],
    type: ["all-mono", "condensed sans + mono"],
    radius: ["sharp 0-2px", "machined 4-7px"],
    surface: ["flat dividers", "technical frames"],
    motif: ["ASCII mark", "line numbers", "cursor glyph"],
    motion: ["slot swap + state wash", "scan reveal + selection slide"],
  },
  {
    family: "Playful Shelf",
    composition: ["choice catalogue", "tactile specimen shelf", "artifact surrounded by choices"],
    measure: ["500px", "560px", "640px"],
    palette: ["tinted canvas + candy signals", "chalk + primary accent", "soft blue + citrus"],
    type: ["rounded sans + mono", "humanist sans + mono"],
    radius: ["friendly 14-18px", "soft 20-24px"],
    surface: ["tinted panels", "soft shadow rings"],
    motif: ["1-3 product emojis", "CSS doodles", "colored punctuation"],
    motion: ["ambient float + soft pop", "state color change + press compression"],
  },
  {
    family: "Split Pamphlet",
    composition: ["text + artifact split", "asymmetric two-zone spread", "title wrapped around specimen"],
    measure: ["600px", "660px", "720px"],
    palette: ["editorial white + deep red", "cream + navy", "fog + forest"],
    type: ["serif + sans", "grotesk + condensed"],
    radius: ["mixed sharp/soft", "balanced 8-12px"],
    surface: ["whitespace + paper rules", "one framed specimen"],
    motif: ["large initial", "stamp", "cropped product image"],
    motion: ["opposing short slides", "clipped reveal + fixed-frame scale"],
  },
  {
    family: "Compact Catalogue",
    composition: ["indexed list + detail pane", "offset specimen grid", "stepped product rows"],
    measure: ["560px", "640px", "720px"],
    palette: ["monochrome + vermilion", "product-tinted neutral", "bone + ultramarine"],
    type: ["condensed + sans", "grotesk + mono"],
    radius: ["sharp 0-2px", "deliberate mixed radii"],
    surface: ["dividers + negative space", "selected detail elevation"],
    motif: ["numeric indices", "swatches", "measurement marks"],
    motion: ["selection slide + fixed-pane crossfade", "restrained row hover + fade"],
  },
];

const pick = (values) => values[randomInt(values.length)];
const family = pick(families);
const fingerprint = Object.fromEntries(
  Object.entries(family).map(([key, value]) => [key, Array.isArray(value) ? pick(value) : value]),
);

console.log(JSON.stringify({ id: randomUUID().slice(0, 8), ...fingerprint }, null, 2));
