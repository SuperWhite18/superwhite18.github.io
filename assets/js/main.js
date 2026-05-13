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

  // ── Table of Contents ──
  var postContent = document.getElementById('postContent');
  var tocList = document.getElementById('tocList');
  var tocSidebar = document.getElementById('tocSidebar');

  if (postContent && tocList && tocSidebar) {
    var headings = postContent.querySelectorAll('h2, h3');
    var tocItems = [];

    headings.forEach(function(h, i) {
      // Add id if missing
      if (!h.id) {
        h.id = 'section-' + (i + 1);
      }
      var level = h.tagName.toLowerCase();
      var item = {
        id: h.id,
        text: h.textContent,
        level: level
      };
      tocItems.push(item);

      // Build TOC link
      var li = document.createElement('li');
      li.className = 'toc-item' + (level === 'h3' ? ' toc-h3' : '');
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.setAttribute('data-target', h.id);
      a.addEventListener('click', function(e) {
        e.preventDefault();
        var target = document.getElementById(this.getAttribute('data-target'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
      li.appendChild(a);
      tocList.appendChild(li);
    });

    // Scroll spy with IntersectionObserver
    var tocLinks = tocList.querySelectorAll('a');
    var scrollObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var id = entry.target.id;
          tocLinks.forEach(function(link) {
            link.classList.toggle('active', link.getAttribute('data-target') === id);
          });
        }
      });
    }, {
      rootMargin: '-80px 0px -70% 0px',
      threshold: 0
    });

    headings.forEach(function(h) {
      scrollObserver.observe(h);
    });
  }
})();
