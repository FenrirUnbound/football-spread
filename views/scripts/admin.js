var admin = admin || {};

admin = (function($) {
  var AWAY_NAME = 'away_name',
      AWAY_SCORE = 'away_score',
      GAME_ID = 'game_id',
      HOME_NAME = 'home_name',
      HOME_SCORE = 'home_score',
      SCORES_URI = 'http://matsumoto26sunday.appspot.com/scores', 
      SPREAD_MARGIN = 'spread_margin',
      SPREAD_ODDS = 'spread_odds',
      TEMPLATES_URI_VIEW = './scripts/templates/view_odds.hbs',
      TEMPLATES_URI_EDIT = './scripts/templates/edit_odds.hbs';

  /*** Constants ***/
  var TEAM_NAMES = {
    "ARI": "ARIZONA",
    "ATL": "ATLANTA",
    "BAL": "BALTIMORE",
    "BUF": "BUFFALO",
    "CAR": "CAROLINA",
    "CHI": "CHICAGO",
    "CIN": "CINCINNATI",
    "CLE": "CLEVELAND",
    "DAL": "DALLAS",
    "DEN": "DENVER",
    "DET": "DETROIT",
    "GB": "GREEN BAY",
    "HOU": "HOUSTON",
    "IND": "INDIANAPOLIS",
    "JAX": "JACKSONVILLE",
    "KC": "KANSAS CITY",
    "LA": "LOS ANGELES",
    "MIA": "MIAMI",
    "MIN": "MINNESOTA",
    "NE": "NEW ENGLAND",
    "NO": "NEW ORLEANS",
    "NYG": "NY GIANTS",
    "NYJ": "NY JETS",
    "OAK": "OAKLAND",
    "PHI": "PHILADELPHIA",
    "PIT": "PITTSBURGH",
    "SD": "SAN DIEGO",
    "SF": "SAN FRANCISCO",
    "SEA": "SEATTLE",
    "TB": "TAMPA BAY",
    "TEN": "TENNESSEE",
    "WAS": "WASHINGTON"
  };

  var scores_ = {},
      templates_ = {},
      week = 0;

  function getScores() {
    return scores_;
  }

  function init() {
    $.get(TEMPLATES_URI_VIEW)
      .done(function(template_data) {
        loadTemplates_(template_data);
      });

    $.get(TEMPLATES_URI_EDIT)
      .done(function(template_data) {
        loadTemplates_(template_data);
      });

    $('#oddsHeader_update').click(scoreFetch_);
  }


  function updateScore() {
    var away_score = $('#editScores-scoreAway').val() || 0,
        data = {},
        game_id = $('#editScores-gameId').val() || 0,
        home_name = favorite =  scores_[game_id]['homeTeam'],
        away_name = scores_[game_id]['awayTeam'],
        home_score = $('#editScores-scoreHome').val() || 0,
        spread_margin = $('#editScores-over-under').val() || 0.0,
        spread_odds = $('#editScores-line').val() || 0.0;

    if( game_id <= 0 ) {
      return false;
    }

    data = {
      away_name: away_name,
      away_score: away_score,
      game_id: game_id,
      home_name: home_name,
      home_score: home_score,
      spread_odds: spread_odds,
      spread_margin: spread_margin
    };

    // Modify the odds based if home team is favorited
    if($('input:radio[name=editScores-favorite]:checked').val() === 'Away') {
      data['spread_odds'] *= -1;
      favorite = away_name;
    }

    // update local scores cache
    for(var key in data) {
      scores_[game_id][key] = data[key];
    }
    //update favorites
    scores_[game_id]['favoriteShort'] = favorite;
    scores_[game_id]['favoriteLong'] = favorite;

    $.post(SCORES_URI, data)
      .done(function (data) {
        $('#editOdds').remove();
      });

    return false;
  }

  function loadScores_(scoreData) {
    var current = {},
        favorite = '',
        scoreboard = {'scores': []},
        spreadLine = 0;

    for(var i = 0; i < scoreData.length; i++) {
      current = scoreData[i];

      // Figure which team is the game favorite 
      spreadLine = current[SPREAD_ODDS];
      if(spreadLine < 0)
        favorite = current[HOME_NAME];
      else if(spreadLine > 0){
        favorite = current[AWAY_NAME];
        spreadLine *= -1;   // Flip so odds are always negative
      } else {
        // No spread data set yet
        favorite = '';
        spreadLine = 0;
      }

      scores_[current[GAME_ID]] = {
        'awayTeam': current[AWAY_NAME],
        'awayScore': current[AWAY_SCORE],
        'favoriteShort': favorite,
        'favoriteLong': favorite,
        'homeTeam': current[HOME_NAME],
        'homeScore': current[HOME_SCORE],
        'spread_odds': spreadLine,
        'spread_margin': current[SPREAD_MARGIN],
        'pickedTeam': '--',
        'totalScore': (current[SPREAD_MARGIN]) ? '--' : 0
      };

      scoreboard['scores'].push({
        'awayName': current[AWAY_NAME],
        'homeName': current[HOME_NAME],
        'favoriteName': favorite,
        'gameId': current[GAME_ID],
        'spreadOdds': spreadLine,
        'spreadMargin': current[SPREAD_MARGIN]
      });
    }

    $('#oddsScoreboard').empty().html(templates_['tmpl-oddsScoreboard'](scoreboard));

    // Add click to each update button
    $('button[id^="update_"]').click(updateGameForm_);
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
    
    for(var i = 0; i < partials.length; i++) {
      partialName = $(partials[i]).attr('id');
      Handlebars.registerPartial(partialName, partials[i].innerHTML);
    }

    // Helper function for determing equality
    Handlebars.registerHelper('ifeq', function(v1, v2, options) {
      if(v1 == v2) {
        return options.fn(this);
      }
      return options.inverse(this);
    });

    if(opt_callback)
      opt_callback();
  }

  function scoreFetch_(event) {
    event.preventDefault();

    var week;

    // Find the week to fetch
    week = $('#oddsHeader_selectWeek').find('option:selected').val();

    $.get(SCORES_URI + '?week=' + week)
      .done(function(data) {
        loadScores_(data);
      });
  }

  function updateGameForm_(event) {
    var value = $(this).val(),
        game = {},
        target;

    event.preventDefault();
    game = {
      favorite: scores_[value]['favoriteShort'],
      gameId: value,
      labels: [
        'Team',
        'Score',
        'Fav'
      ],
      teams: [
        {
          favorite: scores_[value]['awayTeam'] === scores_[value]['favoriteShort'],
          label: 'Away',
          name: scores_[value]['awayTeam'],
          score: scores_[value]['awayScore'],
          teams: Object.keys(TEAM_NAMES)
        },
        {
          favorite: scores_[value]['homeTeam'] === scores_[value]['favoriteShort'],
          label: 'Home',
          name: scores_[value]['homeTeam'],
          score: scores_[value]['homeScore'],
          teams: Object.keys(TEAM_NAMES)
        }
      ],
      odds: [
          {
            label: 'Line',
            id: 'line',
            max: -0.5,
            value: scores_[value]['spread_odds']
          },
          {
            label: 'Over/Under',
            id: 'over-under',
            min: 0.0,
            value: scores_[value]['spread_margin']
          }
      ]
    };

    target = $('#editOdds');
    if(target.length === 0) {
      $('#odds').after(templates_['tmpl-editOdds'](game));
    } else {
      target.replaceWith(templates_['tmpl-editOdds'](game));
    }
  }

  return {
    'getScores': getScores,
    'init': init,
    'updateScore': updateScore
  };
})(jQuery);