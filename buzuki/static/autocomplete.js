'use strict';

$(() => {
  let json = {};

  const $autocompleteWidget = $('ul#autocomplete');
  const $searchInput = $('#search-input');

  const move = function () {
    const element = document.getElementById('search-input');
    $autocompleteWidget.css({
      'left': element.offsetLeft,
      'top': element.offsetTop + element.offsetHeight - 2,
      'min-width': element.offsetWidth,
    });
  };

  const select = function (li, updateVal) {
    $('li.selected').removeClass('selected');
    li.addClass('selected');
    if (updateVal) {
      $searchInput.val(li.text());
    }
  };

  const search = function () {
    const query = $searchInput.val();
    if (!query.length) {
      $autocompleteWidget.hide();
      return;
    }
    fetch(`/api/search/${query}/`)
      .then((resp) => resp.json())
      .then((data) => {
        json = data;
        const items = data.map((item) => item.name);
        if (!items.length) {
          $autocompleteWidget.hide();
          return;
        }
        const newList = [];
        $.each(items, (index, value) => {
          newList.push(`<li>${value}</li>`);
        });
        $autocompleteWidget.html(newList);
        $autocompleteWidget.show();
      });
  };

  const goto = function (value) {
    const url = json.filter((item) => item.name === value)[0].url;
    $('#search-input').val(value);
    window.location.href = url;
  };

  // On window resize, make sure that the widget is positioned correctly.
  $(window).on('resize', () => {
    move();
  });

  // Hide the autocomplete widget when clicking outside.
  $(document).on('click', (event) => {
    if (!$(event.target).closest('ul#autocomplete').length &&
        !$(event.target).closest('input#search-input').length) {
      $autocompleteWidget.hide();
    }
  });

  // We disable selection on mouseenter before doing things that
  // might change the size of the autocomplete widget, because we
  // don't want to select an item without actually moving the mouse.
  let selectOnMouseEnter = true;

  // On input call the search API and update the widget.
  $searchInput.on('input', () => {
    search();
    selectOnMouseEnter = false;
  });

  // Show the autocomplete widget when focusing the search input.
  $searchInput.on('focus', () => {
    // If it's already visible we don't need to do anything.
    if ($autocompleteWidget.css('display') === 'block') {
      return;
    }
    move();
    search();
    selectOnMouseEnter = false;
  });

  // Go to clicked item.
  $autocompleteWidget.on('click', 'li', function () {
    select($(this), true);
    goto($(this).text());
  });

  // Select the hovered item.
  $('#autocomplete').on('mouseenter', 'li', function () {
    if (selectOnMouseEnter) {
      select($(this), false);
    } else {
      selectOnMouseEnter = true;
    }
  });

  // With up/down arrows, select the respective item.
  // With return, go to the selected item if
  // there is one, otherwise go to search page.
  $searchInput.on('keyup', (event) => {
    let li = $('li.selected');
    switch (event.which) {
    case 38: // Up
      li = li.prev().length ? li.prev() : $('ul#autocomplete>li').last();
      select(li, true);
      break;
    case 40: // Down
      li = li.next().length ? li.next() : $('ul#autocomplete>li').first();
      select(li, true);
      break;
    case 13: // Enter
      if (li.length) {
        goto(li.text());
      } else {
        const query = $searchInput.val();
        if (query.length) {
          const url = `/search/?q=${query}`;
          window.location.href = url;
        }
      }
    }
  });
});
