"""Construit le site LVA Distribution dans docs/ (servi tel quel par GitHub Pages).

Lancer : python build.py
Contenu ici ; styles dans src/site.css ; scripts dans src/site.js.
L'adresse de courriel affichée sur le site se lit dans la variable d'environnement
LVA_EMAIL (posée une fois pour toutes par l'utilisateur). Sans elle, le site se
construit sans courriel.
Les mentions légales se lisent dans mentions.json s'il existe.
"""
import datetime
import html
import json
import os
import shutil

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "docs")
DOMAINE = "https://www.lva-distribution.fr"
AUJ = datetime.date.today().isoformat()
TEL = "05 65 10 00 20"
TEL_INT = "+33565100020"
BOUTIQUE = "https://boutique.lva-distribution.fr/"
APPLI = "https://onelink.to/w3tu83"
APPSTORE = "https://apps.apple.com/fr/app/lva-distribution/id6754167450"
CATALOGUE = "https://lva-catalogue.lva-distribution.workers.dev/"
ADRESSE = ("Z.A. Les Vieilles Vignes, Le Causse", "46500", "Rignac")

e = html.escape


def lire_variable(nom):
    v = os.environ.get(nom)
    if v:
        return v.strip()
    try:  # variable posée avec setx : lue dans le registre de l'utilisateur
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return str(winreg.QueryValueEx(k, nom)[0]).strip()
    except Exception:
        return ""


MAIL = lire_variable("LVA_EMAIL")


def lire_json(nom):
    p = os.path.join(ICI, nom)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


MENTIONS = lire_json("mentions.json")

def _version():
    import hashlib
    h = hashlib.sha1()
    for f in ("src/site.css", "src/site.js"):
        with open(os.path.join(ICI, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:8]


VERSION = _version()


def a_mail(texte=None, icone=False):
    if not MAIL:
        return ""
    ic = '<svg class="ic"><use href="#i-mail"/></svg>' if icone else ""
    return f'<a href="mailto:{MAIL}">{ic}{e(texte or MAIL)}</a>'


# ---------------------------------------------------------------- données
COMMUNES = [
    ("Rocamadour", "Lot"), ("Gramat", "Lot"), ("Padirac", "Lot"), ("Alvignac", "Lot"),
    ("Lacave", "Lot"), ("Martel", "Lot"), ("Saint-Céré", "Lot"), ("Bretenoux", "Lot"),
    ("Biars-sur-Cère", "Lot"), ("Souillac", "Lot"), ("Figeac", "Lot"), ("Cahors", "Lot"),
    ("Brive-la-Gaillarde", "Corrèze"),
]
COMMUNES_CARTE = ["Rocamadour", "Gramat", "Padirac", "Lacave", "Martel", "Saint-Céré", "Bretenoux", "Biars-sur-Cère", "Figeac", "Cahors", "Brive-la-Gaillarde"]

MARQUES = [  # (nom, fichier logo ou None, fond sombre)
    ("Rougié", "rougie.svg", False), ("Elle & Vire", "elle-et-vire.svg", False), ("Président", "president.png", False),
    ("Isigny Sainte-Mère", "isigny-sainte-mere.svg", False), ("Candia", "candia.png", False), ("Bridor", "bridor.jpg", True),
    ("Vandemoortele", None, False), ("Debic", None, False), ("Callebaut", "callebaut.svg", False),
    ("Andros", "andros.png", False), ("Jean Floc'h", "jean-floch.svg", False),
]

PHOTOS_RACINE = {"viandes.webp", "fromages.webp", "charcuteries.webp", "boulangerie.webp", "bandeau-droite.webp"}
GAMMES = [  # (titre, image, texte, sous-familles)
    ("Viandes et volailles", "viandes.webp", "Bœuf, veau, agneau, porc et volailles, en pièces, portions ou prêts à cuisiner, frais ou surgelés. Les steaks hachés façon bouchère et les volailles font partie de nos meilleures ventes.", ["Bœuf", "Veau", "Agneau", "Porc", "Poulet", "Dinde", "Volailles découpées"]),
    ("Canard", "bandeau-droite.webp", "Le canard est notre premier rayon : confits, magrets, cuisses, manchons et gésiers, dont la gamme Rougié. Un incontournable des cartes du Lot et du Périgord.", ["Confits", "Magrets", "Cuisses", "Manchons", "Gésiers"]),
    ("Crèmerie et laits", None, "Beurres de cuisine, beurres pâtissiers AOP et de tourage, beurres en portions, crèmes UHT et crèmes fraîches, laits et œufs (coquille, liquides).", ["Beurres de cuisine", "Beurres pâtissiers", "Beurres portions", "Crèmes", "Laits", "Œufs"]),
    ("Fromages", "fromages.webp", "Fromages à la coupe, en portions, râpés et tranchés, dont le Rocamadour AOP et les grands classiques pour la cuisine, le plateau et la pizza.", ["À la coupe", "Portions", "Râpés", "Tranchés", "Rocamadour AOP"]),
    ("Charcuteries", "charcuteries.webp", "Jambons, lards, saucissons et spécialités, tranchés ou à la coupe, pour la cuisine, le snacking et les planches.", ["Charcuterie tranchée", "Charcuterie à la coupe", "Saucisses"]),
    ("Boulangerie et viennoiserie", "boulangerie.webp", "Pains précuits, viennoiseries crues ou cuites, pâtes feuilletées et prêts à garnir, avec des marques comme Bridor et Vandemoortele.", ["Pains", "Viennoiseries", "Pâtes feuilletées", "Prêts à garnir"]),
    ("Ingrédients boulangerie-pâtisserie", None, "Sucres, levures, chocolats de couverture, arômes, purées de fruits et fruits secs pour les boulangers, pâtissiers et cuisiniers.", ["Sucres et sels", "Épices", "Chocolat", "Fruits secs"]),
    ("Plats cuisinés", "plats.webp", "Plats prêts à réchauffer et spécialités pour gagner du temps en service, en cantine comme en restauration rapide.", ["Plats du terroir", "Plats à partager"]),
    ("Légumes et accompagnements", "accompagnements.webp", "Légumes et herbes, champignons, féculents, sauces et préparations, en conserve, surgelés ou prêts à l'emploi.", ["Légumes et herbes", "Champignons", "Féculents", "Sauces"]),
    ("Desserts et glaces", "desserts.webp", "Yaourts, fromages blancs, compotes, purées de fruits et desserts glacés, en formats individuels ou restauration.", ["Yaourts", "Fromages blancs", "Compotes", "Glaces"]),
    ("Boissons", "boissons.webp", "Jus de fruits (bouteilles et BIB), eaux, cafés, jus pour cocktails, vins et bières pour les bars, hôtels et restaurants.", ["Jus de fruits", "Eaux", "Café", "Vins", "Bières"]),
    ("Épicerie, huiles et confitures", "huiles.webp", "Huiles, vinaigres, confitures, miels, pâtes à tartiner, gâteaux et confiseries : toute l'épicerie salée et sucrée.", ["Huiles", "Vinaigres", "Confitures", "Miels", "Confiseries"]),
    ("Emballages et hygiène", "emballages.webp", "Barquettes, sacs, serviettes, produits d'entretien et petits matériels pour la cuisine et la salle.", ["Emballages", "Hygiène", "Fournitures"]),
]

FAQ_ACCUEIL = [
    ("Qui peut commander chez LVA Distribution ?", "Tout le monde : restaurants, boulangeries et pâtisseries, hôtels et campings, cafés et bars, collectivités, traiteurs, boucheries, charcuteries et épiceries, mais aussi les particuliers. L'ouverture d'un compte se fait sur simple demande, par téléphone au 05 65 10 00 20 ou par le formulaire de contact."),
    ("Dans quels secteurs livrez-vous ?", "Nous livrons depuis notre entrepôt de Rignac, à côté de Gramat : le Lot et au-delà (Rocamadour, Gramat, Padirac, Saint-Céré, Martel, Bretenoux, Biars-sur-Cère, Souillac, Figeac, Cahors…), ainsi que Brive-la-Gaillarde et la Corrèze."),
    ("Combien de fois par semaine livrez-vous ?", "Nous livrons plusieurs fois par semaine, en tournées fixes. Les jours de passage dépendent de votre secteur : nous consulter."),
    ("Comment passer commande ?", "Trois possibilités : par téléphone avec notre équipe de télévente, sur la boutique en ligne boutique.lva-distribution.fr (24h/24), ou sur l'application LVA Distribution (iPhone et Android). Vos tarifs personnalisés s'appliquent partout."),
    ("Quels produits proposez-vous ?", "Plus de 4 000 références : viandes et volailles, canard, crèmerie, fromages, charcuterie, boulangerie et viennoiserie, surgelés, épicerie, boissons, emballages et produits d'hygiène."),
    ("Quelles marques distribuez-vous ?", "Nous travaillons notamment avec Rougié, Elle & Vire, Président, Isigny Sainte-Mère, Candia, Debic, Bridor, Vandemoortele, Callebaut, Andros et Jean Floc'h, ainsi qu'avec des producteurs régionaux comme le Rocamadour AOP."),
]
FAQ_LIVRAISON = [
    ("Livrez-vous chez moi ?", "Si vous êtes dans le Lot, à Brive ou en Corrèze, très probablement. Sinon, appelez-nous au 05 65 10 00 20 : nous regardons ensemble la tournée la plus proche."),
    ("Quels jours passez-vous ?", "Nos tournées sont fixes et passent plusieurs fois par semaine. Les jours dépendent de votre secteur : nous consulter."),
    ("Comment la chaîne du froid est-elle respectée ?", "Nous livrons avec nos propres camions frigorifiques. Les produits frais et surgelés restent au froid de notre entrepôt de Rignac jusqu'à votre chambre froide."),
    ("Puis-je être livré en saison seulement ?", "Oui. Beaucoup de nos clients travaillent avec le tourisme (Rocamadour, Padirac, vallée de la Dordogne) et ne commandent qu'une partie de l'année. Nous adaptons les passages à votre activité."),
]
FAQ_COMMANDE = [
    ("Comment ouvrir un compte ?", "Remplissez le formulaire de contact ou appelez le 05 65 10 00 20. Un commercial vous rappelle, vous présente nos tarifs et ouvre votre compte. Vous recevez ensuite vos accès à la boutique en ligne et à l'application."),
    ("Les prix sont-ils affichés sur le site ?", "Nos tarifs sont personnalisés. Ils s'affichent sur la boutique en ligne et dans l'application une fois votre compte ouvert."),
    ("Puis-je commander le soir ou le week-end ?", "Oui, la boutique en ligne et l'application sont accessibles 24h/24 et 7j/7. La commande part avec la prochaine tournée de votre secteur."),
    ("Puis-je garder un interlocuteur au téléphone ?", "Oui. Notre équipe de télévente vous appelle au jour convenu pour prendre votre commande et vous signaler les promotions et les nouveautés."),
]

# ---------------------------------------------------------------- morceaux communs
ICONES = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-tel" viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></symbol>
  <symbol id="i-mail" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></symbol>
  <symbol id="i-lieu" viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></symbol>
  <symbol id="i-panier" viewBox="0 0 24 24"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/></symbol>
  <symbol id="i-fleche" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
  <symbol id="i-livre" viewBox="0 0 24 24"><path d="M2 4h7a3 3 0 0 1 3 3v14a2 2 0 0 0-2-2H2zM22 4h-7a3 3 0 0 0-3 3v14a2 2 0 0 1 2-2h8z"/></symbol>
  <symbol id="i-camion" viewBox="0 0 24 24"><path d="M1 4h14v11H1zM15 8h4l3 3v4h-7z"/><circle cx="5.5" cy="18" r="2"/><circle cx="18.5" cy="18" r="2"/></symbol>
  <symbol id="i-menu" viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18"/></symbol>
  <symbol id="i-croix" viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></symbol>
  <symbol id="i-resto" viewBox="0 0 24 24"><path d="M3 2v7a3 3 0 0 0 3 3v10M9 2v7a3 3 0 0 1-3 3M6 2v7M18 22V2c-2.5 1-4 3.5-4 7v4h4"/></symbol>
  <symbol id="i-hotel" viewBox="0 0 24 24"><path d="M2 20V8M22 20v-6a3 3 0 0 0-3-3H10v6M2 17h20"/><circle cx="6" cy="12" r="2"/></symbol>
  <symbol id="i-cafe" viewBox="0 0 24 24"><path d="M17 8h1a4 4 0 0 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4zM6 2v3M10 2v3M14 2v3"/></symbol>
  <symbol id="i-pain" viewBox="0 0 24 24"><path d="M5 11a4 4 0 0 1 0-8h14a4 4 0 0 1 0 8v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z"/><path d="M9 3v4M15 3v4"/></symbol>
  <symbol id="i-ecole" viewBox="0 0 24 24"><path d="M3 21h18M5 21V10l7-5 7 5v11M10 21v-6h4v6"/></symbol>
  <symbol id="i-toque" viewBox="0 0 24 24"><path d="M6 14a4 4 0 0 1-.6-8 5 5 0 0 1 9.2-1.6A4 4 0 1 1 18 14M6 14h12v6H6z"/></symbol>
  <symbol id="i-apple" viewBox="0 0 24 24"><path d="M16.4 12.6c0-2.4 2-3.6 2.1-3.6-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.1 1-4 2.4-1.7 3-.4 7.3 1.2 9.7.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.2-.8s1.9.8 3.2.8c1.3 0 2.2-1.2 3-2.4.9-1.4 1.3-2.7 1.3-2.8 0 0-2.6-1-2.6-3.9zM14 5.5c.7-.8 1.1-1.9 1-3-1 0-2.1.7-2.8 1.5-.6.7-1.2 1.8-1 2.9 1 .1 2.1-.6 2.8-1.4z"/></symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><path d="M4 2.6v18.8c0 .4.4.7.8.5L21 12.5c.4-.2.4-.8 0-1L4.8 2.1c-.4-.2-.8.1-.8.5z"/></symbol>
</svg>"""

NAV = [("produits/", "Nos produits"), ("livraison/", "Livraison"), ("commander/", "Commander"), ("qui-sommes-nous/", "Qui sommes-nous"), ("contact/", "Contact")]

ORGA_ID = DOMAINE + "/#entreprise"
ORGA = {
    "@type": ["WholesaleStore", "Organization"],
    "@id": ORGA_ID,
    "name": "LVA Distribution",
    "slogan": "Distributeur de saveurs",
    "description": "Grossiste alimentaire pour les professionnels de la restauration et des métiers de bouche dans le Lot et en Corrèze : plus de 4 000 références en frais, surgelé et épicerie, livrées en camions frigorifiques.",
    "url": DOMAINE + "/",
    "logo": DOMAINE + "/assets/img/logo-lva.png",
    "image": DOMAINE + "/assets/img/partage.jpg",
    "telephone": TEL_INT,
    "address": {"@type": "PostalAddress", "streetAddress": ADRESSE[0], "postalCode": ADRESSE[1], "addressLocality": ADRESSE[2], "addressRegion": "Occitanie", "addressCountry": "FR"},
    "geo": {"@type": "GeoCoordinates", "latitude": 44.808, "longitude": 1.693},
    "areaServed": [{"@type": "City", "name": c} for c, _ in COMMUNES] + [{"@type": "AdministrativeArea", "name": n} for n in ("Lot", "Corrèze")],
    "knowsAbout": [g[0] for g in GAMMES],
    "sameAs": [APPSTORE],
    "potentialAction": {"@type": "OrderAction", "target": BOUTIQUE},
}
if MAIL:
    ORGA["email"] = MAIL
for cle_ld, cle in (("vatID", "tva"), ("taxID", "siren")):
    if MENTIONS.get(cle):
        ORGA[cle_ld] = MENTIONS[cle]


def ld(*objets):
    graphe = {"@context": "https://schema.org", "@graph": list(objets)}
    return '<script type="application/ld+json">' + json.dumps(graphe, ensure_ascii=False, separators=(",", ":")) + "</script>"


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}


def ariane_ld(chemin):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAINE + "/" + u} for i, (u, n) in enumerate(chemin)]}


def faq_html(faq):
    return '<div class="faq">' + "".join(f'<details><summary>{e(q)}</summary><div class="reponse"><p>{e(r)}</p></div></details>' for q, r in faq) + "</div>"


def ariane(r, chemin):
    items = []
    for i, (u, n) in enumerate(chemin):
        if i == len(chemin) - 1:
            items.append(f'<li aria-current="page">{e(n)}</li>')
        else:
            items.append(f'<li><a href="{(r + u) or "./"}">{e(n)}</a></li>')
    return '<nav class="ariane" aria-label="Fil d\'Ariane"><ol>' + "".join(items) + "</ol></nav>"


def pied(r):
    accueil = r or "./"
    ligne_mail = ("<br>" + a_mail()) if MAIL else ""
    return f"""<footer class="pied">
  <div class="cadre">
    <div class="pied-grille">
      <div>
        <a href="{accueil}"><img src="{r}assets/img/logo-lva.png" alt="LVA Distribution" width="480" height="363" loading="lazy"></a>
        <p>Grossiste alimentaire des professionnels de la restauration dans le Lot et en Corrèze.</p>
      </div>
      <div>
        <h2>Nous trouver</h2>
        <address>LVA Distribution<br>{ADRESSE[0]}<br>{ADRESSE[1]} {ADRESSE[2]}<br><a href="tel:{TEL_INT}">{TEL}</a>{ligne_mail}</address>
      </div>
      <div>
        <h2>Le site</h2>
        <ul>{''.join(f'<li><a href="{r}{u}">{e(n)}</a></li>' for u, n in NAV)}</ul>
      </div>
      <div>
        <h2>Commander</h2>
        <ul><li><a href="{BOUTIQUE}" rel="noopener">Boutique en ligne</a></li><li><a href="{APPLI}" rel="noopener">Application mobile</a></li><li><a href="{CATALOGUE}" rel="noopener">Catalogue 2026</a></li><li><a href="{r}contact/">Devenir client</a></li></ul>
      </div>
    </div>
    <div class="bas">
      <span>© <span id="annee">{datetime.date.today().year}</span> LVA Distribution · Rignac, Lot</span>
      <a href="{r}mentions-legales/">Mentions légales</a>
    </div>
  </div>
</footer>"""


def page(chemin_fichier, titre, description, corps, r, actif=None, schemas=(), accueil=False, indexer=True, canonique=None):
    url = canonique or (DOMAINE + "/" + ("" if chemin_fichier == "index.html" else chemin_fichier.replace("index.html", "")))
    nav = "".join(f'<a href="{r}{u}"' + (' aria-current="page"' if u == actif else "") + f">{e(n)}</a>" for u, n in NAV)
    site = {"@type": "WebSite", "@id": DOMAINE + "/#site", "url": DOMAINE + "/", "name": "LVA Distribution", "inLanguage": "fr-FR", "publisher": {"@id": ORGA_ID}}
    webpage = {"@type": "WebPage", "@id": url + "#page", "url": url, "name": titre, "description": description, "inLanguage": "fr-FR", "isPartOf": {"@id": DOMAINE + "/#site"}, "about": {"@id": ORGA_ID}, "dateModified": AUJ}
    precharge = ""
    if accueil:
        image_hero = "video/hero-cuisine.jpg" if chemin_fichier.startswith("video/") else "img/hero-farine.webp"
        precharge = f'<link rel="preload" href="{r}assets/{image_hero}" as="image" fetchpriority="high">' + "\n"
    robots = "index, follow, max-image-preview:large" if indexer else "noindex"
    doc = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0e0e0e">
<meta name="geo.region" content="FR-46">
<meta name="geo.placename" content="Rignac">
<meta name="geo.position" content="44.808;1.693">
<meta name="ICBM" content="44.808, 1.693">
<meta property="og:type" content="website">
<meta property="og:site_name" content="LVA Distribution">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="{e(titre)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAINE}/assets/img/partage.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<link rel="preload" href="{r}assets/fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
{precharge}<link rel="stylesheet" href="{r}assets/site.css?v={VERSION}">
<script>document.documentElement.classList.add('js')</script>
{ld(ORGA, site, webpage, *schemas)}
</head>
<body>
{ICONES}
<a class="masque" href="#contenu">Aller au contenu</a>
<header class="entete{'' if accueil else ' toujours'}" id="entete">
  <div class="contact-haut"><div class="cadre">
    <a href="tel:{TEL_INT}"><svg class="ic"><use href="#i-tel"/></svg>{TEL}</a>
    {a_mail(icone=True)}
  </div></div>
  <div class="cadre barre">
    <a class="marque" href="{r or './'}" aria-label="LVA Distribution, accueil"><img src="{r}assets/img/logo-lva.png" alt="LVA Distribution, grossiste alimentaire" width="480" height="363"></a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="nav" aria-label="Ouvrir le menu"><svg class="ic"><use href="#i-menu"/></svg></button>
    <nav class="nav" id="nav" aria-label="Menu principal">
      {nav}
      <div class="nav-mobile">
        <a class="btn btn-rouge" href="{BOUTIQUE}" rel="noopener">Espace client</a>
        <a class="btn btn-ligne" href="tel:{TEL_INT}">{TEL}</a>
      </div>
    </nav>
    <a class="btn btn-rouge" href="{BOUTIQUE}" rel="noopener"><svg class="ic"><use href="#i-panier"/></svg>Espace client</a>
  </div>
</header>
<main id="contenu">
{corps}
</main>
{pied(r)}
<script src="{r}assets/site.js?v={VERSION}" defer></script>
</body>
</html>
"""
    cible = os.path.join(SORTIE, chemin_fichier)
    os.makedirs(os.path.dirname(cible), exist_ok=True)
    with open(cible, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    return url


def carte():
    villes = [("Brive-la-Gaillarde", 187, 50, 196, 55, "start"), ("Martel", 217, 174, 209, 170, "end"), ("Bretenoux · Biars", 312, 179, 320, 178, "start"),
              ("Saint-Céré", 329, 215, 337, 219, "start"), ("Padirac", 271, 226, 271, 211, "middle"), ("Lacave", 195, 225, 187, 222, "end"),
              ("Rocamadour", 220, 250, 211, 258, "end"), ("Gramat", 263, 260, 271, 272, "start"), ("Figeac", 383, 356, 391, 361, "start"), ("Cahors", 151, 445, 159, 450, "start")]
    pts = "".join(f'<circle cx="{cx}" cy="{cy}" r="5"/><text x="{tx}" y="{ty}" text-anchor="{a}">{e(n)}</text>' for n, cx, cy, tx, ty, a in villes)
    return f"""<figure class="carte">
  <svg viewBox="0 0 500 500" role="img" aria-labelledby="carte-titre">
    <title id="carte-titre">Carte des principaux secteurs livrés autour de l'entrepôt LVA Distribution de Rignac : {e(', '.join(COMMUNES_CARTE))}</title>
    <defs><pattern id="points" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#1f1f1f"/></pattern></defs>
    <rect width="500" height="500" fill="url(#points)"/>
    <circle cx="250" cy="245" r="200" class="anneau"/><circle cx="250" cy="245" r="100" class="anneau"/>
    <text class="km" x="352" y="241">20 km</text><text class="km" x="452" y="241">40 km</text>
    <text class="dep" x="330" y="96">CORRÈZE</text><text class="dep" x="28" y="190">DORDOGNE</text><text class="dep" x="410" y="140">CANTAL</text><text class="dep" x="265" y="330">LOT</text><text class="dep" x="400" y="455">AVEYRON</text>
    <g class="ville">{pts}<circle cx="308" cy="186" r="4"/></g>
    <circle cx="250" cy="245" r="15" class="halo"/><circle cx="250" cy="245" r="8" class="entrepot"/>
  </svg>
  <figcaption class="legende"><span><i style="background:var(--rouge)"></i>Entrepôt LVA Distribution, Rignac</span><span><i style="background:var(--blanc)"></i>Principaux secteurs livrés</span></figcaption>
</figure>"""


def bande_marques(r):
    def cartes(cache):
        out = []
        for nom, f, sombre in MARQUES:
            alt = "" if cache else e(nom)
            contenu = f'<img src="{r}assets/img/marques/{f}" alt="{alt}" loading="lazy">' if f else f'<span class="mot">{e(nom)}</span>'
            masque = ' aria-hidden="true"' if cache else ""
            out.append(f'<div class="logo-marque{" sombre" if sombre else ""}"{masque}>{contenu}</div>')
        return "".join(out)
    return f"""<section class="marques" aria-labelledby="titre-marques">
  <div class="cadre tete"><span class="surtitre">Nos marques</span><h2 class="titre" id="titre-marques">Les marques que nous distribuons</h2>
  <p class="chapo">Les grandes marques de la restauration et des producteurs de la région, réunis dans une seule commande.</p></div>
  <div class="marques-fenetre"><div class="marques-piste">{cartes(False)}{cartes(True)}</div></div>
</section>"""


def bande_familles():
    mots = ["Viandes", "Canard", "Fromages", "Crèmerie", "Charcuteries", "Boulangerie", "Surgelés", "Épicerie", "Boissons", "Desserts", "Emballages"]
    s = "".join(("<span class=\"creux\">" if i % 2 else "<span>") + f"{m}</span><i>✦</i>" for i, m in enumerate(mots))
    return f'<div class="defile" aria-hidden="true"><div class="defile-piste">{s}{s}</div></div>'


def canaux():
    return f"""<div class="canaux">
  <article class="canal"><span class="num">01</span><h3>Par téléphone</h3><p>Notre équipe de télévente vous appelle au jour convenu pour prendre votre commande et vous signaler les promotions et nouveautés. Vous pouvez aussi nous appeler.</p><a class="lien" href="tel:{TEL_INT}"><svg class="ic"><use href="#i-tel"/></svg>{TEL}</a></article>
  <article class="canal"><span class="num">02</span><h3>Sur la boutique en ligne</h3><p>Commandez 24h/24 depuis votre ordinateur : cadencier, historique d'achats, promotions, suivi des commandes et des factures.</p><a class="lien" href="{BOUTIQUE}" rel="noopener">boutique.lva-distribution.fr <svg class="ic"><use href="#i-fleche"/></svg></a></article>
  <article class="canal"><span class="num">03</span><h3>Sur l'application</h3><p>Toute la boutique dans votre poche : recommandez vos articles habituels en un clic, depuis la cuisine ou la réserve.</p><div class="stores"><a href="{APPSTORE}" rel="noopener"><svg><use href="#i-apple"/></svg>App Store</a><a href="{APPLI}" rel="noopener"><svg><use href="#i-play"/></svg>Google Play</a></div></article>
</div>"""


def formulaire():
    return """<form class="formulaire" id="formulaire" novalidate>
  <h2>Devenir client</h2>
  <p>Votre demande part dans votre messagerie, adressée à notre équipe. Un commercial vous rappelle.</p>
  <div class="champs">
    <div class="champ"><label for="f-nom">Nom et prénom</label><input id="f-nom" name="nom" autocomplete="name" required></div>
    <div class="champ"><label for="f-etab">Établissement</label><input id="f-etab" name="etablissement" autocomplete="organization" required></div>
    <div class="champ"><label for="f-tel">Téléphone</label><input id="f-tel" name="telephone" type="tel" autocomplete="tel" inputmode="tel" required></div>
    <div class="champ"><label for="f-ville">Ville</label><input id="f-ville" name="commune" autocomplete="address-level2"></div>
    <div class="champ large"><label for="f-type">Votre activité</label><select id="f-type" name="activite"><option>Restaurant</option><option>Boulangerie ou pâtisserie</option><option>Hôtel ou camping</option><option>Café, bar ou snacking</option><option>Collectivité</option><option>Traiteur, boucherie ou épicerie</option><option>Autre</option></select></div>
    <div class="champ large"><label for="f-msg">Votre message (facultatif)</label><textarea id="f-msg" name="message" placeholder="Date d'ouverture, produits recherchés, jours de livraison souhaités…"></textarea></div>
  </div>
  <button class="btn btn-rouge" type="submit">Envoyer ma demande <svg class="ic"><use href="#i-fleche"/></svg></button>
  <p class="note" id="f-note" role="status">Ou appelez-nous directement au 05 65 10 00 20.</p>
</form>"""


def appel(r, titre="Ouvrons votre compte", texte="Un commercial vous rappelle, vous présente nos tarifs et organise votre première livraison."):
    return f"""<section class="appel"><div class="cadre"><h2 class="titre">{e(titre)}</h2><p class="chapo">{e(texte)}</p>
<div class="actions"><a class="btn btn-rouge" href="{r}contact/">Devenir client <svg class="ic"><use href="#i-fleche"/></svg></a><a class="btn btn-ligne" href="tel:{TEL_INT}"><svg class="ic"><use href="#i-tel"/></svg>{TEL}</a></div></div></section>"""


def tete_page(r, chemin, surtitre, h1, chapo, photo=None):
    style = f" style=\"--photo:url('{r}assets/img/{photo}')\"" if photo else ""
    return f"""<section class="tete-page{' avec-photo' if photo else ''}"{style}><div class="cadre">
{ariane(r, chemin)}
<span class="surtitre">{e(surtitre)}</span>
<h1 class="titre">{e(h1)}</h1>
<p class="chapo">{chapo}</p>
</div></section>"""


# ---------------------------------------------------------------- pages
def accueil(variante="photo"):
    r = "" if variante == "photo" else "../"
    publics = [
        ("i-resto", "Restaurants", "Viandes, volailles, fromages, crèmerie, plats cuisinés et desserts."),
        ("i-pain", "Boulangeries et pâtisseries", "Beurres, ingrédients techniques, chocolat, viennoiseries et prêts à garnir."),
        ("i-hotel", "Hôtels et campings", "Petits-déjeuners, viennoiseries, jus de fruits, boissons et snacking."),
        ("i-cafe", "Cafés, bars et snacking", "Boissons, café, glaces, snacking et tout le nécessaire du comptoir."),
        ("i-ecole", "Collectivités", "Grands conditionnements, viandes, produits laitiers, surgelés et épicerie."),
        ("i-toque", "Traiteurs, boucheries, épiceries", "Charcuteries, fromages à la coupe, crèmerie, plats cuisinés et emballages."),
    ]
    pub = "".join(f'<div class="public"><svg class="ic"><use href="#{i}"/></svg><h3>{e(t)}</h3><p>{e(p)}</p></div>' for i, t, p in publics)
    if variante == "video":
        entree = f"""<section class="une une-video" id="accueil">
  <div class="une-film"><video autoplay muted loop playsinline preload="auto" poster="{r}assets/video/hero-cuisine.jpg" aria-hidden="true"><source src="{r}assets/video/hero-cuisine-1080.mp4" type="video/mp4" media="(min-width: 900px)"><source src="{r}assets/video/hero-cuisine-720.mp4" type="video/mp4"></video></div>
"""
    else:
        entree = f"""<section class="une" id="accueil">
  <div class="une-photo" data-parallaxe><img src="{r}assets/img/hero-farine.webp" alt="Les mains d'un cuisinier laissent tomber de la farine sur fond noir" width="1400" height="836" fetchpriority="high"></div>
"""
    corps = f"""
{entree}  <div class="cadre une-texte">
    <span class="surtitre">Grossiste alimentaire · Lot &amp; Corrèze</span>
    <h1 class="titre"><span class="masque">LVA Distribution, grossiste alimentaire à Rignac dans le Lot : </span><span class="ligne"><span style="--d:.35s">Distributeur</span></span><span class="ligne rouge"><span style="--d:.5s">de saveurs</span></span></h1>
    <p class="accroche">Restaurants, hôtels, boulangeries, pâtisseries, traiteurs, boucheries, charcuteries, collectivités, etc. : votre grossiste dans le Lot et au-delà, livré par nos propres camions frigorifiques.</p>
    <div class="actions">
      <a class="btn btn-rouge" href="{r}contact/">Devenir client <svg class="ic"><use href="#i-fleche"/></svg></a>
      <a class="btn btn-ligne" href="{CATALOGUE}" rel="noopener"><svg class="ic"><use href="#i-livre"/></svg>Feuilleter le catalogue</a>
    </div>
  </div>
</section>
<section class="atouts" aria-label="LVA Distribution en bref">
  <ul class="cadre">
    <li><strong data-compte="4000" data-suffixe="+">4&nbsp;000+</strong><span>références</span></li>
    <li><strong data-compte="700" data-suffixe="+">700+</strong><span>professionnels livrés</span></li>
    <li><strong>24h/24</strong><span>commande en ligne</span></li>
    <li><strong data-compte="20" data-suffixe=" ans+">20 ans+</strong><span>d'expérience</span></li>
  </ul>
</section>
{bande_familles()}
<section class="section" id="clients">
  <div class="cadre">
    <span class="surtitre">Pour qui</span>
    <h2 class="titre">Le spécialiste<br>des professionnels</h2>
    <p class="chapo">Depuis plus de 20 ans, LVA Distribution accompagne tous les métiers de bouche du Lot et de la Corrèze. Un partenaire local et réactif, avec les outils d'aujourd'hui : commande en ligne 24h/24, application mobile et télévente dédiée.</p>
    <div class="publics">{pub}</div>
  </div>
</section>
<section class="section section-fonce" id="produits">
  <div class="cadre">
    <span class="surtitre">Nos produits</span>
    <h2 class="titre">Tout pour votre cuisine</h2>
    <p class="chapo">Du frais au surgelé, de l'épicerie aux emballages : une seule commande, une seule livraison. Le frais est notre cœur de métier.</p>
    <div class="mosaique">
      <figure class="tuile"><img src="{r}assets/img/viandes.webp" alt="Pièces de bœuf grillées sur une ardoise" loading="lazy" width="700" height="700"><figcaption><b>Viandes</b><span>Bœuf, veau, agneau, porc, volaille</span></figcaption></figure>
      <figure class="tuile"><img src="{r}assets/img/fromages.webp" alt="Plateau de fromages et verre de vin rouge" loading="lazy" width="700" height="700"><figcaption><b>Fromages</b><span>Coupe, portions, râpés, Rocamadour AOP</span></figcaption></figure>
      <figure class="tuile"><img src="{r}assets/img/charcuteries.webp" alt="Tranches de jambon et de lard sur une planche" loading="lazy" width="700" height="700"><figcaption><b>Charcuteries</b><span>Tranchées et à la coupe</span></figcaption></figure>
      <figure class="tuile"><img src="{r}assets/img/boulangerie.webp" alt="Croissants dorés sur une plaque" loading="lazy" width="540" height="465"><figcaption><b>Boulangerie</b><span>Pains, viennoiseries, prêts à garnir</span></figcaption></figure>
      <figure class="tuile"><img src="{r}assets/img/bandeau-droite.webp" alt="Magret de canard tranché et grains de poivre" loading="lazy" width="378" height="1350" style="object-position:50% 70%"><figcaption><b>Canard</b><span>Magrets, cuisses, confits</span></figcaption></figure>
    </div>
    <div class="pied-section">
      <a class="btn btn-rouge" href="{r}produits/">Voir toutes nos gammes <svg class="ic"><use href="#i-fleche"/></svg></a>
      <a class="btn btn-ligne" href="{CATALOGUE}" rel="noopener"><svg class="ic"><use href="#i-livre"/></svg>Catalogue 2026</a>
    </div>
  </div>
</section>
{bande_marques(r)}
<section class="section" id="commander">
  <div class="cadre">
    <span class="surtitre">Commander</span>
    <h2 class="titre">Comme vous préférez</h2>
    <p class="chapo">Par téléphone avec votre interlocuteur habituel, ou en ligne à n'importe quelle heure. Vos tarifs personnalisés s'appliquent partout.</p>
    {canaux()}
    <p class="livraison"><svg class="ic"><use href="#i-camion"/></svg><span><b>Livré par nos propres camions frigorifiques</b>, sur des tournées fixes, plusieurs fois par semaine selon votre secteur : nous consulter. La chaîne du froid est tenue de notre entrepôt jusqu'à votre chambre froide.</span></p>
  </div>
</section>
<section class="section section-fonce" id="zone">
  <div class="cadre zone-grille">
    {carte()}
    <div>
      <span class="surtitre">Zone de livraison</span>
      <h2 class="titre">Votre grossiste local</h2>
      <p class="chapo">Depuis notre entrepôt de Rignac, à côté de Gramat, nos camions livrent les professionnels du Lot et du bassin de Brive, au cœur de la vallée de la Dordogne.</p>
      <ul class="zones-liste">
        <li><b>Le Lot, et au-delà</b><span>Rocamadour, Gramat, Padirac, Saint-Céré, Martel, Bretenoux, Souillac, jusqu'à Figeac et Cahors.</span></li>
        <li><b>Brive et la Corrèze</b><span>Brive-la-Gaillarde et son bassin.</span></li>
      </ul>
      <p style="margin-top:30px"><a class="btn btn-ligne" href="{r}livraison/">Tout sur la livraison <svg class="ic"><use href="#i-fleche"/></svg></a></p>
    </div>
  </div>
</section>
<section class="section" id="questions">
  <div class="cadre etroit">
    <span class="surtitre">Questions fréquentes</span>
    <h2 class="titre">Vos questions</h2>
    {faq_html(FAQ_ACCUEIL)}
  </div>
</section>
{appel(r)}
"""
    fichier = "index.html" if variante == "photo" else "video/index.html"
    return page(fichier, "LVA Distribution · Grossiste alimentaire pour professionnels, Lot et Corrèze",
                "Grossiste alimentaire à Rignac (Lot) : plus de 4 000 références en frais, surgelé et épicerie pour restaurants, boulangeries, hôtels et collectivités. Livraison en camions frigorifiques dans le Lot et en Corrèze.",
                corps, r, schemas=[faq_ld(FAQ_ACCUEIL)], accueil=True, indexer=(variante == "photo"), canonique=DOMAINE + "/")


def produits():
    r = "../"
    chemin = [("", "Accueil"), ("produits/", "Nos produits")]
    cartes = []
    for titre, img, texte, subs in GAMMES:
        vis = ""
        if img:
            dossier = "" if img in PHOTOS_RACINE else "univers/"
            pos = ' style="object-position:50% 78%"' if img == "bandeau-droite.webp" else ""
            vis = f'<div class="visuel"><img src="{r}assets/img/{dossier}{img}" alt="{e(titre)} chez LVA Distribution" loading="lazy"{pos}></div>'
        puces = "".join(f"<li>{e(s)}</li>" for s in subs)
        cartes.append(f'<article class="gamme">{vis}<div class="corps"><h2>{e(titre)}</h2><p>{e(texte)}</p><ul>{puces}</ul></div></article>')
    catalogue = {"@type": "OfferCatalog", "name": "Gammes LVA Distribution", "itemListElement": [{"@type": "OfferCatalog", "name": t, "description": tx} for t, _, tx, _ in GAMMES]}
    corps = f"""
{tete_page(r, chemin, "Nos produits", "Plus de 4 000 références pour les professionnels", "Viandes, canard, crèmerie, fromages, charcuterie, boulangerie, surgelés, épicerie, boissons et emballages : LVA Distribution réunit tout ce dont une cuisine professionnelle a besoin, livré par une seule tournée.", "fromages.webp")}
<section class="section">
  <div class="cadre">
    <span class="surtitre">Nos gammes</span>
    <h2 class="titre">Treize univers, une seule commande</h2>
    <p class="chapo">Le frais représente près de 70 % de nos ventes. Chaque gamme est présentée en détail, avec les conditionnements, dans notre <a href="{CATALOGUE}" rel="noopener">catalogue 2026 en ligne</a>.</p>
    <div class="gammes">{''.join(cartes)}</div>
  </div>
</section>
{bande_marques(r)}
<section class="section section-fonce">
  <div class="cadre etroit prose">
    <h2 class="titre">Des grandes marques et des produits du terroir</h2>
    <p>LVA Distribution travaille avec les grandes marques de la restauration hors domicile : Rougié pour le canard ; Elle &amp; Vire, Président, Isigny Sainte-Mère, Candia et Debic pour la crèmerie ; Bridor et Vandemoortele pour la boulangerie ; Callebaut pour le chocolat ; Andros pour les fruits ; Jean Floc'h pour la charcuterie.</p>
    <p>Nous distribuons aussi des produits de la région, comme le Rocamadour AOP, l'un des fromages les plus demandés par les restaurants du Lot.</p>
    <p>Vous ne trouvez pas une référence ? Demandez-la à votre interlocuteur ou au <a href="tel:{TEL_INT}">{TEL}</a> : nous pouvons souvent la commander pour vous.</p>
  </div>
</section>
{appel(r, "Recevez nos tarifs", "Ouvrez votre compte : vos prix s'affichent ensuite sur la boutique en ligne et dans l'application.")}
"""
    return page("produits/index.html", "Produits alimentaires pour professionnels : frais, surgelé, épicerie · LVA Distribution",
                "Viandes, canard, crèmerie, fromages, charcuterie, boulangerie, surgelés, épicerie, boissons et emballages : plus de 4 000 références pour la restauration, livrées dans le Lot et en Corrèze.",
                corps, r, actif="produits/", schemas=[ariane_ld(chemin), catalogue])


def livraison():
    r = "../"
    chemin = [("", "Accueil"), ("livraison/", "Livraison")]
    communes = "".join(f"<li>{e(c)}<small>{e(d)}</small></li>" for c, d in COMMUNES)
    corps = f"""
{tete_page(r, chemin, "Zone de livraison", "Livraison des professionnels dans le Lot et en Corrèze", "LVA Distribution livre les restaurants, boulangeries, hôtels et collectivités depuis son entrepôt de Rignac, à côté de Gramat, avec ses propres camions frigorifiques.")}
<section class="section">
  <div class="cadre zone-grille">
    {carte()}
    <div>
      <span class="surtitre">Où nous livrons</span>
      <h2 class="titre">Au cœur de la vallée de la Dordogne</h2>
      <p class="chapo">Nos tournées couvrent le Lot et au-delà, dont Figeac et Cahors, ainsi que Brive-la-Gaillarde et la Corrèze.</p>
      <ul class="zones-liste">
        <li><b>Plusieurs livraisons par semaine</b><span>Des tournées fixes ; les jours dépendent de votre secteur : nous consulter.</span></li>
        <li><b>Nos propres camions frigorifiques</b><span>Le frais et le surgelé restent au froid jusqu'à votre chambre froide.</span></li>
        <li><b>Un entrepôt à Rignac</b><span>{ADRESSE[0]}, {ADRESSE[1]} {ADRESSE[2]}, à quelques minutes de Gramat et de Rocamadour.</span></li>
      </ul>
    </div>
  </div>
</section>
<section class="section section-fonce">
  <div class="cadre">
    <span class="surtitre">Secteurs</span>
    <h2 class="titre">Principaux secteurs livrés</h2>
    <p class="chapo">Nous livrons ces secteurs et leurs alentours. Votre secteur n'apparaît pas ? Appelez-nous au <a href="tel:{TEL_INT}">{TEL}</a>.</p>
    <ul class="communes">{communes}</ul>
  </div>
</section>
<section class="section">
  <div class="cadre etroit">
    <span class="surtitre">Questions fréquentes</span>
    <h2 class="titre">La livraison en questions</h2>
    {faq_html(FAQ_LIVRAISON)}
  </div>
</section>
{appel(r, "Vérifions votre secteur", "Dites-nous où se trouve votre établissement : nous vous indiquons les jours de passage de la tournée.")}
"""
    service = {"@type": "Service", "name": "Livraison de produits alimentaires aux professionnels", "provider": {"@id": ORGA_ID}, "areaServed": ORGA["areaServed"], "serviceType": "Livraison en camion frigorifique"}
    return page("livraison/index.html", "Livraison grossiste alimentaire Lot, Brive et Corrèze · LVA Distribution",
                "LVA Distribution livre les professionnels de la restauration dans le Lot (Rocamadour, Gramat, Saint-Céré, Figeac, Cahors…) et en Corrèze (Brive) avec ses camions frigorifiques, plusieurs fois par semaine.",
                corps, r, actif="livraison/", schemas=[ariane_ld(chemin), faq_ld(FAQ_LIVRAISON), service])


def commander():
    r = "../"
    chemin = [("", "Accueil"), ("commander/", "Commander")]
    corps = f"""
{tete_page(r, chemin, "Commander", "Commander par téléphone, en ligne ou sur l'application", "Chez LVA Distribution, vous choisissez votre façon de commander : avec notre équipe de télévente, sur la boutique en ligne 24h/24 ou sur l'application mobile. Vos tarifs personnalisés s'appliquent partout.", "boulangerie.webp")}
<section class="section">
  <div class="cadre">
    <span class="surtitre">Trois façons de commander</span>
    <h2 class="titre">Comme vous préférez</h2>
    {canaux()}
  </div>
</section>
<section class="section section-fonce">
  <div class="cadre">
    <span class="surtitre">Ouvrir un compte</span>
    <h2 class="titre">Devenir client en quatre étapes</h2>
    <ol class="etapes">
      <li><b>Vous nous contactez</b><span>Par le formulaire ou au {TEL}.</span></li>
      <li><b>Un commercial vous rappelle</b><span>Il fait le point sur vos besoins et vous présente nos tarifs.</span></li>
      <li><b>Votre compte est ouvert</b><span>Vous recevez vos accès à la boutique en ligne et à l'application.</span></li>
      <li><b>Première livraison</b><span>Avec la tournée de votre secteur, en camion frigorifique.</span></li>
    </ol>
  </div>
</section>
<section class="section">
  <div class="cadre etroit">
    <span class="surtitre">Questions fréquentes</span>
    <h2 class="titre">Commander en questions</h2>
    {faq_html(FAQ_COMMANDE)}
  </div>
</section>
{appel(r)}
"""
    return page("commander/index.html", "Commander chez votre grossiste : télévente, boutique en ligne, application · LVA Distribution",
                "Commandez vos produits professionnels par téléphone, sur la boutique en ligne LVA Distribution 24h/24 ou sur l'application iPhone et Android. Ouverture de compte sur simple demande.",
                corps, r, actif="commander/", schemas=[ariane_ld(chemin), faq_ld(FAQ_COMMANDE)])


def qui():
    r = "../"
    chemin = [("", "Accueil"), ("qui-sommes-nous/", "Qui sommes-nous")]
    ligne_mail = f"<dt>Courriel</dt><dd>{a_mail()}</dd>" if MAIL else ""
    corps = f"""
{tete_page(r, chemin, "Qui sommes-nous", "Un grossiste alimentaire du Lot, au service des professionnels", "LVA Distribution est un grossiste alimentaire installé à Rignac, à côté de Gramat, dans le Lot. Nous fournissons les professionnels de la restauration et des métiers de bouche du Lot et de la Corrèze.", "viandes.webp")}
<section class="section">
  <div class="cadre deux-col">
    <div class="prose">
      <h2 class="titre">Notre métier</h2>
      <p>LVA Distribution achète, stocke et livre plus de 4&nbsp;000 références alimentaires et non alimentaires pour les restaurants, boulangeries, hôtels, campings, cafés, collectivités, traiteurs et commerces de bouche.</p>
      <p>Le frais est notre cœur de métier : viandes et volailles, canard, crèmerie, fromages et charcuterie représentent près de 70 % de nos ventes. Nous complétons avec les surgelés, l'épicerie, les boissons et les emballages pour que nos clients puissent tout commander au même endroit.</p>
      <h2 class="titre">Notre façon de travailler</h2>
      <p>Une équipe de télévente qui connaît chaque client, des commerciaux sur le terrain, un entrepôt à Rignac et nos propres camions frigorifiques. Nos clients commandent aussi en ligne, 24h/24, sur la boutique et l'application.</p>
      <p>Notre activité suit le rythme du territoire : Rocamadour, Padirac et la vallée de la Dordogne accueillent de nombreux visiteurs l'été, et nos tournées s'adaptent à la saison.</p>
    </div>
    <div>
      <div class="fiche">
        <dl>
          <dt>Entreprise</dt><dd>LVA Distribution</dd>
          <dt>Activité</dt><dd>Grossiste alimentaire pour professionnels</dd>
          <dt>Entrepôt</dt><dd>{ADRESSE[0]}, {ADRESSE[1]} {ADRESSE[2]}</dd>
          <dt>Zone</dt><dd>Lot, Brive et Corrèze</dd>
          <dt>Références</dt><dd>Plus de 4 000</dd>
          <dt>Clients</dt><dd>Plus de 700 professionnels livrés</dd>
          <dt>Commande</dt><dd>Télévente, boutique en ligne, application</dd>
          <dt>Téléphone</dt><dd><a href="tel:{TEL_INT}">{TEL}</a></dd>
          {ligne_mail}
        </dl>
      </div>
    </div>
  </div>
</section>
{bande_marques(r)}
{appel(r, "Travaillons ensemble", "Restaurant, boulangerie, hôtel ou collectivité : parlons de vos besoins.")}
"""
    about = {"@type": "AboutPage", "@id": DOMAINE + "/qui-sommes-nous/#a-propos", "url": DOMAINE + "/qui-sommes-nous/", "mainEntity": {"@id": ORGA_ID}}
    return page("qui-sommes-nous/index.html", "Qui sommes-nous · LVA Distribution, grossiste alimentaire à Rignac (Lot)",
                "LVA Distribution, grossiste alimentaire installé à Rignac près de Gramat (Lot) : plus de 4 000 références et plus de 700 professionnels livrés dans le Lot et en Corrèze.",
                corps, r, actif="qui-sommes-nous/", schemas=[ariane_ld(chemin), about])


def contact():
    r = "../"
    chemin = [("", "Accueil"), ("contact/", "Contact")]
    ligne_mail = f'<li><svg class="ic"><use href="#i-mail"/></svg><div><small>Courriel</small>{a_mail()}</div></li>' if MAIL else ""
    corps = f"""
{tete_page(r, chemin, "Contact", "Contacter LVA Distribution", "Vous ouvrez, vous reprenez une affaire ou vous cherchez un nouveau fournisseur ? Appelez-nous ou laissez vos coordonnées : un commercial vous rappelle pour ouvrir votre compte.")}
<section class="section">
  <div class="cadre contact-grille">
    <div>
      <span class="surtitre">Nous joindre</span>
      <h2 class="titre">Parlons de<br>votre cuisine</h2>
      <ul class="coord">
        <li><svg class="ic"><use href="#i-tel"/></svg><div><small>Téléphone</small><a href="tel:{TEL_INT}">{TEL}</a></div></li>
        {ligne_mail}
        <li><svg class="ic"><use href="#i-lieu"/></svg><div><small>Entrepôt</small><address><a href="https://www.google.com/maps/search/?api=1&amp;query=LVA+Distribution+Rignac+46500" rel="noopener">{ADRESSE[0]}<br>{ADRESSE[1]} {ADRESSE[2]}</a></address></div></li>
        <li><svg class="ic"><use href="#i-panier"/></svg><div><small>Déjà client</small><a href="{BOUTIQUE}" rel="noopener">Boutique en ligne</a></div></li>
      </ul>
    </div>
    {formulaire()}
  </div>
</section>
"""
    cp = {"@type": "ContactPage", "@id": DOMAINE + "/contact/#contact", "url": DOMAINE + "/contact/", "mainEntity": {"@id": ORGA_ID}}
    return page("contact/index.html", "Contact et ouverture de compte · LVA Distribution, Rignac (Lot)",
                "Contactez LVA Distribution au 05 65 10 00 20 pour ouvrir un compte professionnel. Entrepôt : Z.A. Les Vieilles Vignes, 46500 Rignac (Lot).",
                corps, r, actif="contact/", schemas=[ariane_ld(chemin), cp])


def mentions():
    r = "../"
    chemin = [("", "Accueil"), ("mentions-legales/", "Mentions légales")]
    m = MENTIONS

    def v(cle):
        return e(m[cle]) if m.get(cle) else '<span style="background:#4a3c10;color:#ffe08a;padding:0 4px;border-radius:3px">à compléter</span>'
    joindre = f"Téléphone : {TEL}" + (f" · Courriel : {a_mail()}" if MAIL else "")
    corps = f"""
{tete_page(r, chemin, "Informations légales", "Mentions légales", "Informations sur l'éditeur et l'hébergeur du site lva-distribution.fr.")}
<section class="section"><div class="cadre etroit prose">
<h2 class="titre">Éditeur</h2>
<p>LVA Distribution, {v("forme")}.<br>Siège social : {ADRESSE[0]}, {ADRESSE[1]} {ADRESSE[2]}, France.<br>Immatriculation : {v("rcs")} · SIRET {v("siret")} · TVA intracommunautaire {v("tva")}.<br>{joindre}</p>
<h2 class="titre">Directeur de la publication</h2>
<p>{v("directeur")}</p>
<h2 class="titre">Hébergement</h2>
<p>GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis.</p>
<h2 class="titre">Données personnelles et cookies</h2>
<p>Ce site ne dépose aucun cookie et ne mesure pas l'audience. Le formulaire « Devenir client » n'enregistre rien : il prépare un courriel dans votre propre messagerie. Les informations que vous nous envoyez servent uniquement à vous recontacter et à ouvrir votre compte client. Vous pouvez demander leur consultation, leur rectification ou leur suppression en nous écrivant.</p>
<h2 class="titre">Marques et photographies</h2>
<p>Les marques et logos cités appartiennent à leurs propriétaires respectifs et sont présentés pour indiquer les produits que nous distribuons. Photographies : catalogue LVA Distribution 2026. Vidéo d'accueil : extraits de la banque Mixkit, sous licence gratuite « Stock Video Free License ».</p>
</div></section>
"""
    return page("mentions-legales/index.html", "Mentions légales · LVA Distribution", "Mentions légales du site de LVA Distribution, grossiste alimentaire à Rignac (Lot).", corps, r, schemas=[ariane_ld(chemin)])


def page_404():
    corps = f"""<section class="tete-page"><div class="cadre"><span class="surtitre">Erreur 404</span><h1 class="titre">Cette page n'existe pas</h1><p class="chapo">Elle a peut-être été déplacée. Revenez à l'accueil ou appelez-nous au {TEL}.</p><div class="actions" style="margin-top:28px"><a class="btn btn-rouge" href="/">Retour à l'accueil</a><a class="btn btn-ligne" href="/produits/">Nos produits</a></div></div></section>"""
    page("404.html", "Page introuvable · LVA Distribution", "Cette page n'existe pas.", corps, "/", indexer=False)


# ---------------------------------------------------------------- fichiers annexes
def annexes(urls):
    robots = ["# Moteurs de recherche et assistants IA : tous bienvenus.", "User-agent: *", "Allow: /", ""]
    for bot in ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot"):
        robots += [f"User-agent: {bot}", "Allow: /", ""]
    robots.append(f"Sitemap: {DOMAINE}/sitemap.xml")
    with open(os.path.join(SORTIE, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(robots) + "\n")
    with open(os.path.join(SORTIE, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            prio = "1.0" if u == DOMAINE + "/" else "0.8"
            f.write(f"  <url><loc>{u}</loc><lastmod>{AUJ}</lastmod><priority>{prio}</priority></url>\n")
        f.write("</urlset>\n")
    faq = "\n".join(f"- **{q}** {rep}" for q, rep in FAQ_ACCUEIL + FAQ_LIVRAISON + FAQ_COMMANDE)
    gammes = "\n".join(f"- **{t}** : {tx}" for t, _, tx, _ in GAMMES)
    communes = ", ".join(c for c, _ in COMMUNES)
    ligne_mail = f"\n- Courriel : {MAIL}" if MAIL else ""
    with open(os.path.join(SORTIE, "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"""# LVA Distribution

> LVA Distribution est un grossiste alimentaire installé à Rignac, à côté de Gramat, dans le Lot (46500, Occitanie). Il fournit plus de 700 professionnels de la restauration et des métiers de bouche du Lot et de la Corrèze : restaurants, boulangeries-pâtisseries, hôtels et campings, cafés, collectivités, traiteurs, boucheries et épiceries. Plus de 4 000 références en frais, surgelé, épicerie, boissons et emballages, livrées en camions frigorifiques plusieurs fois par semaine.

## Coordonnées
- Adresse : {ADRESSE[0]}, {ADRESSE[1]} {ADRESSE[2]}, France
- Téléphone : {TEL}{ligne_mail}
- Boutique en ligne (clients) : {BOUTIQUE}
- Application mobile : {APPLI}
- Catalogue 2026 : {CATALOGUE}

## Zone de livraison
{communes} ; le Lot et au-delà, Brive et la Corrèze. Jours de passage selon le secteur : nous consulter.

## Gammes
{gammes}

## Marques distribuées
{", ".join(mq[0] for mq in MARQUES)}, ainsi que des produits régionaux comme le Rocamadour AOP.

## Commander
Par téléphone (télévente), sur la boutique en ligne 24h/24, ou sur l'application iPhone et Android. Tarifs personnalisés, visibles après ouverture du compte. Ouverture de compte : {DOMAINE}/contact/

## Questions fréquentes
{faq}

## Pages
- [Accueil]({DOMAINE}/)
- [Nos produits]({DOMAINE}/produits/)
- [Livraison]({DOMAINE}/livraison/)
- [Commander]({DOMAINE}/commander/)
- [Qui sommes-nous]({DOMAINE}/qui-sommes-nous/)
- [Contact]({DOMAINE}/contact/)
""")
    open(os.path.join(SORTIE, ".nojekyll"), "w").close()


def ressources():
    a = os.path.join(SORTIE, "assets")
    for sous in ("img/marques", "img/univers", "fonts"):
        os.makedirs(os.path.join(a, sous), exist_ok=True)
    shutil.copy(os.path.join(ICI, "src", "site.css"), os.path.join(a, "site.css"))
    shutil.copy(os.path.join(ICI, "src", "site.js"), os.path.join(a, "site.js"))
    for f in os.listdir(os.path.join(ICI, "fonts")):
        shutil.copy(os.path.join(ICI, "fonts", f), os.path.join(a, "fonts", f))
    for f in ("logo-lva.png", "hero-farine.webp", "viandes.webp", "fromages.webp", "charcuteries.webp", "boulangerie.webp", "bandeau-droite.webp", "partage.jpg", "favicon-32.png", "apple-touch-icon.png"):
        shutil.copy(os.path.join(ICI, "img", f), os.path.join(a, "img", f))
    os.makedirs(os.path.join(a, "video"), exist_ok=True)
    for f in os.listdir(os.path.join(ICI, "video")):
        shutil.copy(os.path.join(ICI, "video", f), os.path.join(a, "video", f))
    for d in ("marques", "univers"):
        for f in os.listdir(os.path.join(ICI, "img", d)):
            shutil.copy(os.path.join(ICI, "img", d, f), os.path.join(a, "img", d, f))


if __name__ == "__main__":
    if os.path.isdir(SORTIE):
        for nom in os.listdir(SORTIE):
            if nom == "CNAME":
                continue
            p = os.path.join(SORTIE, nom)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(SORTIE, exist_ok=True)
    ressources()
    urls = [accueil(), produits(), livraison(), commander(), qui(), contact(), mentions()]
    accueil("video")  # variante à comparer, non indexée
    page_404()
    annexes(urls)
    print("Site construit :", len(urls), "pages dans", SORTIE, "| courriel :", "oui" if MAIL else "NON (variable LVA_EMAIL absente)")
