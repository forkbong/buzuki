'use strict';

/* global addEventListeners */

const transposeInit = (apiUrl, slug, contentDivId) => {
  const setHtml = (elementId, html) => {
    const element = document.getElementById(elementId);
    element.innerHTML = html;
  };

  const setLogoutNext = (url) => {
    const logout = document.getElementById('logout');
    if (logout) {
      const parts = logout.getAttribute('href').split('=');
      parts[1] = url;
      logout.setAttribute('href', parts.join('='));
    }
  };

  addEventListeners('.transpose-dropdown-item', 'click', (event) => {
    const element = event.target;
    const root = element.getAttribute('data-root');
    fetch(`${apiUrl}/${root}`)
      .then((resp) => resp.json())
      .then((data) => {
        setHtml(contentDivId, data.info);
        if (data.title) {
          setHtml('header-title', data.title);
        }
        let parts = window.location.pathname.split('/');
        parts = ['', parts[1], parts[2], root];
        const url = parts.join('/');
        window.history.pushState(null, '', url);
        setLogoutNext(url);
      });
    if (slug) {
      const saveBtn = document.getElementById('save-button');
      const printBtn = document.getElementById('print-button');
      saveBtn.removeAttribute('hidden');
      saveBtn.setAttribute('href', `/admin/save/${slug}/${root}`);
      printBtn.setAttribute('href', `/songs/${slug}/${root}/print`);
    }
  });

  window.onpopstate = (event) => {
    const url = window.location.pathname;
    setLogoutNext(url);
    const parts = url.split('/');
    const root = parts[3];
    fetch(`${apiUrl}/${root}`)
      .then((resp) => resp.json())
      .then((data) => {
        setHtml(contentDivId, data.info);
        if (data.title) {
          setHtml('header-title', data.title);
        }
      });
    event.preventDefault();
    if (slug) {
      const saveBtn = document.getElementById('save-button');
      const printBtn = document.getElementById('print-button');
      if (root) {
        saveBtn.removeAttribute('hidden');
        saveBtn.setAttribute('href', `/admin/save/${slug}/${root}`);
        printBtn.setAttribute('href', `/songs/${slug}/${root}/print`);
      } else {
        saveBtn.setAttribute('hidden', true);
      }
    }
  };
};
