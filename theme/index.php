<?php
/**
 * LaParusia — la page unique.
 *
 * Le balisage ci-dessous est EXTRAIT de index.html du site statique par
 * build_theme.py. Ne pas le modifier ici : la modification serait perdue a la
 * prochaine generation, et la version statique (le zip, l'apercu) ne
 * l'aurait pas. Modifier ../laparusia/index.html, puis regenerer.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<header class="top">
  <div class="wrap bar">
    <a class="brand" href="#top" aria-label="LaParusia, home">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 40 40" width="40" height="40" role="presentation">
          <circle cx="20" cy="20" r="19" fill="none" stroke="currentColor" stroke-width="2"/>
          <g stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
            <path d="M20 3v34M3 20h34M8 8l24 24M32 8L8 32"/>
          </g>
        </svg>
      </span>
      <span class="brand-word">LaParusia</span>
    </a>
    <nav class="nav">
      <a href="#builder">Build a pizza</a>
      <a href="#bakery">Bakery</a>
      <a href="#visit">Visit</a>
    </nav>
  </div>
</header>

<main id="top">

  <section class="hero">
    <div class="wrap hero-in">
      <p class="eyebrow">Pizza &amp; bakery</p>
      <h1>Eight slices.<br>Eight decisions.</h1>
      <p class="lede">Build one pizza the whole table agrees on, or a different topping on
        every one of the eight slices. Choose your size in inches and watch the price follow
        you either way.</p>
      <p class="hero-cta"><a class="btn" href="#builder">Start building</a>
        <a class="btn btn-quiet" href="#bakery">See the bakery</a></p>
    </div>
  </section>

  <!-- ====================================================== le constructeur -->
  <section id="builder" class="builder">
    <div class="wrap">
      <p class="kicker">The builder</p>
      <h2>Your pizza, your way</h2>

      <!-- Les deux façons de commander. Deux boutons visibles plutôt qu'une
           case à cocher : personne ne coche « slice by slice » sans savoir ce
           que ça veut dire, alors chacun porte sa phrase d'explication. -->
      <div class="mode" id="mode" role="radiogroup" aria-label="How you want to build it">
        <button type="button" class="mode-btn" id="modeWhole" role="radio" aria-checked="false">
          <b>One custom pizza</b>
          <small>The same toppings all the way round</small>
        </button>
        <button type="button" class="mode-btn" id="modeSlices" role="radio" aria-checked="true">
          <b>Slice by slice</b>
          <small>A different topping on each of the eight</small>
        </button>
      </div>

      <div class="build-grid">

        <!-- la pizza -->
        <div class="pie-side">
          <div class="pie-wrap">
            <svg id="pie" viewBox="0 0 420 420" role="img"
                 aria-label="A pizza cut into eight slices. Select a slice to give it its own toppings.">
              <defs>
                <radialGradient id="crustGrad" cx="50%" cy="45%" r="60%">
                  <stop offset="70%" stop-color="#E8C48E"/>
                  <stop offset="100%" stop-color="#C99A5E"/>
                </radialGradient>
              </defs>
              <circle cx="210" cy="210" r="196" fill="url(#crustGrad)"/>
              <circle cx="210" cy="210" r="196" fill="none" stroke="#B98A50" stroke-width="2"/>
              <g id="slices"></g>
              <g id="cuts" aria-hidden="true"></g>
            </svg>
          </div>

          <p class="pie-hint" id="pieHint">Slice 1 selected — choose its toppings.</p>

          <div class="pie-tools">
            <button class="btn btn-quiet" type="button" id="allSame">Put this slice on all eight</button>
            <button class="btn btn-quiet" type="button" id="clearSlice">Clear this slice</button>
          </div>
        </div>

        <!-- les choix -->
        <div class="pick-side">

          <fieldset class="block">
            <legend>Size</legend>
            <div class="sizes" id="sizes" role="radiogroup" aria-label="Pizza size in inches"></div>
            <p class="note" id="sizeNote"></p>
          </fieldset>

          <fieldset class="block" id="blockSlices">
            <legend>Slice</legend>
            <div class="slicetabs" id="sliceTabs" role="tablist" aria-label="Choose a slice"></div>
          </fieldset>

          <fieldset class="block">
            <legend>Base <span class="legend-note">— for the whole pizza</span></legend>
            <div class="bases" id="bases" role="radiogroup" aria-label="Sauce base"></div>
          </fieldset>

          <fieldset class="block">
            <legend>Toppings <span class="legend-note" id="toppingFor">— slice 1</span></legend>
            <div class="tops" id="tops"></div>
            <p class="note" id="topNote">A topping on one slice costs an eighth of what it
              costs on the whole pizza. That is the whole point of cutting it into eight.</p>
          </fieldset>

          <div class="ticket" aria-live="polite">
            <div class="ticket-row">
              <span>Base — <b id="tSize">12"</b></span><span id="tBase">$16.50</span>
            </div>
            <div class="ticket-row">
              <span>Toppings — <b id="tCount">0 slices topped</b></span><span id="tTops">$0.00</span>
            </div>
            <div class="ticket-row ticket-total">
              <span>Total</span><span id="tTotal">$16.50</span>
            </div>
            <p class="ticket-note">Prices shown are placeholders while the real menu is
              being set. Nothing here is an offer.</p>
          </div>

        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================= boulangerie -->
  <section id="bakery" class="bakery">
    <div class="wrap">
      <p class="kicker">The bakery</p>
      <h2>Baked the same morning</h2>
      <ul class="bakery-list" id="bakeryList"></ul>
      <p class="note">Same placeholder prices. Send the real ones and they drop straight in.</p>
    </div>
  </section>

  <!-- ================================================================== visite -->
  <section id="visit" class="visit">
    <div class="wrap visit-in">
      <div>
        <p class="kicker">Visit</p>
        <h2>Come and get it</h2>
        <p class="lede">The address, the opening hours and the phone number go here — they
          are the three things a hungry person actually looks for, so they get their own
          block rather than a line in the footer.</p>
        <p class="note">Waiting on the real details before anything is written here. An
          address that turns out to be wrong costs more than an empty space.</p>
      </div>
      <div class="visit-card">
        <p class="k">Address</p><p class="v">—</p>
        <p class="k">Hours</p><p class="v">—</p>
        <p class="k">Phone</p><p class="v">—</p>
      </div>
    </div>
  </section>

</main>

<footer class="foot">
  <div class="wrap foot-in">
    <span>LaParusia — pizza and bakery</span>
    <span class="foot-note">Demonstration build. Prices and details are placeholders.</span>
  </div>
</footer>
<?php get_footer(); ?>
