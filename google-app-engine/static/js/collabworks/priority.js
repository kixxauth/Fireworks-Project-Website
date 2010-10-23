/**
 * @fileOverview Page JavaScript for the Uber priority todo list.
 * @author Kris Walker <kris@kixx.name>
 * @version 0.2
 *
 * All source code is (c) 2010 by contributors to The Fireworks Project
 * Inc. (http://www.fireworksproject.com) and, unless otherwise indicated, is
 * licensed under the MIT license.
 */

/*jslint
  laxbreak: true
, onevar: true
, undef: true
, nomen: true
, eqeqeq: true
, plusplus: true
, bitwise: true
, regexp: true
, immed: true
, strict: true
*/

/*global window: false */

"use strict";

// A jQuery extension for walking a DOM tree.
(function (window) {
  var jQuery = window.jQuery;

  jQuery.fn.walk = function (action) {
    var walk, node_action, root_children = this.children();
    if (root_children.length === 0) {
      return;
    }

    node_action = function () {
      var ch = jQuery(this), children = ch.children();
      action(this, ch);
      if (children.length > 0) { walk(children); }
    };

    walk = function (children) {
      children.each(node_action);
    };
    walk(root_children);
  };
}(window));

// A jQuery extension for showing centered UI notifications.
(function (window) {
  var jQuery = window.jQuery;

  jQuery.fn.appendCenter = function (opts) {
    opts = opts || {};
    var src = typeof opts.src === 'string' ? opts.src : ''
      , width = typeof opts.width === 'number' ? opts.width : 50
      , height = typeof opts.height === 'number' ? opts.height : 50
      , node = (opts.node || {}).jquery ? opts.node : jQuery('<img />')
      , nodes = []
      ;

    node
      .attr('src', src)
      .css({
          position: 'absolute'
        , left: '50%'
        , top: '50%'
        , 'margin-left': -Math.floor(width/2)
        , 'margin-top': -Math.floor(height/2)
        })
      ;

    jQuery(this[0]).css('position', 'relative');
    this.each(function (i, el) {
      var n = node.clone();
      jQuery(this).append(n);
      nodes.push(n[0]);
    });

    this.removeCenter = function () {
      jQuery(nodes).remove();
      nodes = [];
    };

    return this;
  };
  jQuery.fn.removeCenter = jQuery.noop;
}(window));

(function (window, opts, undef) {
    // Global shortcuts.
  var setTimeout = window.setTimeout
    , hasown = Object.prototype.hasOwnProperty
    , tostr = Object.prototype.toString
    , doc = window.document

    // Global namespace clean up and library shortcuts.
    // DataTables plugin depends on global `jQuery`
    // , j = window.jQuery.noConflict(true)
    , j = window.jQuery
    , raphael = window.Raphael.ninja()
    , u = window._.noConflict()

    // Will contain the DOM ready promise
    , ready

    // Report an error to the UI with a dialog box.
    , show_error

    // Object containing the table controls (defined later).
    , datatable

    , component_diagram

    // Functions defined later
    , sort_by_value
    , calc_priority
    ;

  // Generic object creator.
  function create_object(spec) {
    function F() {}
    F.prototype = spec;
    return new F();
  }

  // A trim function to remove leading and trailing whitespace from strings.
  function trim(str) {
    return (str +'').replace(/^\s\s*/, '').replace(/\s\s*$/, '');
  }

  function shortnum(n, l) {
    return parseFloat(n.toFixed(l));
  }

  // Promise constructor.
  function promise() {
    var that = {}
      // Shortcuts
      , unresolved = 'unresolved', fulfilled = 'fulfilled', smashed = 'smashed'
      , slice = Array.prototype.slice

      // Carries the internal state of this promise.
      , status = unresolved

      // Progress reports.
      , reports = []

      // The outcome of the fillfilled promise (an array of arguments).
      , outcome

      // List of callbacks waiting for fulfillment.
      , waiting = []

      // List of callbacks waiting for an error.
      , dreading = []

      // List of callbacks listening for progress reports.
      , watching = []
      ;

    // The proper way to call a callback.
    function callback(fn, args) {
      try {
        fn.apply(null, args);
      } catch (e) {
        // Report a callback error after it can no longer get in our way.
        setTimeout(function () { throw e; }, 0);
      }
    }

    // Broadcast to a list of callbacks.
    function broadcast(callbacks, args) {
      var i = 0;
      for (; i < callbacks.length; i += 1) {
        callback(callbacks[i], args);
      }
    }

    // Resolve this promise.
    function resolve(deed, args) {
      if (status !== unresolved) {
        throw {
          name: 'PromiseError'
        , message: 'This promise has already been resolved: '+ status
        };
      }

      broadcast(
          deed === fulfilled ? waiting : dreading
        , outcome = args
        );
      waiting = null; dreading = null; status = deed;
    }

    // Add a callback to the waiting or dreading list.
    function add_fn(deed, fn) {
      if (typeof fn !== 'function') { return; }

      if (status !== unresolved) { callback(fn, outcome); return; }

      (deed === fulfilled ? waiting : dreading).push(fn);
    }

    // Create a new public function representing this promise.
    function pub() {
      return function (fn_fulfill, fn_smashed, fn_progress) {
        add_fn(fulfilled, fn_fulfill);
        add_fn(smashed, fn_smashed);
        if (typeof fn_progress === 'function') {
          watching.push(fn_progress);
          callback(fn_progress, [status, reports]);
        }
        return pub();
      };
    }

    that.fulfill = function () {
           resolve(fulfilled, slice.call(arguments));
         };
    that.smash = function () {
           resolve(smashed, slice.call(arguments));
         };
    that.report = function (report) {
           reports.push({status: status, report: report});
           broadcast(watching, [status, reports]);
         };
    that.handle = pub();
    return that;
  }

  // Assign the DOM ready promise.
  ready = (function () {
    var my = promise();

    j(function (j) {
      my.fulfill(j);
    });

    return my.handle;
  }());

  function waiting_ui(jnode) {
    jnode.appendCenter({
        src: opts.waiting_img_loc
      , width: 235
      , height: 235
      });

    return function() {
      jnode.removeCenter();
    };
  }

  popup = (function popup() {
    var that = {}
      , j
      , open
      , do_open
      , jpopup
      , jwin
      ;

    do_open = function () {};

    function handle_close(ev) {
      jpopup.hide();
      do_open = open;
      j(window.document).unbind('click', handle_close);
    }

    open = function (content) {
      var width = jwin.width();

      j('#popup-content')
        .empty()
        .append(content)
        ;
      jpopup
        .css({
            top: jwin.scrollTop() + (jwin.height() /7)
          , left: (width / 2) - (width /4)
          , width: width / 2
          })
        .show()
        ;

      do_open = j.noop;
      setTimeout(function () {
        j(window.document).click(handle_close);
      }, 100);
    };

    ready(function (jQuery) {
      j = jQuery;
      jwin = j(window)
      jpopup = j('#popup')
                 .css({
                     position: 'absolute'
                   })
                 .hide()
                 ;
      j('#popup-control').hover(
          function () {
            j(this).addClass('ui-state-hover');
          }
        , function () {
            j(this).removeClass('ui-state-hover');
          });
      do_open = open;
    });

    return function (content) { do_open(content); };
  }());

  show_error = (function () {
    var dialog, template
      , not_ready
      ;

    not_ready = ready(function () { not_ready = false; });

    function close() {
      dialog.dialog('close');
    }

    function do_open(err, msg, status) {
      var buttons = {}
        , data = {
            err: err.name +': '+ err.message +
                 ' ('+ err.fileName +':'+ err.lineNumber +')'
          , message: msg
          , status: status
          }
        ;

      if (!dialog || !template) {
        template = j('#error-dialog-template').template();
        dialog = j('#error-dialog').dialog({
            autoOpen: false
          , draggable: false
          , resizable: false
          })
          .append(j.tmpl(template, data))
          ;
      }
      else {
        dialog.empty().append(j.tmpl(template, data));
      }

      // We're gonna die.
      if (status === 1) {
        buttons["That's a bummer"] = close;
      }
      // We might be OK.
      else {
        buttons.OK = close;
      }

      dialog.dialog('option', {
          buttons: buttons
        , width: j(window).width() / 2.5
        })
        .dialog('open')
        ;

      // IE needs help.
      setTimeout(function () { throw err; }, 0);
    }

    return function (err, msg, status) {
      if (not_ready) {
        return not_ready(function () {
            do_open(err, msg, status);
          });
      }
      do_open(err, msg, status);
    };
  }());

  datatable = {
    columnize: function (original, data) {
      var i = 0, len = data.list.length, item;

      function mapper(val, name) {
        // This is a terrible workaround for the fact that we may or may not be
        // mutating data. This could fail at any time without warning.
        return typeof val === 'number' ?
                 name +': '+ Math.round(val * 100) : val;
      }

      function find_orphans(dep, k, list) {
        // More terrible workarounds. Forget you've seen it.
        k = typeof dep === 'string' ? dep.split(':')[0] : k;
        if (!hasown.call(data.dict, k)) {
          this.push([
              k
            , 'orphan'
            , 0
            , 9999
            ]);
        }
      }

      for (; i < len; i += 1) {
        item = data.list[i];
        u.each(item.dependencies, find_orphans, original);
        item.dependencies = u.map(item.dependencies, mapper);
        item.dependents = u.map(item.dependents, mapper);
        original.push([
            item.name
          , item.classname
          , item.value
          , item.rank
          ]);
      }
      return original;
    }

  , init: function (data) {
      var p = promise(), template;

      function click_handler() {
        var k = j(this).children('td').html();
        if (hasown.call(data.dict, k)) {
          if (!template) {
            template = j('#item-popup-template').template();
          }
          popup(j.tmpl(template, data.dict[k]));
        }
      }

      u.defer(function () {
        try {
          j('#datatable').dataTable({
              aaData: datatable.columnize([], data)
            , aaSorting: []
            , aoColumns: [
                {sTitle: 'Name'}
              , {sTitle: 'Class'}
              , {sTitle: 'Value'}
              , {sTitle: 'Rank'}
              ]
            , bPaginate: false
            , bAutoWidth: false
            , fnRowCallback: function (row, d, i) {
                j(row)
                  .bind('click.tablecol', click_handler)
                  ;
                return row;
              }
            });
        } catch (table_err) {
          p.smash(table_err);
          return;
        }
        p.fulfill();
      });
      return p.handle;
    }

  , update: function () {
      throw new Error('datatables.update() is not implemented yet.');
    }
  };

  component_diagram = (function () {
    var template;

    function mapper(val, name) {
      // This is a terrible workaround for the fact that we may or may not be
      // mutating data. This could fail at any time without warning.
      return typeof val === 'number' ?
               name +': '+ Math.round(val * 100) : val;
    }

    function draw_item(item, x, y, width, height) {
      var rv = item;
      rv.x = x;
      rv.y = y;
      rv.width = width;
      rv.height = height;
      rv.color = raphael.getColor();
      rv.corner = 7
      rv.text = item.name;
      return rv;
    }

    function draw(node, width, height, vectors) {
      var canvas = raphael(node, width, height);
      u.each(vectors, function (vector) {
        var box, txt;

        vector.dependencies = u.map(vector.dependencies, mapper);
        vector.dependents = u.map(vector.dependents, mapper);

        box = canvas
            .rect(
                vector.x +4
              , vector.y +4
              , vector.width -10
              , vector.height -10
              , vector.corner
              )
            .attr({
                fill: vector.color
              , 'fill-opacity': .2
              , stroke: vector.color
              , 'stroke-width': 3
              , cursor: 'pointer'
              }).node
            ;

        if (vector.text.length < vector.width * .08) {
          txt = canvas
              .text(
                  Math.floor(vector.x +(vector.width / 2))
                , Math.floor(vector.y +(vector.height / 2))
                , vector.text
                )
              .attr({
                  fill: '#fff'
                , 'font-size': 20
                , cursor: 'pointer'
                }).node
              ;
        }

        j(txt ? [box, txt] : box).click(function () {
            if (!template) {
              template = j('#item-popup-template').template();
            }
            popup(j.tmpl(template, vector));
          });
      });
    }

    function walk(dict, root, width, height, x, y) {
      var maxy = 0, vectors = [];

      function recurse(item, width, x, y) {
        var n, dwidth;
        item.visiting = true;

        vectors.push(draw_item(item, x, y, width, height));

        y += height;
        maxy = y > maxy ? y : maxy;

        for (n in item.dependencies) {
          if (hasown.call(item.dependencies, n) && !(dict[n] || {}).visiting) {
            dwidth = Math.floor(item.dependencies[n] * width);
            if (hasown.call(dict, n)) {
              recurse(dict[n], dwidth, x, y);
            }
            x += dwidth;
          }
        }
        item.visiting = false;
      }

      recurse(root, width, x, y);
      return {height: maxy, vectors: vectors};
    }

    return function (opts) {
      raphael.getColor.reset();
      opts = opts || {};
      var width = opts.width || 600
        , v = walk(
            opts.dict || {}
          , opts.root
          , width
          , opts.row_height || 50
          , x = typeof opts.x === 'number' ? opts.x : 0
          , y = typeof opts.y === 'number' ? opts.y : 0
          )
        ;

      draw(opts.node, width, v.height, v.vectors);
    };
  }());

  // Using jQuery to parse a document is probably not the most efficient...
  // But who's counting?
  function parse_page_data(root_node) {
    var rv = {list: [], dict: {}};

    function make_item() {
      var that = {}
        , total_value = 0
        , raw_values = []
        ;

      that.dependencies = {};
      that.depslist = [];
      that.name = 'anonymous';
      that.value = 0;
      that.score = 0;
      that.rank = 0;

      that.toString = function () {
        return that.name;
      };

      that.set_name = function (val) {
        if (!val || typeof val !== 'string') {
          throw new TypeError('"name" value must be a string > 1 character.');
        }
        that.name = val;
      };
      that.set_classname = function (val) {
        that.classname = typeof val === 'string' ?
                         val : 'unclassified';
      };
      that.set_description = function (val) {
        that.description = typeof val === 'string' ?
                           val : 'No description.';
      };
      that.set_content = function (val) {
        that.content = typeof val === 'string' ?
                       val : 'No content.';
      };
      that.set_dependency = function (val) {
        var d = val.split(':')
          , k = trim(d[0])
          , value = parseInt(trim(d[1]), 10)
          , i = 0
          ;

        if (!k || !value || isNaN(value)) {
          throw new TypeError('Invalid dependency declaration: "'+
                              val +'" for "'+ that.name +'".');
        }

        raw_values.push([k, value]);
        total_value += value;

        for (; i < raw_values.length; i += 1) {
          that.dependencies[raw_values[i][0]] = raw_values[i][1] / total_value;
        }
        that.depslist.push(k);
      };
      return that;
    }

    function parse_node(list, dict) {
      var current_item;

      return function (el, jel) {
        if (el.nodeName.toUpperCase() !== 'LI') { return; }

        if (jel.hasClass('dependency')) {
          current_item.set_dependency(jel.html());
        }
        else if (jel.hasClass('name')) {
          current_item.set_name(jel.html());
          dict[current_item.name] = current_item;
        }
        else if (jel.hasClass('classname')) {
          current_item.set_classname(jel.html());
        }
        else if (jel.hasClass('description')) {
          current_item.set_description(jel.html());
        }
        else if (jel.hasClass('content')) {
          current_item.set_content(jel.html());
        }
        else if (jel.hasClass('item')) {
          list.push(current_item = make_item());
        }
      };
    }

    root_node.walk(parse_node(rv.list, rv.dict));
    return rv;
  }

  // Find and score dependents for each item.
  function score_dependents(list) {
    var i = 0
      , len = list.length
      , n
      , deps = {}
      ;
    for (; i < len; i += 1) {
      for (n in list[i].dependencies) {
        if (hasown.call(list[i].dependencies, n)) {
          if (!hasown.call(deps, n)) {
            deps[n] = {};
          }
          deps[n][list[i].name] = list[i].dependencies[n];
        }
      }
    }
    return deps;
  }

  // Recursively calculate valuations.
  function calc_valuations(item, value, dict) {
    var n, deps = item.dependencies;

    item.value = shortnum(item.value + (value * 100), 2);
    item.visiting = true;

    for (n in deps) {
      if (hasown.call(deps, n) &&
          hasown.call(dict, n) && // Some dependencies may not be listed.
          !dict[n].visiting) { // Prevent circular dependency.
        calc_valuations(dict[n], value * deps[n], dict);
      }
    }
    item.visiting = false;
  }

  // Collection of functions for calculating priority rank.
  calc_priority = {
    // Use the list of dependency names and the dictionary of dependencies to
    // sort the dependencies by valuation and return the sorted list of names.
    sort_deps: function (list, dict) {
      list.sort(function (a, b) {
        return dict[a] > dict[b] ? -1 : 1;
      });
      return list;
    }

  , sort: function (list) {
      list.sort(function (a, b) {
        return a.score > b.score ? -1 : 1;
      });
      return list;
    }

  , rank: function (list) {
      u.each(list, function (item, i) {
        item.rank = i + 1;
      });
      return list;
    }

    // Return a list of items scored and sorted by priority.
  , calc: function (list, dict) {
      var i = list.length, score = 0;

      function recurse(item, score, dict) {
        var deps = calc_priority.sort_deps(item.depslist, item.dependencies)
          , i = deps.length
          , n
          ;

        item.visiting = true;
        item.score = (score += 1);

        while (i > 0) {
          i -= 1;
          n = deps[i];
          if (hasown.call(dict, n) && !dict[n].visiting) {
            score = recurse(dict[n], score, dict);
          }
        }

        item.visiting = false;
        return score;
      }

      while (i > 0) {
        i -= 1;
        score = recurse(list[i], score, dict);
      }

      return calc_priority.rank(calc_priority.sort(list));
    }
  };

  sort_by_value = (function () {
    var classranks = {
          'GOAL': 100
        , 'ABSTRACTION': 80
        , 'ABSTRACT PROCESS': 60
        , 'CONCRETE PROCESS': 40
        , 'TASK': 20
        };

    return function (list) {
      list.sort(function (a, b) {
        if (a.value === b.value) {
          return ((classranks[a.classname.toUpperCase()] >
                  classranks[b.classname.toUpperCase()]) ? -1 : 1);
        }
        return a.value > b.value ? -1 : 1;
      });
      return list;
    };
  }());

  function Dataclass(list, regx, sort) {
    this.items = u.reduce(list, [], function (rv, item) {
        if (!regx.test(item.classname)) {
          return rv;
        }
        var new_item = {
          name: item.name
        , dependencies: item.dependencies
        , classname: item.classname
        , description: item.description
        , content: item.content
        , dependencies: item.dependencies
        , dependents: item.dependents
        , rank: item.rank
        , value: item.value
        };
        rv.push(item);
        return rv;
    });

    this.items.sort(sort);
  }
  // opts.node
  // opts.width
  // opts.height
  // opts.template
  Dataclass.prototype.draw = function (opts) {
    opts = opts || {};
    var node = opts.node
      , width = typeof opts.width === 'number' ? opts.width : 300
      , height = typeof opts.height === 'number' ? opts.height : 70
      , canv = raphael(
                   node
                 , width
                 , Math.ceil(height * this.items.length)
                 )
      , template = opts.template
      , y = -(height)
      , vmargin = Math.round(height * .25)
      ;

    raphael.getColor.reset();

    function mapper(val, name) { return name +': '+ Math.round(val * 100); }

    u.each(this.items, function (item) {
      var color = raphael.getColor()
        , box = canv
            .rect(
                3
              , (y += height) +3
              , width - 6
              , height - vmargin -6
              , 20
              )
            .attr({
                fill: color
              , 'fill-opacity': .2
              , stroke: color
              , 'stroke-width': 3
              , cursor: 'pointer'
              })
            .node

        , txt = canv
            .text(
                Math.floor(width / 2)
              , Math.floor(y + 3 +((height - vmargin -6) / 2))
              , item.name
              )
            .attr({
                fill: '#fff'
              , 'font-size': 20
              , cursor: 'pointer'
              })
            .node
        ;

      item.dependencies = u.map(item.dependencies, mapper);
      item.dependents = u.map(item.dependents, mapper);

      j([box, txt]).click(function () { popup(j.tmpl(template, item)); });
    });
  };

  function get_components(list) {
    var dict = {}, reg = /[C,c]+omponent/;
    list = u.reduce(list, [], function (list, item) {
        if (!reg.test(item.classname)) {
          return list;
        }
        var new_item = {
          name: item.name
        , dependencies: item.dependencies
        , classname: item.classname
        , description: item.description
        , content: item.content
        , dependencies: item.dependencies
        , dependents: item.dependents
        , rank: item.rank
        , value: item.value
        };
        dict[item.name] = new_item;
        list.push(new_item);
        return list;
    });

    return {list: list, dict: dict};
  }

  function get_data(root_node) {
    var p = promise();

    u.defer(function () {
      var data, deps, roots = [];
      try {
        data = parse_page_data(root_node);
      } catch (parsing_err) {
        p.smash(parsing_err);
        return;
      }
      try {
        deps = score_dependents(data.list);
        u.each(data.dict, function (item, name, dict) {
          if (hasown.call(deps, name)) {
            item.dependents = deps[name];
          }
          else {
            item.dependents = {};
            roots.push(item);
          }
        });
        if (roots.length !== 1) {
          throw new Error('There should be 1 and only 1 root item '+
                          'with no dependents: '+ roots);
        }
        data.root = roots[0];
      } catch (deps_err) {
        p.smash(deps_err);
        return;
      }
      try {
        calc_valuations(data.root, 1, data.dict);
      } catch (valuation_err) {
        p.smash(valuation_err);
        return;
      }
      try {
        data.list = sort_by_value(data.list);
        calc_priority.calc(data.list, data.dict);
      } catch (pri_err) {
        p.smash(pri_err);
        return;
      }
      try {
        data.components = get_components(data.list);
      } catch (comp_err) {
        p.smash(comp_err);
        return;
      }
      try {
        data.tasks = new Dataclass(data.list, /[T,t]+ask/,
            function (a, b) {
              return a.rank < b.rank ? -1 : 1;
            });
        data.assets = new Dataclass(data.list, /[A,a]+sset/,
            function (a, b) {
              return a.value > b.value ? -1 : 1;
            });
        data.processes = new Dataclass(data.list, /[P,p]+rocess/,
            function (a, b) {
              return a.value > b.value ? -1 : 1;
            });
      } catch (dataclass_err) {
        p.smash(dataclass_err);
        return;
      }
      p.fulfill(data);
    });

    return p.handle;
  }

  // Start the application.
  ready(function (j) {
    j('a.popover')
      .button()
      .click(function () {
          popup(j(j(this).attr('href')).clone().children());
          return false;
        });
    j('div.popover').hide();
    j('div.tabs').css('height', Math.floor(j(window).height() * 0.7));
    j('#data').hide();
    j('#tabs').tabs();

    var rm_waiting = waiting_ui(j('div.tabs'));

    get_data(j('#data'))(
      function (data) {
        // opts.node
        // opts.width
        // opts.height
        // opts.template
        var pop_tmp = j('#item-popup-template').template();
        data.tasks.draw({
            node: doc.getElementById('todo-list')
          , width: 300
          , height: 70
          , template: pop_tmp
          });
        data.assets.draw({
            node: doc.getElementById('asset-list')
          , width: 300
          , height: 70
          , template: pop_tmp
          });
        data.processes.draw({
            node: doc.getElementById('process-list')
          , width: 300
          , height: 70
          , template: pop_tmp
          });
      }

      // Handle data errors here, and we will not have to do it again.
    , function (err) {
        //console.error(err);
        show_error(
              err
            , ('There was an error parsing the data '+
               'which prevents us from going any further:')
            , 1
            );
         rm_waiting();
      }
      )(
      function (data) {
        //console.debug(data);
        datatable.init(data)(
          function () {
            rm_waiting();
          }
        , function (table_err) {
            show_error(
                  table_err
                , ('There was an error creating the data table.')
                , 0
                );
            rm_waiting();
          });
      }
    )(
      function (data) {
        //console.debug(data);
        if (!hasown.call(data.components.dict, data.root.name)) {
          show_error(
                new TypeError('The root node is not a component: '+ data.root)
              , ('The root item is not a business component '+
                 'like it was expected to be.')
              , 0
              );
        }
        component_diagram({
            dict: data.components.dict
          , node: doc.getElementById('component-diagram')
          , row_height: 100
          , root: data.components.dict[data.root.name] || data.root
          , width: 900 
          , x: 0
          , y: 0
          });
      }
    )(
      function () {
        j('div.tabs')
          .css({
              height: '100%'
            , 'min-height': (j(window).height() -80) +'px'
            });
      }
     );

    j('#data-view').append(j('#data').detach().show());
  });
}(window, {

  waiting_img_loc: '/css/img/loading-000000.gif'
}));
