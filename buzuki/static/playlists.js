'use strict';

const playlistsInit = function playlistsInit(songSlug, csrfToken) {
  // Allow Bootstrap dropdown menus to have forms/checkboxes inside,
  // and when clicking on a dropdown item, the menu doesn't disappear.
  $(document).on('click', '.custom-control, .custom-select', (event) => {
    event.stopPropagation();
  });

  const headers = {
    'X-CSRFToken': csrfToken,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };

  const add = function add(playlistSlug, root = null) {
    const body = {
      slug: songSlug,
      root,
    };
    fetch(`/api/playlists/${playlistSlug}/songs/`, {
      method: 'post',
      headers,
      body: JSON.stringify(body),
    });
  };

  const remove = function remove(playlistSlug) {
    const body = {slug: songSlug};
    fetch(`/api/playlists/${playlistSlug}/songs/${songSlug}`, {
      method: 'delete',
      headers,
      body: JSON.stringify(body),
    });
  };

  $('.playlist-checkbox').on('change', (event) => {
    const $element = $(event.target);
    const $elementRoot = $(`#root-${$element.attr('id')}`);
    const playlistSlug = $element.data('playlist-slug');
    if ($element.is(':checked')) {
      add(playlistSlug);
      $elementRoot.show();
    } else {
      remove(playlistSlug);
      $elementRoot.hide();
    }
  });

  $('.playlist-root').on('change', (event) => {
    const $element = $(event.target);
    const playlistSlug = $element.data('playlist-slug');
    let root = event.target.value;
    if (root === '-') {
      root = null;
    }
    add(playlistSlug, root);
  });
};
