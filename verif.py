# -*- coding: utf-8 -*-
"""
Controle du theme WordPress LaParusia, AU RENDU.

Le point de la manoeuvre n'est pas « la page s'affiche ». C'est :
  1. la carte des prix se charge bien depuis le theme (le chemin change entre
     le statique et WordPress — c'est LE defaut qui tuerait le constructeur) ;
  2. l'addition affichee est celle qu'on retrouve en recalculant depuis le
     JSON, sans passer par le code de la page ;
  3. WordPress n'a rien ajoute ni casse (pas d'erreur PHP dans le corps, pas
     d'erreur JavaScript).

Usage : python3 verif.py http://127.0.0.1:8912
"""
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8912").rstrip("/")
RACINE = os.path.dirname(os.path.abspath(__file__))
CARTE = json.load(open(os.path.join(RACINE, "theme", "data", "menu.json"),
                      encoding="utf-8"))

ok, ko = 0, []


def verif(nom, condition, detail=""):
    global ok
    if condition:
        ok += 1
    else:
        ko.append((nom, detail))
        print("  ECHEC ", nom, " ", detail)


def prix_attendu(taille_key, garnitures_entieres, garnitures_par_part):
    """Recalcul INDEPENDANT depuis le JSON.

    Regle du produit : une garniture sur la pizza entiere coute son prix
    plein ; sur une part elle coute le huitieme. C'est ce rapport qui donne
    un sens a la decoupe, donc c'est lui qu'on verifie.
    """
    taille = [s for s in CARTE["sizes"] if s["key"] == taille_key][0]
    prix = {t["key"]: t["whole"] for t in CARTE["toppings"]}
    total = taille["base"]
    for g in garnitures_entieres:
        total += prix[g]
    for g in garnitures_par_part:
        total += prix[g] / 8.0
    return round(total, 2)


with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page()
    pg.set_viewport_size({"width": 1280, "height": 800})

    erreurs = []
    pg.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: erreurs.append(str(e)))

    reponses = {}
    pg.on("response", lambda r: reponses.__setitem__(r.url, r.status))

    pg.goto(BASE + "/", wait_until="networkidle")

    # --- la coquille WordPress -------------------------------------------
    corps = pg.inner_text("body")
    verif("aucune erreur PHP dans la page",
          not re.search(r"(Fatal error|Warning:|Notice:|Deprecated:)", corps),
          corps[:120])
    verif("le titre est celui ecrit, pas celui de WordPress",
          "LaParusia" in pg.title(), pg.title())

    # --- LA carte ---------------------------------------------------------
    # Le chemin de menu.json est ce qui change entre statique et WordPress.
    # On verifie qu'une requete est bien partie ET qu'elle a repondu 200.
    menus = [(u, s) for u, s in reponses.items() if "menu.json" in u]
    verif("la carte des prix est demandee", len(menus) == 1, str(menus))
    verif("la carte des prix repond 200",
          bool(menus) and menus[0][1] == 200, str(menus))
    verif("la carte est servie depuis le theme, pas la racine",
          bool(menus) and "/wp-content/themes/laparusia/" in menus[0][0],
          str(menus))
    # Controle positif du message d'erreur : s'il s'affichait, le constructeur
    # serait mort et tout le reste ci-dessous n'aurait aucun sens.
    verif("le constructeur n'affiche pas son message d'echec",
          "could not be loaded" not in corps)

    # --- ce que la carte annonce se retrouve a l'ecran ---------------------
    verif("huit parts", pg.locator("#slices .slice").count() == 8,
          str(pg.locator("#slices .slice").count()))
    verif("autant de tailles que dans la carte",
          pg.locator("#sizes button").count() == len(CARTE["sizes"]),
          f'{pg.locator("#sizes button").count()} vs {len(CARTE["sizes"])}')
    verif("autant de bases que dans la carte",
          pg.locator("#bases button").count() == len(CARTE["bases"]),
          f'{pg.locator("#bases button").count()} vs {len(CARTE["bases"])}')
    verif("autant de garnitures que dans la carte",
          pg.locator("#tops button").count() == len(CARTE["toppings"]),
          f'{pg.locator("#tops button").count()} vs {len(CARTE["toppings"])}')
    verif("autant d'items de boulangerie que dans la carte",
          pg.locator("#bakeryList li").count() == len(CARTE.get("bakery", [])),
          f'{pg.locator("#bakeryList li").count()} vs {len(CARTE.get("bakery", []))}')

    def total_affiche():
        t = pg.inner_text("#tTotal")
        return float(re.sub(r"[^0-9.]", "", t))

    # --- L'ADDITION, mode pizza entiere ------------------------------------
    # Les boutons ne portent pas de cle dans le DOM ; on les designe par leur
    # RANG, qui est celui de la carte — c'est aussi ce qui fait echouer le
    # controle si un jour l'ordre du JSON et celui de l'ecran divergent.
    i_taille, i_g1, i_g2 = 2, 1, 2             # 14 pouces, pepperoni, champignon
    taille = CARTE["sizes"][i_taille]["key"]
    g1 = CARTE["toppings"][i_g1]["key"]
    g2 = CARTE["toppings"][i_g2]["key"]

    verif("le rang des tailles a l'ecran est celui de la carte",
          pg.locator("#sizes button span").nth(i_taille).inner_text().strip()
          == CARTE["sizes"][i_taille]["label"],
          pg.locator("#sizes button span").nth(i_taille).inner_text())
    verif("le rang des garnitures a l'ecran est celui de la carte",
          pg.locator("#tops .top-name").nth(i_g1).inner_text().strip()
          == CARTE["toppings"][i_g1]["label"],
          pg.locator("#tops .top-name").nth(i_g1).inner_text())

    pg.click("#modeWhole")
    pg.wait_for_timeout(200)
    pg.locator("#sizes button").nth(i_taille).click()
    pg.locator("#tops button").nth(i_g1).click()
    pg.locator("#tops button").nth(i_g2).click()
    pg.wait_for_timeout(250)
    attendu = prix_attendu(taille, [g1, g2], [])
    verif("entiere : le total affiche est celui recalcule depuis le JSON",
          abs(total_affiche() - attendu) < 0.005,
          f"affiche {total_affiche()} vs recalcule {attendu}")

    # --- L'ADDITION, mode part par part ------------------------------------
    # Huit parts de la meme garniture doivent tomber EXACTEMENT sur le prix de
    # la pizza entiere avec cette garniture : 8 x (prix/8) = prix. C'est la
    # promesse du produit, et elle se verifie par une soustraction.
    # RECHARGEMENT. Les deux modes gardent chacun leurs choix, et l'un
    # recopie l'autre quand il est vide : enchainer les deux tests sur la meme
    # page mesurait un etat que je n'avais pas voulu, et le premier jet a
    # ainsi accuse le produit d'une erreur de 1 $ qui etait la mienne.
    pg.goto(BASE + "/", wait_until="networkidle")
    pg.wait_for_timeout(400)
    pg.locator("#sizes button").nth(i_taille).click()
    pg.wait_for_timeout(200)
    verif("part par part : la taille seule donne le prix de base",
          abs(total_affiche() - CARTE["sizes"][i_taille]["base"]) < 0.005,
          f'affiche {total_affiche()} vs base {CARTE["sizes"][i_taille]["base"]}')

    # UNE part garnie : c'est ICI que se verifie la regle du huitieme, celle
    # qui donne un sens a la decoupe. Si elle etait fausse, la page vendrait
    # une part au prix d'une pizza.
    pg.locator("#tops button").nth(i_g1).click()
    pg.wait_for_timeout(250)
    attendu_1 = prix_attendu(taille, [], [g1])
    verif("part par part : une part garnie coute le huitieme de la garniture",
          abs(total_affiche() - attendu_1) < 0.005,
          f"affiche {total_affiche()} vs recalcule {attendu_1}")

    pg.click("#allSame")
    pg.wait_for_timeout(250)
    attendu_8 = prix_attendu(taille, [], [g1] * 8)
    attendu_entiere = prix_attendu(taille, [g1], [])
    verif("part par part : huit parts identiques = la pizza entiere",
          abs(attendu_8 - attendu_entiere) < 0.005,
          f"{attendu_8} vs {attendu_entiere}")
    verif("part par part : le total affiche est celui recalcule",
          abs(total_affiche() - attendu_8) < 0.005,
          f"affiche {total_affiche()} vs recalcule {attendu_8}")
    verif("les huit parts sont comptees comme garnies",
          "8" in pg.inner_text("#tCount"), pg.inner_text("#tCount"))

    # --- changer de mode ne detruit pas les choix --------------------------
    avant = total_affiche()
    pg.click("#modeWhole"); pg.wait_for_timeout(150)
    pg.click("#modeSlices"); pg.wait_for_timeout(250)
    verif("revenir au mode part par part rend les memes choix",
          abs(total_affiche() - avant) < 0.005,
          f"{total_affiche()} vs {avant}")

    # --- aucun prix ecrit en dur dans la page ------------------------------
    # Tout montant doit venir du JSON. On cherche un prix present a l'ecran
    # qui ne serait derivable d'aucune valeur de la carte : ce serait un
    # chiffre invente, le defaut le plus cher sur une carte de restaurant.
    montants = set(re.findall(r"\$\s?([0-9]+\.[0-9]{2})", corps))
    # 0,00 $ est l'etat « rien de choisi », pas un prix. Il n'a pas a figurer
    # dans la carte pour etre legitime.
    connus = {"0.00"}
    for s in CARTE["sizes"]:
        connus.add(f"{s['base']:.2f}")
    for t in CARTE["toppings"]:
        connus.add(f"{t['whole']:.2f}")
        connus.add(f"{t['whole']/8:.2f}")
    for b in CARTE.get("bakery", []):
        connus.add(f"{b.get('price', 0):.2f}")
    inconnus = montants - connus
    verif("aucun montant a l'ecran qui ne vienne de la carte",
          not inconnus, str(sorted(inconnus)[:5]))

    verif("aucune erreur JavaScript", not erreurs, str(erreurs[:2]))

    # --- captures ---------------------------------------------------------
    D = "/var/lib/freelancer/projects/40478471/"
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
    pg.screenshot(path=D + "lpwp-1-haut.png")
    pg.evaluate("document.querySelector('#builder').scrollIntoView()")
    pg.wait_for_timeout(400)
    pg.screenshot(path=D + "lpwp-2-constructeur.png")
    pg.evaluate("document.querySelector('#bakery').scrollIntoView()")
    pg.wait_for_timeout(400)
    pg.screenshot(path=D + "lpwp-3-boulangerie.png")

    pg.set_viewport_size({"width": 390, "height": 800})
    pg.goto(BASE + "/", wait_until="networkidle")
    pg.wait_for_timeout(500)
    debord = pg.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    verif("mobile 390 px : pas de debordement horizontal", debord <= 0, str(debord))
    pg.evaluate("document.querySelector('#builder').scrollIntoView()")
    pg.wait_for_timeout(400)
    pg.screenshot(path=D + "lpwp-4-mobile.png")

    nav.close()

print(f"\n{ok + len(ko)} verifications, {len(ko)} echec(s)")
for nom, detail in ko:
    print("  -", nom, detail)
sys.exit(1 if ko else 0)
