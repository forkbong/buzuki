'use strict';

$(() => {
  $('#search-input').autocomplete({
    source: (request, response) => {
      $.ajax({
        url: `/api/search/${$('#search-input').val()}/`,
        success: (data) => {
          response(data.slice(0, 15));
        },
      });
    },
    select: (ev, ui) => {
      $('#search-input').val(ui.item.value);
      $('#search-form').submit();
    },
    delay: 150,
  });
});
