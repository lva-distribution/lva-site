(function () {
  var doc = document.documentElement;
  var calme = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Menu
  var entete = document.getElementById('entete');
  var burger = entete.querySelector('.burger');
  function surScroll() { entete.classList.toggle('plein', window.scrollY > 40); }
  burger.addEventListener('click', function () {
    var ouvert = entete.classList.toggle('ouvert');
    burger.setAttribute('aria-expanded', ouvert);
    burger.setAttribute('aria-label', ouvert ? 'Fermer le menu' : 'Ouvrir le menu');
    burger.querySelector('use').setAttribute('href', ouvert ? '#i-croix' : '#i-menu');
  });
  entete.querySelectorAll('.nav a').forEach(function (a) {
    a.addEventListener('click', function () { if (entete.classList.contains('ouvert')) burger.click(); });
  });

  // Vidéo d'accueil : arrêtée si l'utilisateur préfère moins d'animations ; relancée si le navigateur l'a bloquée
  var film = document.querySelector('.une-film video');
  if (film) {
    if (calme) { film.removeAttribute('autoplay'); film.pause(); }
    else { var essai = film.play(); if (essai && essai.catch) essai.catch(function () {}); }
  }

  // Barre de lecture et parallaxe
  var barre = document.createElement('div'); barre.className = 'progression'; document.body.appendChild(barre);
  var photo = document.querySelector('[data-parallaxe]');
  var filmBloc = document.querySelector('.une-film');
  function auDefilement() {
    var y = window.scrollY, h = doc.scrollHeight - window.innerHeight;
    surScroll();
    barre.style.transform = 'scaleX(' + (h > 0 ? y / h : 0) + ')';
    // la vidéo s'assombrit puis s'efface pendant que le texte passe devant
    if (filmBloc) {
      var course = window.innerWidth > 760 ? filmBloc.offsetHeight * 0.9 : filmBloc.offsetHeight * 2.4;
      var p = Math.min(1, Math.max(0, y / course));
      filmBloc.style.setProperty('--p', p.toFixed(3));
      filmBloc.style.visibility = p >= 1 ? 'hidden' : 'visible';
    }
    if (!calme && photo && window.innerWidth > 760 && y < window.innerHeight * 1.2) photo.style.transform = 'translate3d(0,' + (y * 0.35) + 'px,0)';
  }
  var attente = false;
  window.addEventListener('scroll', function () {
    if (!attente) { attente = true; requestAnimationFrame(function () { auDefilement(); attente = false; }); }
  }, { passive: true });
  auDefilement();

  // Apparition des blocs en cascade
  var cibles = document.querySelectorAll('main .section .surtitre, main .section h2, main .section .chapo, .public, .canal, .tuile, .univers-liste li, .carte, .zones-liste li, .coord li, .formulaire, .livraison, .pied-section, .atouts li, .gamme, .etapes li, .faq, .fiche, .communes, .prose > *');
  if ('IntersectionObserver' in window && !calme) {
    var hauteur = window.innerHeight;
    cibles = Array.prototype.filter.call(cibles, function (el) {
      // ce qui est déjà à l'écran au chargement reste visible tout de suite
      return el.getBoundingClientRect().top > hauteur * 0.9;
    });
    cibles.forEach(function (el) {
      var i = Array.prototype.indexOf.call(el.parentNode.children, el);
      el.style.setProperty('--d', (Math.min(i, 8) * 0.08) + 's');
      el.classList.add('reveal');
    });
    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vu'); obs.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.1 });
    cibles.forEach(function (el) { obs.observe(el); });
  }

  // Chiffres qui défilent
  var fmt = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };
  if ('IntersectionObserver' in window && !calme) {
    var obsC = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) {
        if (!e.isIntersecting) return;
        obsC.unobserve(e.target);
        var el = e.target, fin = +el.dataset.compte, suff = el.dataset.suffixe || '', t0 = null;
        (function pas(t) {
          if (!t0) t0 = t;
          var p = Math.min((t - t0) / 1600, 1);
          el.textContent = fmt(Math.round(fin * (1 - Math.pow(1 - p, 3)))) + suff;
          if (p < 1) requestAnimationFrame(pas);
        })(performance.now());
      });
    }, { threshold: 0.6 });
    document.querySelectorAll('[data-compte]').forEach(function (el) { obsC.observe(el); });
  }

  // Halo qui suit la souris
  document.querySelectorAll('.public, .canal').forEach(function (c) {
    c.addEventListener('pointermove', function (e) {
      var r = c.getBoundingClientRect();
      c.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      c.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  // Bandes qui défilent : avance toute seule, se met en pause au survol ou quand on la touche,
  // se fait glisser au doigt (défilement natif) ou à la souris, et repart 3 s après
  function bandeDefilante(fenetre, vitesse) {
    var piste = fenetre.firstElementChild;
    if (!piste || piste.children.length < 2) return;
    var n = piste.children.length / 2, x = 0, avant = null, reprise = 0, survol = false, doigt = false;
    var glisse = null, ecrit = 0;   // ecrit = dernière position posée par le script
    function moitie() { return piste.children[n].offsetLeft - piste.children[0].offsetLeft; }
    function boucler() { var m = moitie(); if (m > 0) { while (x >= m) x -= m; while (x < 0) x += m; } }
    function poser() { fenetre.scrollLeft = x; ecrit = fenetre.scrollLeft; }
    function main() {   // la personne a fait glisser la bande : on reprend sa position
      if (Math.abs(fenetre.scrollLeft - ecrit) > 2) { x = fenetre.scrollLeft; ecrit = x; reprise = Date.now() + 3000; return true; }
      return false;
    }
    function tic(t) {
      var dt = avant ? Math.min(t - avant, 100) / 1000 : 0; avant = t;
      if (!glisse) main();
      var arretee = doc.classList.contains('anim-arretees') || calme;
      if (!arretee && !survol && !doigt && !glisse && Date.now() > reprise) {
        x += vitesse * dt; boucler(); poser();
      }
      requestAnimationFrame(tic);
    }
    fenetre.addEventListener('scroll', function () {
      if (!glisse && main()) {
        var m = moitie(); if (m > 0 && (x >= m || x <= 0)) { boucler(); poser(); }
      }
    }, { passive: true });
    fenetre.addEventListener('mouseenter', function () { survol = true; });
    fenetre.addEventListener('mouseleave', function () { survol = false; });
    fenetre.addEventListener('touchstart', function () { doigt = true; }, { passive: true });
    fenetre.addEventListener('touchend', function () { doigt = false; reprise = Date.now() + 3000; }, { passive: true });
    fenetre.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse') return;
      glisse = { depart: e.clientX, x: x }; fenetre.classList.add('saisi');
      fenetre.setPointerCapture(e.pointerId);
    });
    fenetre.addEventListener('pointermove', function (e) {
      if (!glisse) return;
      x = glisse.x - (e.clientX - glisse.depart); boucler(); poser();
    });
    function lacher() { if (glisse) { glisse = null; fenetre.classList.remove('saisi'); reprise = Date.now() + 3000; } }
    fenetre.addEventListener('pointerup', lacher);
    fenetre.addEventListener('pointercancel', lacher);
    requestAnimationFrame(tic);
  }
  document.querySelectorAll('.marques-fenetre').forEach(function (f) { bandeDefilante(f, 45); });
  document.querySelectorAll('.defile').forEach(function (f) { bandeDefilante(f, 60); });

  // Bouton pause : arrête la vidéo et les bandes qui défilent
  var pause = document.querySelector('.pause-anim');
  if (pause) {
    var poser = function (arret) {
      doc.classList.toggle('anim-arretees', arret);
      pause.setAttribute('aria-pressed', arret);
      pause.setAttribute('aria-label', arret ? 'Relancer la vidéo et les animations' : 'Mettre en pause la vidéo et les animations');
      pause.querySelector('svg').innerHTML = arret ? '<path d="M7 4l13 8-13 8z"/>' : '<path d="M9 5v14M15 5v14"/>';
      if (film) { if (arret) film.pause(); else { var j = film.play(); if (j && j.catch) j.catch(function () {}); } }
    };
    if (calme) poser(true);
    pause.addEventListener('click', function () { poser(!doc.classList.contains('anim-arretees')); });
  }

  var an = document.getElementById('annee'); if (an) an.textContent = new Date().getFullYear();

  // Formulaire « Devenir client » : prépare un courriel, rien n'est stocké
  var form = document.getElementById('formulaire');
  if (form) {
    var note = document.getElementById('f-note');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var manquants = [];
      form.querySelectorAll('[required]').forEach(function (c) {
        var vide = !c.value.trim();
        c.setAttribute('aria-invalid', vide);
        c.style.borderColor = vide ? '#a32239' : '';
        if (vide) manquants.push(form.querySelector('label[for="' + c.id + '"]').textContent.toLowerCase());
      });
      if (manquants.length) {
        note.textContent = 'Il manque : ' + manquants.join(', ') + '.';
        form.querySelector('[aria-invalid="true"]').focus();
        return;
      }
      var v = function (n) { return form.elements[n].value.trim(); };
      var corps = ['Bonjour,', '', 'Je souhaite devenir client de LVA Distribution.', '',
        'Nom : ' + v('nom'), 'Établissement : ' + v('etablissement'), 'Activité : ' + v('activite'),
        'Ville : ' + (v('commune') || 'non précisée'), 'Téléphone : ' + v('telephone'), '', v('message'), '', 'Merci de me recontacter.'].join('\n');
      window.location.href = 'mailto:lva@lva-distribution.fr?subject=' + encodeURIComponent('Demande d\'ouverture de compte : ' + v('etablissement')) + '&body=' + encodeURIComponent(corps);
      note.textContent = 'Votre messagerie s\'ouvre avec la demande prête : il ne reste qu\'à l\'envoyer. Rien ne s\'ouvre ? Appelez le 05 65 10 00 20.';
    });
  }
})();
