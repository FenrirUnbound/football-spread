var loadingBar = loadingBar || {},
    scores = scores || {};

$(document).ready(function() {
    scores.init();
    spread.init();
});

scores = (function($) {
  /*** Constants and Definitions ***/
  var AWAY_NAME = "away_name",
      AWAY_SCORE = "away_score",
      GAME_CLOCK = "game_clock",
      GAME_ID = "game_id",
      GAME_LINE = "spread_odds",
      GAME_MARGIN = "spread_margin",
      GAME_START_DAY = "game_day",
      GAME_START_TIME = "game_time",
      GAME_STATUS = "game_status",
      HOME_NAME = "home_name",
      HOME_SCORE = "home_score",
      SCORE_URL = 'http://matsumoto26sunday.appspot.com/scores';

  /*** Global Variables ***/
  var templates_ = {},
      scores_ = [];

  /**
   * Get the game scores.
   *
   * @return {array} This returns an array of arrays, where each array
   *     relates to a specific game and contains data pertaining to it.
   */
  function getScores() {
    return scores_;
  }

  /**
   * Initializes the module.
   *
   * !!! THIS MUST BE CALLED BEFORE USING THE MODULE
   *
   * This directs the proper order of operations in order to setup and
   * initialize the module, including any and all dependencies.
   */
  function init() {
    var path = "./scripts/templates/scoreboard.hbs",
        secondary_path = "./templates/scoreboard.hbs";
    $.get(path)
      .done(function(data) {
        loadTemplates_(data, scoreFetch_);
      })
      .fail(function() {
        // This should never happen. Why I'm doing it, I don't know.
        console.log("Initial path failed. Trying secondary path");

        $.get(secondary_path)
          .done(function(data) {
            loadTemplates_(data, scoreFetch_);
          });
      });
  }

  /**
   * Embed the game scores into the page.
   *
   * The game favorite and underdog are determined first. Once that is
   * resolved, the game data is formatted for the jsRender template to
   * consume properly.
   *
   * Once the scores are embedded, each game score has its details
   * drawer enabled. The details drawer contains all the spread-specific
   * data, such as the line, total score, margin, etc.
   *
   * @param {array} score The unmodified array of game scores received
   *     from the server.
   */
  function deployScoreboard_(score) {
    var current = {},
        favorite = '',
        gameStatus = '',
        scoreboard = {'scores': []},
        spreadLine = 0.0;

    for(var i = score.length - 1; i >= 0; i -= 1) {
      current = score[i];
      gameStatus = '';

      // Figure which team is the game favorite 
      spreadLine = current[GAME_LINE];
      if(spreadLine < 0)
        favorite = current[HOME_NAME];
      else {
        favorite = current[AWAY_NAME];
        spreadLine *= -1;   // Flip so odds are always negative
      }

      // Omit all Pregame game status
      if(current[GAME_STATUS] !== 'Pregame')
        gameStatus = current[GAME_STATUS];

      scoreboard['scores'].push({
        'awayTeam': {
          'name': current[AWAY_NAME],
          'score': current[AWAY_SCORE]
        },
        'favoriteShort': favorite,
        'favoriteLong': favorite,
        'gameClock': current[GAME_CLOCK],
        'gameId': current[GAME_ID],
        'gameStatus': gameStatus,
        'gameStartDay': current[GAME_START_DAY],
        'gameStartTime': current[GAME_START_TIME],
        'homeTeam': {
          'name': current[HOME_NAME],
          'score': current[HOME_SCORE]
        },
        'line': spreadLine,
        'margin': current[GAME_MARGIN],
        'pickedTeam': '--',
        'totalScore': (current[GAME_MARGIN]) ? '--' : 0
      });
    }

    // sort the scoreboard by earliest to latest game
    scoreboard.scores.sort(function(first, second) {
        if ( first.gameId && second.gameId ) {
            return first.gameId - second.gameId;
        }
    });

    // Render the scoreboard
    $('#scoreboard').empty().html(
      templates_['tmpl-scorebox'](scoreboard)
    );


    // Enable expansion of spread details
    $('ul#expandSpreadDetails').click(scoreboardDrawer_);
  }

  function loadTemplates_(template_data, opt_callback) {
    var partialName = '',
        partials = $(template_data).filter('script[data-part]'),
        templateName = '',
        templates = $(template_data).filter('script[data-tmpl]');

    for(var i = 0; i < templates.length; i++) {
      templateName = $(templates[i]).attr('id');
      templates_[templateName] = Handlebars.compile(templates[i].innerHTML);
    }
    
    templates = $('script[data-tmpl]');
    for(var i = 0; i < templates.length; i++) {
      templateName = $(templates[i]).attr('id');
      templates_[templateName] = Handlebars.compile(templates[i].innerHTML);
    }

    for(var i = 0; i < partials.length; i++) {
      partialName = $(partials[i]).attr('id');
      Handlebars.registerPartial(partialName, partials[i].innerHTML);
    }

    if(opt_callback)
      opt_callback();
  }

  /**
   * Controls for the scoreboards' details drawer.
   *
   * The height is the determinent on whether the action is to close
   * or open. For closing the drawer, the height is simply zero'd out
   * and hidden.
   *
   * For opening, the  actual height of the details drawer is calculated
   * while it's hidden. Once this is figured out, we reset the drawer so
   * it's in the correct position. Then we unhide the drawer, and expand
   * it to its full height.
   */
  function scoreboardDrawer_() {
    var element = $(this).parent().siblings('#spreadDetails'),
        height = element.height(),
        newHeight = 0,
        offset = element.outerHeight();

    // Toggle open/close action based on initial height
    if(height > 1) {    // Close drawer
      element.css({
        'height': '0px',
        'visibility': 'hidden'
      });
    } else {    // Open drawer
      // Calculate the height of the actual element behind the scenes
      element.css({
        'height': 'auto',
        'position': 'absolute'
      });
      newHeight = element.height();
      
      // Reset the element
      element.css({
        'height': '0px',
        'position': 'static'
      });
      // Increase the height
      element.css({
        'height': newHeight + offset + 'px',
        'visibility': 'visible'
      });
    }
  }

  function scoreFetch_() {
    $.get(SCORE_URL)
      .done(function(scoreData) {
        scores_ = scoreData;
        deployScoreboard_(scoreData);
      });      
  }

  return {
    'getScores': getScores,
    'init': init,
    'scoreboardDrawer': function() {$('ul#expandSpreadDetails').click(scoreboardDrawer_);}
  }
})(jQuery);
