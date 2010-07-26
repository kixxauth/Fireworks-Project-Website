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
    var presentation = j('#presentation').impression({
          intervals: {
            'slide-a': 7000
          , 'slide-1': 5000
          , 'slide-2': 5000
          , 'slide-3': 6500
          , 'slide-4': 6000
          , 'slide-5': 6000
          , 'slide-55': 7000
          , 'slide-7': 10000
          , 'slide-6': 7000
          , 'slide-8': 8000
          , 'slide-9': 8000
          , 'slide-10': 7000
          }
        })

      , slide = j(j('div.presentation.slide')[0])
      , slide_width = slide.width()
      , player = j('#about-presentation')
                   .html(j('#presentation-player-template').html())
      , controls = j('#presentation-controls')
      , back = j('#player-controls-back')
      , next = j('#player-controls-next')
      , controls_notice = j('#player-controls-notice')

      , player_offset = player.offset()
      , controls_height, slide_border_width
      ;

    function pause() {
      presentation.impression('stop');
      controls_notice.text('paused');
    }

    function play() {
      presentation.impression('play');
      controls_notice.text('playing');
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

    j('div.presentation.slide')
      .css({
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
        })
      .offset(player_offset)
      ;

    presentation.toggle(pause, play);

    back.click(function () {
      presentation.impression('back');
    });
    next.click(function () {
      presentation.impression('next');
    });

    j('#presentation-player-intro').click(function () {
      j('#presentation-player-intro').hide();
      controls_notice.text('playing');
      controls.show();
      controls_notice.width((function () {
        var left_margin = +back.css('margin-left').replace(/px/, '')
          , right_margin = +next.css('margin-right').replace(/px/, '')
          ;

        return (slide_width -
                back.width() -
                next.width() -
                left_margin -
                right_margin);
      }()));
      presentation.impression('play');
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

