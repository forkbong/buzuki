'use strict';

const addEventListeners = (selector, type, listener) => {
  document
    .querySelectorAll(selector)
    .forEach((el) => {
      el.addEventListener(type, listener);
    });
};
