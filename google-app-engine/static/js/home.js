/**
 * General scripting and presentation player for the root domain page.
 *
 * copyright: (c) 2010 by The Fireworks Project.
 * license: MIT, see LICENSE.txt in this directory for more details.
 */

/*jslint
  browser: true
, onevar: true
, undef: true
, nomen: true
, eqeqeq: true
, plusplus: true
, bitwise: true
, regexp: true
, newcap: true
, immed: true
, strict: true
, maxlen: 80
*/

/*global
  window: false
*/

// ECMAScript 5 strict mode.
"use strict";

(function (window) {
  var j;

  function setup_slideshow() {
    j('#presentation').impression();

    j('#about-presentation')
      .css({
          'width': '350px'
        , 'height': '356px'
        })
      .html(j('#presentation-player-template').html())
      ;
  }

  window.jQuery(function (jq) {
    j = jq;
    setup_slideshow();
  });
}(window));

