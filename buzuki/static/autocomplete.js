'use strict';

(() => {
  const autocomplete = document.getElementById('autocomplete');
  const input = document.getElementById('search-input');

  const move = () => {
    autocomplete.style.left = `${input.offsetLeft}px`;
    autocomplete.style.top = `${input.offsetTop + input.offsetHeight - 2}px`;
    autocomplete.style.minWidth = `${input.offsetWidth}px`;
  };

  const select = (li, updateVal = true) => {
    if (!li) {
      return;
    }
    const element = document.querySelector('li.selected');
    if (element) {
      element.classList.remove('selected');
    }
    li.classList.add('selected');
    if (updateVal) {
      input.value = li.innerText;
    }
  };

  const search = () => {
    const query = input.value
      .replace(/[!@#$%^&*()\-_=+'"\s]+/gu, ' ')
      .trim();
    if (!query.length) {
      autocomplete.innerHTML = '';
      autocomplete.style.display = 'none';
      return;
    }
    fetch(`/api/autocomplete/?q=${query}`)
      .then((resp) => resp.json())
      .then((data) => {
        if (!data.length) {
          autocomplete.innerHTML = '';
          autocomplete.style.display = 'none';
          return;
        }
        const list = [];
        data.forEach((item) => {
          list.push(`<li data-url="${item.url}">${item.name}</li>`);
        });
        autocomplete.innerHTML = list.join('');
        autocomplete.style.display = 'block';
      });
  };

  // On window resize, make sure that the widget is positioned correctly.
  window.addEventListener('resize', () => {
    move();
  });

  // Hide the autocomplete widget when clicking anywhere but the search input.
  document.addEventListener('click', () => {
    autocomplete.style.display = 'none';
  });
  input.addEventListener('click', (event) => {
    event.stopPropagation();
  });

  // On input call the search API and update the widget.
  input.addEventListener('input', () => {
    search();
  });

  // Show the autocomplete widget when focusing the search input.
  input.addEventListener('focus', () => {
    // If it's already visible we don't need to do anything.
    if (autocomplete.style.display === 'block') {
      return;
    }
    move();
    search();
  });

  // Go to clicked item.
  autocomplete.addEventListener('click', (event) => {
    select(event.target);
    window.location.href = event.target.getAttribute('data-url');
  });

  // Select hovered item.
  autocomplete.addEventListener('mouseover', (event) => {
    select(event.target, false);
  });

  // With up/down arrows, select the respective item.
  // With return, go to the selected item if
  // there is one, otherwise go to search page.
  input.addEventListener('keyup', (event) => {
    let li = document.querySelector('li.selected');
    switch (event.which) {
    case 38: // Up
      li = li && li.previousElementSibling
        ? li.previousElementSibling
        : document.querySelector('ul#autocomplete>li:last-child');
      select(li);
      break;
    case 40: // Down
      li = li && li.nextElementSibling
        ? li.nextElementSibling
        : document.querySelector('ul#autocomplete>li:first-child');
      select(li);
      break;
    case 13: // Enter
      autocomplete.style.display = 'none';
      if (li) {
        window.location.href = li.getAttribute('data-url');
      } else if (input.value.length) {
        window.location.href = `/search/?q=${input.value}`;
      }
    }
  });
})();
