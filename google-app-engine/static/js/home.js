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
, 'position'     : 'absolute'
, 'font-size'    : '24px'
, 'cursor'       : 'pointer'
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

      , slides = j('div.presentation.slide')
      , slide = j(slides[0])
      , slide_width = slide.width()
      , player = j('#about-presentation')
                   .html(j('#presentation-player-template').html())
      , controls = j('#presentation-controls')
      , back = j('#player-controls-back')
      , next = j('#player-controls-next')
      , notice_action = j('#controls-notice-action')
      , notice_index = j('#controls-notice-index')

      , player_offset = player.offset()
      , controls_height, slide_border_width
      ;

    function pause() {
      presentation.impression('stop');
      notice_action.text('paused');
    }

    function play() {
      presentation.impression('play');
      notice_action.text('playing');
    }

    function last_slide() {
      presentation
        .unbind('click', pause)
        .unbind('click', play)
        ;

      notice_action.text('done');
      slides.css('cursor', 'default');
    }

    controls_height = (+controls.css('height').replace(/px/, '') +
                       +controls.css('padding-top').replace(/px/, '') +
                       +controls.css('padding-bottom').replace(/px/, ''));
    slide_border_width = +slide.css('border-top-width').replace(/px/, '');

    player
      .css({
          'width': slide_width +'px'

        , 'height': (slide.height()+
                     controls_height+
                     (slide_border_width *2) +'px')

        , 'border-width': slide_border_width

        , 'border-style': slide.css('border-top-style')
        , 'border-color': slide.css('border-top-color')

        , 'cursor': 'pointer'
        })
      ;

    controls
      .css({'position': 'absolute'})
      .offset({top: player_offset.top + player.height() - controls_height})
      ;

    slides 
      .css(slide_styles)
      .offset(player_offset)
      ;

    presentation
      .toggle(pause, play)
      .bind('impressShowing', function (ev, index) {
        notice_index.text(index +1);

        // Playing the last slide.
        if (index === presentation_intervals.length) {
          last_slide();
        }
      })
      ;

    back.click(function () {
      presentation.impression('back');
    });
    next.click(function () {
      presentation.impression('next');
    });

    j('#presentation-player-intro').click(function () {
      j('#presentation-player-intro').hide();

      j('#controls-notice-length')
        .text(presentation_intervals.length +1);

      controls.show(); // Must show here to calculate width next.
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
      play();
      notice_index.text(1);
      return false;
    });
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

