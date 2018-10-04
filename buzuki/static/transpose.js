'use strict';

const transposeInit = function transposeInit(apiUrl, slug, contentDivId) {
  $('.transpose-dropdown-item').click(function () {
    const root = $(this).data('root');
    fetch(`${apiUrl}/${root}`)
      .then((resp) => resp.json())
      .then((data) => {
        $(contentDivId).html(data.info);
        let parts = window.location.pathname.split('/');
        parts = ['', parts[1], parts[2], root];
        window.history.pushState(null, '', parts.join('/'));
        if (data.title) {
          $('#header-title').html(data.title);
        }
      });
    if (slug) {
      const saveBtn = $('#save-button');
      const printBtn = $('#print-button');
      saveBtn.prop('hidden', false);
      saveBtn.attr('href', `/admin/save/${slug}/${root}`);
      printBtn.attr('href', `/songs/${slug}/${root}/print`);
    }
  });

  window.onpopstate = function (event) {
    const parts = window.location.pathname.split('/');
    const root = parts[3];
    fetch(`${apiUrl}/${root}`)
      .then((resp) => resp.json())
      .then((data) => {
        $(contentDivId).html(data.info);
        if (data.title) {
          $('#header-title').html(data.title);
        }
      });
    event.preventDefault();
    if (slug) {
      const saveBtn = $('#save-button');
      const printBtn = $('#print-button');
      if (root) {
        saveBtn.prop('hidden', false);
        saveBtn.attr('href', `/admin/save/${slug}/${root}`);
        printBtn.attr('href', `/songs/${slug}/${root}/print`);
      } else {
        saveBtn.prop('hidden', true);
      }
    }
  };
};
