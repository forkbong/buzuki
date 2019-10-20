'use strict';

/* global addEventListeners */

const playlistsInit = (songSlug, csrfToken) => {
  // Allow Bootstrap dropdown menus to have forms/checkboxes inside,
  // and when clicking on a dropdown item, the menu doesn't disappear.
  addEventListeners('.custom-control,.custom-select', 'click', (event) => {
    event.stopPropagation();
  });

  const headers = {
    'X-CSRFToken': csrfToken,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };

  const add = (playlistSlug, root = null) => {
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

  const remove = (playlistSlug) => {
    const body = {slug: songSlug};
    fetch(`/api/playlists/${playlistSlug}/songs/${songSlug}`, {
      method: 'delete',
      headers,
      body: JSON.stringify(body),
    });
  };

  addEventListeners('.playlist-checkbox', 'change', (event) => {
    const element = event.target;
    const elementRoot = document.getElementById(`root-${element.id}`);
    const playlistSlug = element.getAttribute('data-playlist-slug');
    if (element.checked) {
      add(playlistSlug);
      elementRoot.style.display = 'block';
    } else {
      remove(playlistSlug);
      elementRoot.style.display = 'none';
    }
  });

  addEventListeners('.playlist-root', 'change', (event) => {
    const element = event.target;
    const playlistSlug = element.getAttribute('data-playlist-slug');
    let root = element.value;
    if (root === '-') {
      root = null;
    }
    add(playlistSlug, root);
  });
};
