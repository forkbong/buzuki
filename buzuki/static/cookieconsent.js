'use strict';

window.addEventListener('load', () => {
  window.cookieconsent.initialise({
    palette: {
      popup: {
        background: '#343a40',
        text: '#ffffff',
      },
      button: {
        background: '#343a40',
        text: '#ffffff',
      },
    },
    position: 'bottom',
    content: {
      message: 'Ενδέχεται να παρεισφρήσουνε ορισμένα κούκηζ.',
      dismiss: 'ΟΚ',
      link: 'Πώς κι έτσι?',
    },
  });
});
