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
, jQuery: false
*/

"use strict";

var HOME = (function (window, undef) {
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
      , slide // HTML string of the current slide.
      , deck = [] // Array of slides as HTML strings.
      , stop = true // Flag used to stop and start animation.
      , listeners = {} // Listener functions
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

    // Recursive loop that runs the show.
    function loopy() {
      if (stop) {
        return;
      }

      self.next();
      setTimeout(loopy, slide.interval);
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
      self.goto(1).start();
      broadcast('playing');
      return self;
    };

    // Stop the show.
    self.stop = function () {
      stop = true;
    };

    // Start the show.
    self.start = function () {
      stop = false;
      setTimeout(loopy, slide.interval);
    };

    // Goto the next slide.
    self.next = function () {
      return self.goto(frame +1);
    };

    // Go back one slide.
    self.back = function () {
      return self.goto(frame -1);
    };

    // Add a named signal listener.
    self.addListener = function (name, cb) {
      if (!listeners[name]) {
        listeners[name] = [];
      }
      listeners[name].push(cb);
    };

    return self;
  }

  // Play the page introduction animation.
  function playIntro(callback) {
    var i = 1, t = 700;

    function makecb(n) {
      return function () {
        jq('#intro-'+ n).fadeTo(400, 1);
      };
    }

    for (; i < 5; i += 1) {
      setTimeout(makecb(i), t);
      t += 1200;
    }
    setTimeout(function () {
      jq('#home>p.content').fadeTo(500, 1);
      callback();
    }, t);
  }

  // Start it up on page load.
  jq(function () {
    // Remove the presentation from the DOM.
    var slides = jq('#presentation').remove().children()
      , presentationPlayer // Will be jq object.
      , playerControls // Will be jq object.
      ;

    // Hide the intro content.
    jq('#home>p').fadeTo(0, 0);

    // Inject the presentation player.
    presentationPlayer = jq('<div id="presentation-player"></div>')
      .insertAfter('#home>p.content')
      .css('border', '2px dashed #ccc')
      .html(jq('#presentation-player-template').html())
      ;
    playerControls = jq('#presentation-player-controls').hide();

    // Play the introduction.
    playIntro(function() {});

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
}(window));

