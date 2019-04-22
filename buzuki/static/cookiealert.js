'use strict';

(() => {
  const cookieAlert = document.querySelector('.cookiealert');
  const acceptCookies = document.querySelector('.acceptcookies');

  if (!cookieAlert) {
    return;
  }

  // Cookie functions from w3schools
  const setCookie = (name, value, days) => {
    const date = new Date();
    const offset = days * 24 * 60 * 60 * 1000;
    date.setTime(date.getTime() + offset);
    document.cookie = `${name}=${value}; expires=${date.toUTCString()}; path=/`;
  };

  const getCookie = (name) => {
    const cookies = decodeURIComponent(document.cookie).split(';');
    for (let idx = 0; idx < cookies.length; idx += 1) {
      const cookie = cookies[idx].trim();
      const key = `${name}=`;
      if (cookie.indexOf(key) === 0) {
        return cookie.substring(key.length, cookie.length);
      }
    }
    return '';
  };

  // Show the alert if we cant find the 'consent' cookie
  if (!getCookie('consent')) {
    cookieAlert.classList.add('show');
  }

  // When clicking on the agree button, create a 1 year
  // cookie to remember user's choice and close the banner
  acceptCookies.addEventListener('click', () => {
    setCookie('consent', true, 365);
    cookieAlert.classList.remove('show');
  });
})();
