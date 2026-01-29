/* =====================================================
   FLOWENGINE – UNIVERSAL MOBILE MENU SCRIPT
===================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', init);

  function init() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    createToggle();
    createOverlay();
    bindResize();
  }

  function createToggle() {
    if (document.querySelector('.mobile-menu-toggle')) return;

    const btn = document.createElement('button');
    btn.className = 'mobile-menu-toggle';
    btn.innerHTML = '<i class="fas fa-bars"></i>';
    btn.addEventListener('click', toggleMenu);

    document.body.appendChild(btn);
  }

  function createOverlay() {
    if (document.querySelector('.sidebar-overlay')) return;

    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.addEventListener('click', closeMenu);

    document.body.appendChild(overlay);
  }

  function toggleMenu() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const icon = document.querySelector('.mobile-menu-toggle i');

    const open = sidebar.classList.toggle('active');
    overlay.classList.toggle('active', open);

    icon.className = open ? 'fas fa-times' : 'fas fa-bars';
    document.body.style.overflow = open ? 'hidden' : '';
  }

  function closeMenu() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const icon = document.querySelector('.mobile-menu-toggle i');

    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    icon.className = 'fas fa-bars';
    document.body.style.overflow = '';
  }

  function bindResize() {
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        closeMenu();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMenu();
  });

})();
/* =====================================================
   MOBILE MODAL CUSTOM SELECT (NO HTML CHANGES)
===================================================== */

(function () {
  if (window.innerWidth > 768) return;

  document.addEventListener('click', closeAllCustomSelects);

  const observer = new MutationObserver(() => {
    initMobileModalSelects();
  });

  observer.observe(document.body, { childList: true, subtree: true });

  function initMobileModalSelects() {
    document.querySelectorAll('.modal-content select:not(.native-hidden)')
      .forEach(select => {
        if (select.dataset.customized) return;

        select.dataset.customized = 'true';
        select.classList.add('native-hidden');

        const wrapper = document.createElement('div');
        wrapper.className = 'mobile-custom-select';

        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = select.options[select.selectedIndex]?.text || 'Select';

        const options = document.createElement('div');
        options.className = 'mobile-custom-options';
        options.style.display = 'none';

        [...select.options].forEach(opt => {
          const div = document.createElement('div');
          div.textContent = opt.text;

          div.onclick = () => {
            select.value = opt.value;
            button.textContent = opt.text;
            options.style.display = 'none';
            select.dispatchEvent(new Event('change', { bubbles: true }));
          };

          options.appendChild(div);
        });

        button.onclick = (e) => {
          e.stopPropagation();
          closeAllCustomSelects();
          options.style.display = 'block';
        };

        wrapper.appendChild(button);
        wrapper.appendChild(options);
        select.parentNode.insertBefore(wrapper, select.nextSibling);
      });
  }

  function closeAllCustomSelects() {
    document.querySelectorAll('.mobile-custom-options')
      .forEach(o => o.style.display = 'none');
  }
})();
