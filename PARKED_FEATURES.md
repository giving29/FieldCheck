# FieldCheck — Parked Features (retrievable)
_Things intentionally hidden from the live site but fully preserved in the code.
 This doc is the index of what's parked and EXACTLY how to bring each back._

---

## 1. Greatest Clips / "The moments, in motion." (homepage reel)
**Parked:** July 2026. **Why:** overlapped with the Feed; two showcase surfaces diluted the
company-ready homepage. Feed kept as the single showcase. Reel can return anytime.

**Where it is now:** `index.html`, wrapped in an inert `<template id="parked-greatest-clips">`.
A `<template>` renders nothing and its inner `<script>` does NOT run — but the full block is
preserved verbatim in the file. Bounded by these markers:
- `<!-- PARKED_CLIPS_START ... -->` then `<template id="parked-greatest-clips" data-parked="moments-in-motion">`
- `</template>` then `<!-- PARKED_CLIPS_END -->`
The original block still carries its own inner comments:
`<!-- ====== THE GREATEST CLIPS — home reel ====== -->` … `<!-- ====== end Greatest Clips ====== -->`

**HOW TO BRING IT BACK (un-park):**
1. Open `index.html`, find `PARKED_CLIPS_START`.
2. Delete these FOUR wrapper lines only, leaving the block between them intact:
   - the `<!-- PARKED_CLIPS_START ... -->` comment line
   - the `<template id="parked-greatest-clips" ...>` opening line
   - the matching `</template>` line
   - the `<!-- PARKED_CLIPS_END -->` comment line
3. The reel's `<section>`, styles, data, and `<script>` are now live again exactly as before.
4. Verify: `grep -c 'parked-greatest-clips' index.html` should return 0 after un-parking.
5. `fck dev` → check the reel renders + scrolls on the homepage → `fck ship "un-park: restore Greatest Clips reel"`.

**Quick sanity after un-park:** the homepage should again show "The moments, in motion." with the
scrolling clip rail (`#reel` / `#track`) below the live-journeys strip and above the audience section.

---

## (template for future parks)
## N. <Feature name>
**Parked:** <date>. **Why:** <reason>.
**Where it is now:** <file + wrapper method>.
**HOW TO BRING IT BACK:** <exact steps>.
