// Tableau de bord de fréquentation (page /stats/, réservée à LVA, protégée par un code)
(function () {
  var API = 'https://axnysfiklmtfpterawgm.supabase.co/rest/v1/rpc/site_stats';
  var CLE = 'sb_publishable_xhAnr45DL5VdMaDotuelcQ_WM6-QxMC';
  var form = document.getElementById('stats-acces');
  var zone = document.getElementById('stats-resultats');
  var etat = document.getElementById('stats-etat');
  var champCode = document.getElementById('stats-code');
  var choixJours = document.getElementById('stats-jours');
  var compter = document.getElementById('stats-compter');

  function lire(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function ecrire(k, v) { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} }

  // Ne pas compter les visites de ce navigateur (postes LVA)
  compter.checked = lire('lva-stats-off') === '1';
  compter.addEventListener('change', function () { ecrire('lva-stats-off', compter.checked ? '1' : null); });

  var NOMS_EVT = { tel: 'Clics sur le téléphone', mail: 'Clics sur le mail', boutique: 'Clics vers la boutique', appli: 'Clics vers l\'application', catalogue: 'Ouvertures du catalogue', formulaire: 'Demandes « Devenir client »' };
  var NOMS_PAGES = { '/': 'Accueil', '/produits/': 'Nos produits', '/livraison/': 'Livraison', '/commander/': 'Commander', '/qui-sommes-nous/': 'Qui sommes-nous', '/contact/': 'Contact', '/mentions-legales/': 'Mentions légales' };
  var fmt = function (n) { return Number(n).toLocaleString('fr-FR'); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  function tableau(titre, lignes, colNom, colVal) {
    if (!lignes.length) return '<div class="stats-bloc"><h2>' + titre + '</h2><p class="stats-vide">Rien pour l\'instant.</p></div>';
    var max = Math.max.apply(null, lignes.map(function (l) { return l.v; }));
    return '<div class="stats-bloc"><h2>' + titre + '</h2><table class="stats-table"><thead><tr><th>' + colNom + '</th><th>' + colVal + '</th></tr></thead><tbody>' +
      lignes.map(function (l) {
        return '<tr><td><span class="stats-jauge" style="--l:' + Math.max(2, Math.round(l.v / max * 100)) + '%"></span>' + esc(l.n) + '</td><td>' + fmt(l.v) + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  function afficher(d, jours) {
    var evt = {}; (d.evenements || []).forEach(function (e) { evt[e.evenement] = e.nombre; });
    var tuiles = [
      ['Visiteurs', d.visiteurs, 'un même visiteur compte une fois par jour'],
      ['Pages vues', d.vues, ''],
      ['Clics téléphone', evt.tel || 0, ''],
      ['Clics boutique', evt.boutique || 0, ''],
      ['Demandes « Devenir client »', evt.formulaire || 0, '']
    ];
    // jours sans visite remis à zéro pour un axe continu
    var parJour = {}; (d.par_jour || []).forEach(function (p) { parJour[p.jour] = p; });
    var serie = [], debut = new Date(d.debut + 'T12:00:00');
    for (var i = 0; i < jours; i++) {
      var dt = new Date(debut.getTime() + i * 86400000), k = dt.toISOString().slice(0, 10);
      serie.push({ jour: dt, visiteurs: parJour[k] ? parJour[k].visiteurs : 0, vues: parJour[k] ? parJour[k].vues : 0 });
    }
    var max = Math.max(1, Math.max.apply(null, serie.map(function (s) { return s.visiteurs; })));
    var etiquette = function (dt) { return dt.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }); };
    var barres = serie.map(function (s) {
      var h = Math.round(s.visiteurs / max * 100);
      return '<div class="stats-barre" tabindex="0" data-info="' + etiquette(s.jour) + ' : ' + fmt(s.visiteurs) + ' visiteur' + (s.visiteurs > 1 ? 's' : '') + ', ' + fmt(s.vues) + ' page' + (s.vues > 1 ? 's' : '') + ' vue' + (s.vues > 1 ? 's' : '') + '"><span style="height:' + h + '%"></span></div>';
    }).join('');
    var tableJours = '<details class="stats-details"><summary>Voir le détail jour par jour</summary><table class="stats-table"><thead><tr><th>Jour</th><th>Visiteurs</th><th>Pages vues</th></tr></thead><tbody>' +
      serie.slice().reverse().map(function (s) { return '<tr><td>' + s.jour.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' }) + '</td><td>' + fmt(s.visiteurs) + '</td><td>' + fmt(s.vues) + '</td></tr>'; }).join('') + '</tbody></table></details>';

    zone.innerHTML =
      '<div class="stats-tuiles">' + tuiles.map(function (t) { return '<div class="stats-tuile"><b>' + fmt(t[1]) + '</b><span>' + t[0] + '</span>' + (t[2] ? '<small>' + t[2] + '</small>' : '') + '</div>'; }).join('') + '</div>' +
      '<div class="stats-bloc"><h2>Visiteurs par jour</h2><div class="stats-graphe" role="img" aria-label="Visiteurs par jour sur ' + jours + ' jours ; détail dans le tableau ci-dessous">' + barres + '</div>' +
      '<div class="stats-axe"><span>' + etiquette(serie[0].jour) + '</span><span>' + etiquette(serie[serie.length - 1].jour) + '</span></div><div class="stats-bulle" hidden></div>' + tableJours + '</div>' +
      '<div class="stats-grille">' +
      tableau('Pages les plus vues', (d.pages || []).map(function (p) { return { n: NOMS_PAGES[p.page] || p.page, v: p.vues }; }), 'Page', 'Vues') +
      tableau('D\'où viennent les visiteurs', (d.sources || []).map(function (p) { return { n: p.source === 'direct' ? 'Accès direct (lien tapé, favori, QR…)' : p.source, v: p.visiteurs }; }), 'Provenance', 'Visiteurs') +
      tableau('Appareils', (d.appareils || []).map(function (p) { return { n: { mobile: 'Téléphone', tablette: 'Tablette', ordinateur: 'Ordinateur' }[p.appareil] || p.appareil, v: p.visiteurs }; }), 'Appareil', 'Visiteurs') +
      tableau('Actions des visiteurs', (d.evenements || []).map(function (p) { return { n: NOMS_EVT[p.evenement] || p.evenement, v: p.nombre }; }), 'Action', 'Nombre') +
      '</div>';

    var bulle = zone.querySelector('.stats-bulle'), graphe = zone.querySelector('.stats-graphe');
    function montrer(b) {
      bulle.textContent = b.getAttribute('data-info'); bulle.hidden = false;
      var r = b.getBoundingClientRect(), g = graphe.getBoundingClientRect();
      bulle.style.left = Math.min(Math.max(0, r.left - g.left + r.width / 2 - 110), g.width - 220) + 'px';
    }
    graphe.querySelectorAll('.stats-barre').forEach(function (b) {
      b.addEventListener('pointerenter', function () { montrer(b); });
      b.addEventListener('focus', function () { montrer(b); });
    });
    graphe.addEventListener('pointerleave', function () { bulle.hidden = true; });
  }

  function charger() {
    var code = champCode.value.trim(), jours = +choixJours.value;
    if (!code) { etat.textContent = 'Entrez le code.'; return; }
    etat.textContent = 'Chargement…';
    fetch(API, { method: 'POST', headers: { 'apikey': CLE, 'Content-Type': 'application/json' }, body: JSON.stringify({ p_code: code, p_jours: jours }) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) {
        if (!x.ok) { etat.textContent = /code/.test(x.j.message || '') ? 'Code incorrect.' : 'Erreur : ' + (x.j.message || 'inconnue'); zone.innerHTML = ''; return; }
        ecrire('lva-stats-code', code); etat.textContent = 'Depuis le ' + new Date(x.j.debut + 'T12:00:00').toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' }) + '.';
        afficher(x.j, jours);
      })
      .catch(function () { etat.textContent = 'Impossible de joindre le serveur.'; });
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); charger(); });
  choixJours.addEventListener('change', function () { if (champCode.value.trim()) charger(); });
  var memo = lire('lva-stats-code'); if (memo) { champCode.value = memo; charger(); }
})();
