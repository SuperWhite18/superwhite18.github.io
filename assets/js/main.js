// Theme toggle
(function() {
  var themeToggle = document.getElementById('themeToggle');
  var html = document.documentElement;

  var savedTheme = localStorage.getItem('theme') || 'light';
  html.setAttribute('data-theme', savedTheme);

  themeToggle.addEventListener('click', function() {
    var current = html.getAttribute('data-theme');
    var next = current === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });

  // Nav scroll effect
  var navbar = document.getElementById('navbar');
  window.addEventListener('scroll', function() {
    if (navbar) {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    }
  });

  // Mobile menu
  var menuToggle = document.getElementById('menuToggle');
  var navLinks = document.getElementById('navLinks');
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', function() {
      navLinks.classList.toggle('open');
    });
  }

  // Search overlay
  var searchBtn = document.getElementById('searchBtn');
  var searchOverlay = document.getElementById('searchOverlay');
  var searchInput = document.getElementById('searchInput');

  if (searchBtn && searchOverlay && searchInput) {
    searchBtn.addEventListener('click', function() {
      searchOverlay.classList.add('active');
      setTimeout(function() { searchInput.focus(); }, 100);
    });

    searchOverlay.addEventListener('click', function(e) {
      if (e.target === searchOverlay) searchOverlay.classList.remove('active');
    });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') searchOverlay.classList.remove('active');
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchOverlay.classList.toggle('active');
        if (searchOverlay.classList.contains('active')) searchInput.focus();
      }
    });
  }

  // Intersection Observer - animate elements as they scroll into view
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.05 });

  document.querySelectorAll('.article-card, .sidebar-card').forEach(function(el) {
    observer.observe(el);
  });
})();
