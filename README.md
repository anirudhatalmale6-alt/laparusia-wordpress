# LaParusia — WordPress theme

The pizza builder as a WordPress theme, generated from the static site that was
already built and checked. One page: eight slices, each carrying its own
toppings, priced from a JSON file.

```
build_theme.py   reads ../laparusia and writes theme/
verif.py         checks the result in a real browser, against a real WordPress
theme/           what gets installed
laparusia-theme-1.0.0.zip   the same folder, installable as it is
```

## The theme is generated, not written

Nothing in `theme/` is typed by hand. `build_theme.py` extracts the markup, the
stylesheet, the script and the price list from `../laparusia`, which is the
version that was verified at the rendered page — eight slices, five sizes, the
arithmetic recomputed by hand from the JSON.

That is on purpose. A second copy of the markup, maintained by hand, diverges
from the first the day a price changes, and the copy that is wrong is the one
that happens to be online. **Edit `../laparusia`, then regenerate.** Editing
`theme/` directly loses the change at the next build, and the static version —
the zip, the preview — never receives it.

## The one thing that had to change

`app.js` fetches the price list. In the static site the page and `data/` sit in
the same folder, so a relative path is correct. Under WordPress the page is
served at the root of the domain while the file lives inside the theme, so
`data/menu.json` would resolve to `/data/menu.json` — a 404, and the builder
would show its "menu could not be loaded" message instead of every price on the
page.

So the theme sets `window.LP_MENU_URL` to the real URL, and `app.js` reads
`window.LP_MENU_URL || 'data/menu.json'`. The same file serves both. There are
not two versions of the script to keep in step.

## No price is written in the code

Every figure comes from `theme/data/menu.json`, and **every figure in it is a
placeholder**. Sizes, toppings, bakery items, the currency. Replace them with
the real card and nothing else needs touching — no template, no stylesheet, no
script.

The address, the opening hours and the telephone number are deliberately left
empty. A wrong address on a bakery costs more than an empty line.

## Verification

`python3 verif.py http://your-dev-url` — 23 checks in a real browser against a
real WordPress install. **23 checks, 0 failures**, run against the theme
installed from the zip rather than from the working folder.

What it actually checks, rather than that the page loads:

- the price list is requested **from inside the theme**, answers 200, and the
  builder is not showing its failure message;
- the total on screen equals the total **recomputed independently from the
  JSON** — for a whole pizza, for one topped slice, and for all eight;
- the one-eighth rule: a topping on one slice costs an eighth of its price on
  the whole pizza, so eight identical slices land exactly on the price of the
  whole pizza with that topping;
- every amount visible on the page can be derived from the card — a figure that
  cannot is an invented price, which is the most expensive defect a menu can
  carry;
- the order of sizes and toppings on screen is the order in the card;
- no PHP notice or JavaScript error anywhere, and no horizontal overflow at
  390 px.

### The suite is proved able to fail

A check that has never failed proves nothing. One topping was changed by 25
cents in the served card and the run produced four named failures — the whole
pizza total, the single slice, the eight slices, and `$0.47` appearing on
screen as an amount the card cannot produce. Then it was restored and the run
went green again.

One thing the rig taught me, worth writing down: breaking the price-list path
on purpose did **not** produce a clean failure, it produced a hang. PHP's
built-in development server is single-threaded, so the page request and the
404 for the missing file deadlock each other. That is the test rig, not the
site — but it is why the positive control changes a *price* rather than a
*path*.

## Installing

The theme folder, or the zip, goes in `wp-content/themes/`. It needs no plugin,
no database content and no page to be created: the front page **is** the
builder, whatever WordPress is set to show.
