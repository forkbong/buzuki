'use strict';

$(() => {
  let json = {};
  $('#search-input').autocomplete({
    source: (request, response) => {
      $.ajax({
        url: `/api/search/${$('#search-input').val()}/`,
        success: (data) => {
          json = data;
          response(data.map((item) => item.name));
        },
      });
    },
    select: (ev, ui) => {
      const url = json.filter((item) => item.name === ui.item.value)[0].url;
      $('#search-input').val(ui.item.value);
      window.location.pathname = url;
    },
    delay: 150,
  });
});
