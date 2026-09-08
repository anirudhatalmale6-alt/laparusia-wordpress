# -*- coding: utf-8 -*-
"""
Fabrique le theme WordPress « laparusia » A PARTIR du site statique deja
verifie (../laparusia). Rien n'est retape ici : le balisage, le CSS, le
JavaScript et la carte sont EXTRAITS des fichiers d'origine.

Pourquoi extraire plutot que reecrire : le constructeur de pizza a ete
verifie au rendu (huit parts, cinq tailles, l'addition recalculee a la main
depuis le JSON). Une deuxieme copie du balisage, maintenue a la main, aurait
diverge des la premiere correction de prix — et la version fausse aurait ete
celle en ligne.

Sortie : theme/  (a deposer dans wp-content/themes/laparusia)
"""
import json
import os
import re
import shutil

RACINE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.normpath(os.path.join(RACINE, "..", "laparusia"))
SORTIE = os.path.join(RACINE, "theme")

VERSION = "1.0.1"


def lire(nom):
    with open(os.path.join(SOURCE, nom), encoding="utf-8") as f:
        return f.read()


def php_chaine(valeur):
    """Une chaine PHP entre apostrophes. Seuls \\ et ' s'echappent dans cette
    forme — pas $, pas \\n : PHP ne les interprete pas entre apostrophes."""
    return "'" + valeur.replace("\\", "\\\\").replace("'", "\\'") + "'"


def ecrire(chemin, contenu):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)


# ---------------------------------------------------------------------------
# 1. Decoupe de la page statique.
html = lire("index.html")

m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
if not m:
    raise SystemExit("index.html : <body> introuvable — le theme serait vide")
corps = m.group(1)

# Le <script> de fin de page part dans functions.php (wp_enqueue_script), sinon
# il serait charge DEUX fois : une par le balisage, une par WordPress. Un
# double chargement de app.js rebranche tous les ecouteurs et chaque clic
# compterait double.
corps, nb_scripts = re.subn(r"[ \t]*<script[^>]*src=[^>]*></script>\s*", "", corps)

titre = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
desc = re.search(r'<meta name="description" content="(.*?)"', html, re.S).group(1)


def meta_og(prop):
    m = re.search(r'<meta property="%s" content="(.*?)"' % re.escape(prop), html, re.S)
    return m.group(1) if m else ""


og = {p: meta_og(p) for p in ("og:type", "og:site_name", "og:locale",
                              "og:title", "og:description")}

# La carte est LUE ici uniquement pour un controle de coherence. Le theme
# sert le fichier tel quel ; aucun prix ne passe par ce script.
carte = json.loads(lire(os.path.join("data", "menu.json")))
assert carte["sizes"] and carte["toppings"], "menu.json : carte vide"


# ---------------------------------------------------------------------------
# 2. Ecriture du theme.
if os.path.isdir(SORTIE):
    shutil.rmtree(SORTIE)
os.makedirs(SORTIE)

css_site = lire("style.css")
ecrire(os.path.join(SORTIE, "style.css"), f"""/*
Theme Name: LaParusia
Theme URI: https://laparusia.com/
Author: Anirudha Talmale
Description: Single-page theme for LaParusia — pizza and bakery. The page is
  the pizza builder: eight slices, each carrying its own toppings, priced from
  data/menu.json. No figure is written into the code.
Version: {VERSION}
Requires at least: 6.0
Tested up to: 7.1
License: GPLv2 or later
Text Domain: laparusia
*/

{css_site}""")

# functions.php — tout ce que WordPress ajoute d'office et qui n'a rien a faire
# sur cette page part ici.
ecrire(os.path.join(SORTIE, "functions.php"), r"""<?php
/**
 * LaParusia — theme d'une seule page.
 *
 * Le principe : le balisage, le CSS et le JavaScript viennent du site
 * statique verifie. WordPress sert de coquille, il ne reecrit rien.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'LP_VERSION', '%%VERSION%%' );

function lp_soutien() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'html5', array( 'style', 'script' ) );
}
add_action( 'after_setup_theme', 'lp_soutien' );

function lp_ressources() {
	wp_enqueue_style( 'laparusia', get_stylesheet_uri(), array(), LP_VERSION );
	wp_enqueue_script( 'laparusia', get_template_directory_uri() . '/app.js',
		array(), LP_VERSION, true );

	/*
	 * LE POINT QUI CASSE TOUT SI ON L'OUBLIE.
	 * app.js va chercher la carte des prix. En statique, la page et data/ sont
	 * dans le meme dossier. Ici la page est servie a la racine du domaine et
	 * le fichier vit dans le theme : un chemin relatif pointerait sur
	 * /data/menu.json — 404, et le constructeur afficherait son message
	 * d'erreur a la place des prix. On lui donne donc l'URL reelle.
	 */
	wp_add_inline_script( 'laparusia',
		'window.LP_MENU_URL = ' . wp_json_encode(
			get_template_directory_uri() . '/data/menu.json?v=' . LP_VERSION
		) . ';', 'before' );
}
add_action( 'wp_enqueue_scripts', 'lp_ressources' );

/*
 * Cette page n'a ni article, ni commentaire, ni emoji, ni fil RSS, ni API
 * publique a annoncer. Chaque balise retiree est une requete de moins et une
 * information de moins sur l'installation.
 */
function lp_allege() {
	remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
	remove_action( 'wp_print_styles', 'print_emoji_styles' );
	remove_action( 'wp_head', 'wp_generator' );
	remove_action( 'wp_head', 'wlwmanifest_link' );
	remove_action( 'wp_head', 'rsd_link' );
	remove_action( 'wp_head', 'feed_links_extra', 3 );
	remove_action( 'wp_head', 'wp_shortlink_wp_head' );
}
add_action( 'init', 'lp_allege' );

/* Les blocs de WordPress ne servent a rien ici et leur feuille pese. */
function lp_sans_blocs() {
	wp_dequeue_style( 'wp-block-library' );
	wp_dequeue_style( 'wp-block-library-theme' );
	wp_dequeue_style( 'global-styles' );
	wp_dequeue_style( 'classic-theme-styles' );
}
add_action( 'wp_enqueue_scripts', 'lp_sans_blocs', 100 );

/* Le partage : mêmes valeurs que la version statique, ecrites une fois. */
function lp_partage() {
	$og = %%OG%%;
	$image = get_template_directory_uri() . '/partage.png';
	echo "\n";
	echo '<meta name="description" content="' . esc_attr( %%DESC%% ) . '">' . "\n";
	foreach ( $og as $prop => $valeur ) {
		echo '<meta property="' . esc_attr( $prop ) . '" content="' . esc_attr( $valeur ) . '">' . "\n";
	}
	echo '<meta property="og:image" content="' . esc_url( $image ) . '">' . "\n";
	echo '<meta property="og:image:width" content="1200">' . "\n";
	echo '<meta property="og:image:height" content="630">' . "\n";
	echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
	echo '<meta name="twitter:title" content="' . esc_attr( %%TITRE%% ) . '">' . "\n";
	echo '<meta name="twitter:image" content="' . esc_url( $image ) . '">' . "\n";
}
add_action( 'wp_head', 'lp_partage', 5 );

/*
 * Le titre du document. WordPress y colle le nom du site ; la page statique
 * portait un titre ecrit, et c'est celui-la qui a ete relu.
 */
function lp_titre( $parties ) {
	return array( 'title' => %%TITRE%% );
}
add_filter( 'document_title_parts', 'lp_titre' );
""".replace("%%VERSION%%", VERSION)
   .replace("%%OG%%", "array(\n\t\t" + ",\n\t\t".join(
       "%s => %s" % (php_chaine(k), php_chaine(v)) for k, v in og.items()) + ",\n\t)")
   .replace("%%DESC%%", php_chaine(desc))
   .replace("%%TITRE%%", php_chaine(titre)))

# index.php — la page. get_header()/get_footer() pour que les extensions et le
# futur cache de l'hebergeur trouvent wp_head()/wp_footer() la ou ils les
# attendent.
ecrire(os.path.join(SORTIE, "index.php"), """<?php
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
""" + corps.strip() + """
<?php get_footer(); ?>
""")

ecrire(os.path.join(SORTIE, "header.php"), """<?php if ( ! defined( 'ABSPATH' ) ) { exit; } ?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width,initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
""")

ecrire(os.path.join(SORTIE, "footer.php"), """<?php if ( ! defined( 'ABSPATH' ) ) { exit; } ?>
<?php wp_footer(); ?>
</body>
</html>
""")

for nom in ("app.js", "partage.png"):
    shutil.copy2(os.path.join(SOURCE, nom), os.path.join(SORTIE, nom))
os.makedirs(os.path.join(SORTIE, "data"))
shutil.copy2(os.path.join(SOURCE, "data", "menu.json"),
             os.path.join(SORTIE, "data", "menu.json"))

# ---------------------------------------------------------------------------
# 3. Controles immediats — un theme qui part casse coute un aller-retour.
theme_css = open(os.path.join(SORTIE, "style.css"), encoding="utf-8").read()
assert theme_css.count("/*") == theme_css.count("*/"), \
    "style.css : commentaires desequilibres, les regles suivantes seraient ignorees"
index_php = open(os.path.join(SORTIE, "index.php"), encoding="utf-8").read()
assert "<script" not in index_php, \
    "index.php contient encore un <script> — app.js serait charge deux fois"
assert 'id="pieHint"' in index_php or "pieHint" in index_php, \
    "index.php : le constructeur n'a pas ete extrait"

print("theme ecrit :", SORTIE)
print("  scripts retires du balisage :", nb_scripts)
print("  titre  :", titre)
print("  tailles:", len(carte["sizes"]), "| garnitures:", len(carte["toppings"]),
      "| boulangerie:", len(carte.get("bakery", [])))
