'use strict';

module.exports = function (grunt) {
  grunt.initConfig({
    terser: {
      target: {
        files: {
          'buzuki/static/dist/buzuki.min.js': ['buzuki/static/*.js'],
        },
      },
    },
    cssmin: {
      target: {
        files: {
          'buzuki/static/dist/buzuki.min.css': ['buzuki/static/*.css'],
        }
      }
    }
  });
  grunt.loadNpmTasks('grunt-terser');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.registerTask('default', ['terser', 'cssmin']);
};
