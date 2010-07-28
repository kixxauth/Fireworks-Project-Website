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

var SPEC = {};

SPEC.slideShowIntervals = [
  7000
, 5500
, 9000
, 7000
, 6500
, 7000
, 8000
, 10500
, 7500
, 9500
, 8500
, 7500
];

SPEC.slideStyles = {
  'margin-top'   : '0'
, 'margin-right' : '0'
, 'margin-left'  : '0'
, 'margin-bottom': '0'
, 'float'        : 'none'
, 'border-top'   : 'none'
, 'border-left'  : 'none'
, 'border-right' : 'none'
, 'font-size'    : '24px'
};

(function (window) {
  var j
    , spec = window.SPEC || {}
    , presentation_intervals = spec.slideShowIntervals || []
    , slide_styles = spec.slideStyles || {}
    ;

  function setup_slideshow() {
    var presentation = j('#presentation').impression({
          intervals: presentation_intervals
        })

      , slide = j(j('div.presentation.slide').css(slide_styles)[0])
      , slide_width = slide.width()
      , slide_height = slide.height()
      , player = j('#about-presentation')
      , controls, back, next, notice_action, notice_index
      , intro, slide_border_width
      ;

    // Create and insert the player controls.
    player.html(j('#presentation-player-template').html());
    controls = j('#presentation-controls')
    back = j('#player-controls-back');
    next = j('#player-controls-next');
    intro = j('#presentation-player-intro');
    notice_action = j('#controls-notice-action');
    notice_index = j('#controls-notice-index');

    function pause() {
      notice_action.text('paused:');
      presentation.impression('stop');
    }

    function play() {
      notice_action.text('playing:');
      presentation.impression('play');
    }

    // Move the presentation slides into position.
    presentation
      .detach()
      .appendTo(player)
      .bind('impressShowing', function (ev, index) {
        notice_index.text(index +1);

        // Playing the last slide.
        if (index === presentation_intervals.length) {
          player
            .unbind('click', pause)
            .unbind('click', play)
            .css('cursor', 'default')
            ;
          notice_action.text('done:');
        }
      })
      ;

    slide_border_width = +slide.css('border-bottom-width').replace(/px/, '');

    // Apply styles and event handlers.
    player
      .css({
          'border-width': slide_border_width
        , 'border-style': slide.css('border-bottom-style')
        , 'border-color': slide.css('border-bottom-color')
        , 'cursor': 'pointer'
        })
      .width(slide_width)
      .height(slide_height+
              controls.height()+
              (+controls.css('padding-top').replace(/px/, ''))+
              (+controls.css('padding-bottom').replace(/px/, ''))+
              slide_border_width)
      .click(function player_click() {
        var self = j(this);
        self.unbind('click', player_click);
        intro.hide();

        // Position and show the player controls.
        controls
          .css('top', (slide_height + slide_border_width) +'px')
          // Must show controls now to calculate position and width.
          .show()
          ;

        j('#player-controls-notice').width((function () {
          var left_margin = +back.css('margin-left').replace(/px/, '')
            , right_margin = +next.css('margin-right').replace(/px/, '')
            ;

          return (slide_width -
                  back.width() -
                  next.width() -
                  left_margin -
                  right_margin);
        }()));
        j('#controls-notice-length')
          .text(presentation_intervals.length +1);

        play();

        j('#player-back-control').click(function () {
          presentation.impression('back');
          return false;
        });
        j('#player-forward-control').click(function () {
          presentation.impression('next');
          return false;
        });
        self.toggle(pause, play);

        return false;
      })
      ;

    intro.show();
  }

  window.jQuery(function (jq) {
    j = jq;

    // Firefox likes to remember scroll positioning for its users, which
    // actually screws with our positioning in JavaScript, so we set it to a
    // nice default here.
    j(window).scrollTop(0);

    setup_slideshow();
  });
}(window));

