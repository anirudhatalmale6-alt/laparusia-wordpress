<?php
/**
 * LaParusia — theme d'une seule page.
 *
 * Le principe : le balisage, le CSS et le JavaScript viennent du site
 * statique verifie. WordPress sert de coquille, il ne reecrit rien.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'LP_VERSION', '1.0.1' );

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
	$og = array(
		'og:type' => 'website',
		'og:site_name' => 'LaParusia',
		'og:locale' => 'en_CA',
		'og:title' => 'LaParusia — pizza and bakery',
		'og:description' => 'One custom pizza, or slice by slice — a different topping on each of the eight.',
	);
	$image = get_template_directory_uri() . '/partage.png';
	echo "\n";
	echo '<meta name="description" content="' . esc_attr( 'Build one custom pizza, or build it slice by slice — a different topping on each of the eight. Pick your size in inches and see the price as you go.' ) . '">' . "\n";
	foreach ( $og as $prop => $valeur ) {
		echo '<meta property="' . esc_attr( $prop ) . '" content="' . esc_attr( $valeur ) . '">' . "\n";
	}
	echo '<meta property="og:image" content="' . esc_url( $image ) . '">' . "\n";
	echo '<meta property="og:image:width" content="1200">' . "\n";
	echo '<meta property="og:image:height" content="630">' . "\n";
	echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
	echo '<meta name="twitter:title" content="' . esc_attr( 'LaParusia — pizza and bakery' ) . '">' . "\n";
	echo '<meta name="twitter:image" content="' . esc_url( $image ) . '">' . "\n";
}
add_action( 'wp_head', 'lp_partage', 5 );

/*
 * Le titre du document. WordPress y colle le nom du site ; la page statique
 * portait un titre ecrit, et c'est celui-la qui a ete relu.
 */
function lp_titre( $parties ) {
	return array( 'title' => 'LaParusia — pizza and bakery' );
}
add_filter( 'document_title_parts', 'lp_titre' );
