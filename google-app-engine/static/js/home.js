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
  jQuery: false
*/

// ECMAScript 5 strict mode.
"use strict";

var HOME = (function (jQuery) {
  var jq = jQuery.noConflict(true) // Safely acquire the jQuery object.

    // The presentation player module.
    , player
    ;

  // Constructor for the presentation player module.
  // `viewport` A jQuery object representing the viewport of the player.
  // `slides` An array of DOM nodes representing the presentation slides.
  // `interval` Default interval between slides.
  function constructPlayer(viewport, slides, interval) {
    var self = {}
      , frame = 0 // The current frame number.
      , slide // The interval and HTML string of the current slide.
      , deck = [] // Array of slides as objects with interval and HTML string.
      , listeners = {} // Listener functions
      , current_timeout // The id of the current window.setTimeout().
      , stopped = true
      ;

    function makeSlide(element, i) {
      var el = jq(element)
        , inc = el.attr('interval');
      return {interval: inc ? +inc : interval, content: el.html()};
    }

    deck = jq.map(slides, makeSlide);

    // Utility to broadcast to listeners of a signal.
    function broadcast(signal) {
      var i = 0, len;
      if (listeners[signal]) {
        len = listeners[signal].length;
        for (; i < len; i += 1) {
          listeners[signal][i]();
        }
      }
    }

    // Goto a specific slide.
    self.goto = function (n) {
      if (deck[n -1]) {
        slide = deck[n -1];
        viewport.html(slide.content);
        frame = n;
      }
      return self;
    };

    // Play the show from the beginning.
    self.play = function () {
      stopped = false;
      self.goto(1).start();
      broadcast('playing');
      return self;
    };

    // Stop the show.
    self.stop = function () {
      stopped = true;
      clearTimeout(current_timeout);
      return self;
    };

    // Start the show.
    self.start = function () {
      stopped = false;
      current_timeout = setTimeout(self.next, slide.interval);
      return self;
    };

    // Goto the next slide.
    self.next = function () {
      clearTimeout(current_timeout);
      self.goto(frame +1);
      if (!stopped) {
        current_timeout = setTimeout(self.next, slide.interval);
      }
      return self;
    };

    // Go back one slide.
    self.back = function () {
      clearTimeout(current_timeout);
      self.goto(frame -1);
      if (!stopped) {
        current_timeout = setTimeout(self.next, slide.interval);
      }
      return self;
    };

    // Add a named signal listener.
    self.addListener = function (name, cb) {
      if (!listeners[name]) {
        listeners[name] = [];
      }
      if (typeof cb === 'function') {
        listeners[name].push(cb);
      }
    };

    return self;
  }

  // Start it up on page load.
  jq(function () {
    // Remove the presentation from the DOM.
    var slides = jq('#presentation').remove().children()
      , presentationPlayer // Will be jq object.
      , playerControls // Will be jq object.
      ;

    // Inject the presentation player.
    presentationPlayer = jq('<div id="presentation-player"></div>')
      .insertAfter('#intro')
      .css('border', '2px dashed #ccc')
      .html(jq('#presentation-player-template').html())
      ;
    playerControls = jq('#presentation-player-controls').hide();

    // Load the presentation.
    player = constructPlayer(jq('#presentation-viewport'), slides, 3000);
    player.addListener('playing', function () {
      playerControls.show();
      jq('#player-play-pause').toggle(
        function () {
          player.stop();
          jq(this).html('play');
        },
        function () {
          player.start();
          jq(this).html('pause');
        });
      jq('#player-back').click(player.back);
      jq('#player-next').click(player.next);
      jq('#player-start').click(function () { player.goto(1); });
    });
    jq('#presentation-start-button').click(function () {
      player.play();
      return false;
    });

    // Inject the comments section.
    jq('<div id="comments"></div>')
      .insertAfter('#home')
      .html(jq('#comments-template').html())
      ;
  });
}(jQuery));

