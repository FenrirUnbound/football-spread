var helper = helper || {};

$(document).ready(function() {
    $('#pushUp').click(helper.push);
});

helper = (function($) {
    var AWAY_NAME = 'away_name',
        AWAY_SCORE = 'away_score',
        GAME_ID = 'game_id',
        HOME_NAME = 'home_name',
        HOME_SCORE = 'home_score',
        SPREAD_MARGIN = 'spread_margin',
        SPREAD_ODDS = 'spread_odds',
        SPREAD_URI = 'http://matsumoto26sunday.appspot.com/spreads';

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
        "JAC": "JACKSONVILLE",
        "KC": "KANSAS CITY",
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
        "STL": "ST. LOUIS",
        "TB": "TAMPA BAY",
        "TEN": "TENNESSEE",
        "WAS": "WASHINGTON"
    };

    var batch_;

    function parseAll() {
        var text = $('#spreadData').val().trim().split(/\n/),
            lines = [],
            width = 0,
            lineCount = 0,
            spreadData = {},
            order = [];

        text.forEach(function(line) {
          lines.push(line.split(/\s/));
        })

        width = lines[0].length;

        for (lineCount = 0; lineCount < lines.length; lineCount++) {
            switch(lineCount) {
            case 0:
                //Owners
                lines[lineCount].forEach(function (owner) {
                    order.push(owner);
                    spreadData[owner] = [];
                });
                break;
            case 1:
            case 2:
            case 3:
                // Miscellaneous data to ignore
                break;
            default:
                if (lines[lineCount][0] !== '') {
                    lines[lineCount].forEach(function (item, index) {
                        spreadData[order[index]].push(item);
                    });
                }

                break;
            }
        }

        return spreadData;
    }

    function groupUp(spreadData) {
        var keys = Object.keys(spreadData),
            dataSet = [],
            result = {},
            i = 0;

        keys.forEach(function (key) {
            dataSet = spreadData[key];
            result[key] = [];
            console.log(dataSet);

            for (i = 0; i < dataSet.length - 2; i++) {
                // Check if spread_margin is given
                if (!isNaN(dataSet[i+2])) {
                    result[key].push([
                        dataSet[i],
                        dataSet[i+1],
                        dataSet[i+2]
                    ]);

                    i += 2;
                } else {
                    result[key].push([dataSet[i]]);
                }
            }

        });

        return result;
    }

    function run() {
        var startIndex = $('#gameId').val(),
            year = $('#year').val(),
            week = parseInt($('#week').val()),
            data = groupUp(parseAll());
            result = [],
            id = 0,
            keys = Object.keys(data),
            aggregate = {};

        keys.forEach(function (key) {
            id = parseInt(startIndex)
            aggregate = {
                "year": year,
                "week": week+200,
                "owner": key
            };

            data[key].forEach(function (spread) {
                aggregate[id] = spread;
                id += 1;
            });

            result.push(aggregate);
        });

        setBatch(result);
        return result;
    }

    function setBatch(value) {
        batch_ = value;
    }

    function getBatch() {
        return batch_;
    }

    function push() {
        var data = run();

        data.forEach(function (spreadData) {
            $.post(SPREAD_URI, spreadData);
        });
    }


    return {
        "run": run,
        "push": push,
        "batch": getBatch
    };
})(jQuery);