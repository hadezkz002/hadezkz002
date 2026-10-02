# Media handoff — signal slots

Shared channel between the **code agent** (puzzle logic, README, post-processing)
and the **media agent** (images, GIFs). Both sides edit this file: update the
status table and append to the log at the bottom. Keep it short.

> This repo is public. Nothing here may contain answers, keys or plaintexts —
> those live outside the repo with the owner. Do not ask for them; you do not
> need them to do your part.

## Status

| slot | file | owner now | status |
|------|------|-----------|--------|
| 0x01 | `signal/0x01.wav` | code | live |
| 0x02 | `signal/0x02.pub` | code | live |
| 0x03 | `signal/0x03.png` | media | **wanted** |
| 0x04 | `signal/0x04.gif` | media | **wanted** |

Status flow: `wanted` → `delivered` (media) → `live` (code).

## Workflow

1. Media agent commits the files at the exact paths above on its own branch and
   sets the slot to `delivered`. Do **not** touch `README.md` or anything else
   under `signal/`.
2. Code agent post-processes the delivered files in place, wires them into the
   README (the `<!-- slot:0x03 -->` / `<!-- slot:0x04 -->` markers, plus the
   `(sleeping)` entries in `TERMINAL` inside `tools/typeset.py` and in the
   terminal image's alt text), re-runs `tools/typeset.py`, and sets the slot
   to `live`.
3. After step 2, nobody re-exports, optimises, resizes or recompresses those
   files. Any change to a `live` file goes back through the code agent.

## Visual direction (both slots)

- Typography across the profile (outside the banner) is Archivo Expanded 800
  for display and Courier Prime for everything mono. If text appears inside
  your media, use the same pair.

- Must sit inside the existing profile: dark, minimal, terminal, cryptographic.
  Reference the current assets, `assets/after-hours.svg` and
  `assets/night-drive.png`.
- Palette: near-black `#100e17`, charcoal `#1a1722`, terminal grey `#aaa0b5`,
  off-white `#e5d6f7`. One accent only: lilac `#cfb0e9`. Pink `#de78b3` is
  allowed for tiny glitch cuts, nothing more.
- Motif: the cicada, which is original to this profile (see the ASCII one in
  `README.md`), plus number stations, old Unix, signals and noise. `3301` may
  appear once and stay small.
- Do not use the Cicada 3301 logo or its known artwork, anything from Nous
  Research / Hermes, skulls, Matrix rain, neon, emoji or watermarks.
- Every image must read on both GitHub light and dark backgrounds, so it needs
  its own dark field and no transparency.

## Slot specs

### 0x03 — `signal/0x03.png`

- PNG, **8-bit RGB, no alpha, non-interlaced, no palette/indexed mode**.
- At least 512 × 512 and at most 1200 px on the long side. Square is preferred.
- Use a photographic or noisy texture rather than flat colour. Grain, scanlines
  and dithering are good; large perfectly flat areas are not.
- Content idea: a cicada specimen photographed under a desk lamp, a pinned
  insect on graph paper, or a CRT macro. It must look like a finished artwork
  on its own, not like "a puzzle".
- Strip metadata (EXIF/XMP/text chunks).

### 0x04 — `signal/0x04.gif`

- GIF89a, loops forever, **at least 24 frames, at most 64**.
- Keep "optimise/merge identical frames" **off** so the frame count survives.
- Width 320–640 px, file under 5 MB.
- Content idea: a slow, quiet loop, such as a cicada's wing veins pulsing like a
  signal meter, a radio dial drifting, or the ASCII cicada flickering on a
  phosphor screen. No fast flashing (photosensitivity).

## Backlog (not scheduled)

These are ideas the code agent can wire up later. Media agent: say in the log
if you want to take one.

- 0x05: a short video. GitHub READMEs only play video uploaded through the web
  editor, so this would be a linked file rather than inline.
- 0x06: a printable "field card" image (specimen label style) for a final page.

## Log

- code: created slots 0x03/0x04, stages 0x01–0x02 are live. Waiting on media.
