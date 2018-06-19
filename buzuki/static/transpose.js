'use strict';

const transposeInit = function transposeInit(apiUrl, contentDivId) {
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
  };
};
