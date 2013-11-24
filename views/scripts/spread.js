var spread = spread || {};

spread = (function ($, scores_) {
    var AWAY_NAME = "away_name",
        AWAY_SCORE = "away_score",
        GAME_CLOCK = "game_clock",
        GAME_ID = 'game_id',
        GAME_LINE = "spread_odds",
        GAME_MARGIN = "spread_margin",
        GAME_START_DAY = "game_day",
        GAME_START_TIME = "game_time",
        GAME_STATUS = "game_status",
        HOME_NAME = "home_name",
        HOME_SCORE = "home_score",
        SPREAD_URL = 'http://matsumoto26sunday.appspot.com/spreads';

    var spread_ = {},
        templates_ = {};

    function init() {
        var path = "./scripts/templates/scoreboard.hbs";
        $.get(path)
            .done(function(data) {
                loadTemplates_(data, fetchSpread_);
            })
            .fail(function() {
                // This should never happen. Why I'm doing it, I don't know.
                console.log("Initial path failed. Trying secondary path");
            });
    }

    function loadTemplates_(template_data, opt_callback) {
        var templateName = '',
            templates = $('script[data-tmpl]'),
            externalTemplates = $(template_data).filter('script[data-tmpl]');

            for(var i = 0; i < templates.length; i++) {
                templateName = $(templates[i]).attr('id');
                templates_[templateName] = Handlebars.compile(templates[i].innerHTML);
            }

            for(var i = 0; i < externalTemplates.length; i++) {
                templateName = $(externalTemplates[i]).attr('id');
                templates_[templateName] = Handlebars.compile(externalTemplates[i].innerHTML);
            }

        if(opt_callback)
            opt_callback();
    }

    function fetchSpread_() {
        $.get(SPREAD_URL)
            .done(function (data) {
                spread_ = data;
                deploySpread_(spread_);

                // Enable the spread-select button
                $('#selectButton').click(redeploy_);
            });
    }

    function deploySpread_(spreadData) {
        var list = [],
            data = { "players": [] },
            contents = {},
            playersLength = spreadData.length,
            result = '',
            names = [];

        for (var i = 0; i < playersLength; i++) {
            contents[spreadData[i]['owner']] = true;
        }

        names = Object.keys(contents);
        for (var j = 0; j < names.length; j++) {
            data.players.push({
                "name": names[j],
                "value": j
            });
        }

        data.players.sort(function(a,b) {
            if (a.name < b.name) {
                return -1;
            } else if (a.name > b.name) {
                return 1;
            } else {
                return 0;
            }
        });

        result = templates_['tmpl-listoptions'](data);
        $('#selectMenu').html(result);
    }

    function redeploy_() {
        var current = {},
            favorite = '',
            gameStatus = '',
            scoreboard = {'scores': []},
            spreadLine = 0.0,
            chosenOne = $('#selectMenu').find('option:selected').text(),
            spread = {},
            gameData = [],
            gameId = 0,
            scoreDiff = 0,
            isWinning = false,
            pickedTeam = '',
            totalScore = 0,
            tally = 0,
            score = scores_.getScores();


        for (var i = 0; i < spread_.length; i++) {
            if (spread_[i]['owner'] === chosenOne) {
              spread = spread_[i];
              break;
            }
        }


        for(var i = score.length - 1; i >= 0; i -= 1) {
            current = score[i];
            gameStatus = '';
            isWinning = false;
            pickedTeam = '';
            totalScore = 0;

            // Figure which team is the game favorite 
            spreadLine = current[GAME_LINE];
            if(spreadLine < 0) {
                favorite = current[HOME_NAME];
                scoreDiff = current[HOME_SCORE] - current[AWAY_SCORE] + spreadLine;
            }
            else {
                favorite = current[AWAY_NAME]; 
                spreadLine *= -1;   // Flip so odds are always negative
                scoreDiff = current[AWAY_SCORE] - current[HOME_SCORE] + spreadLine ;
            }

            favorite = (favorite === 'ARI') ? 'AZ' : favorite;

            // Omit all Pregame game status
            if(current[GAME_STATUS] !== 'Pregame')
                gameStatus = current[GAME_STATUS];

            //Check if chosen as winner
            gameId = current[GAME_ID];
            gameData = spread[gameId];
            if (gameData && gameData.length > 0) {
                pickedTeam = gameData[0];
            }
            if (gameData && gameStatus) {
                // Lazy. Only check if the first letter matches.
                // Problems with games where both teams start with the same letter
                if (gameData[0] === favorite) {
                    //Winning if the favorite is winning after handicap
                    isWinning = scoreDiff > 0;
                } else {
                    // Winning if the favorite is tied or losing
                    isWinning = scoreDiff <= 0;
                }

                // Winning spread
                if (isWinning) {
                    tally += 1;
                }

                // Over/Under
                if (gameData.length > 1) {
                    if (gameData[1][0] === 'O' && current[HOME_SCORE] + current[AWAY_SCORE] > current[GAME_MARGIN]) {
                        tally += 1;
                    } else if (gameData[1][0] === 'U' && current[HOME_SCORE] + current[AWAY_SCORE] < current[GAME_MARGIN]) {
                        tally += 1;
                    }
                }

                if (gameData.length === 3) {
                    totalScore = gameData[2];

                    if (totalScore === current[HOME_SCORE] + current[AWAY_SCORE]) {
                        tally += 1;
                    }
                    if (totalScore >= current[HOME_SCORE] + current[AWAY_SCORE] - 3) {
                        if (totalScore <= current[HOME_SCORE] + current[AWAY_SCORE] + 3) {
                            tally += 1;
                        }
                    }
                }
            }

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
                'pickedTeam': pickedTeam || '--',
                'totalScore': (current[GAME_MARGIN]) ? (current[HOME_SCORE] + current[AWAY_SCORE]) + ((totalScore) ? ' (' + (totalScore)+ ')' : '') : 0,
                'isWinning': (gameStatus && gameData && isWinning),
                'isLosing': (gameStatus && gameData && !isWinning),
                'isOver': (gameStatus && gameData && gameData.length > 1 && gameData[1][0] === 'O'),
                'isUnder': (gameStatus && gameData && gameData.length > 1 && gameData[1][0] === 'U'),
                'actualOver': (gameStatus && current[HOME_SCORE] + current[AWAY_SCORE] > current[GAME_MARGIN]),
                'actualUnder': (gameStatus && current[GAME_MARGIN] > current[HOME_SCORE] + current[AWAY_SCORE]),
                'totalGood': (gameStatus && totalScore && (totalScore >= current[HOME_SCORE]+current[AWAY_SCORE]-3 && totalScore <= current[HOME_SCORE]+current[AWAY_SCORE]+3)),
                'totalBad': (gameStatus && totalScore && (totalScore < current[HOME_SCORE]+current[AWAY_SCORE]-3 || totalScore > current[HOME_SCORE]+current[AWAY_SCORE]+3))
              });
        }

        scoreboard.scores.sort(function(a,b) {
            if (a.gameId && b.gameId) {
                return (a.gameId - b.gameId);
            }

            return 0;
        })

        // Render the scoreboard
        $('#scoreboard').empty().html(
            templates_['tmpl-scorebox'](scoreboard)
            );
        scores_.scoreboardDrawer();
        $('#selectTally').text(tally);
    }

    function getSpread() {
        return spread_;
    }

    return {
        init: init,
        getSpread: getSpread,
        redeploy: redeploy_
    };
})(jQuery, scores); 
