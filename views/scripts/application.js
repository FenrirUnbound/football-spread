window.Spread = Ember.Application.create();

Spread.ApplicationAdapter = DS.RESTAdapter.extend({
    buildURL: function (type, week) {
        var endpoint = (type === 'scorebox') ? 'scores' : type;

        return [this.host, endpoint].join('/');
    },
    findAll: function (store, type, sinceToken) {
        var adapter = this,
            namespace = type.typeKey,
            url = this.buildURL(type.typeKey),
            scores = [],
            result = {};

        return Ember.$.getJSON(url).then(function (response) {
            response.forEach(function (game) {
                scores.push(adapter.compileData_(game));
            });

            result[namespace] = scores;
            return result;
        });
    },
    compileData_: function (gameData) {
        var awayName = gameData.away_name,
            homeName = gameData.home_name,
            spreadOdds = gameData.spread_odds;

        return {
            id: gameData.game_id,
            awayTeam: awayName,
            awayScore: gameData.away_score,
            favorite: (spreadOdds < 0) ? homeName : awayName,  // negative spreads favor home team
            gameStatus: gameData.game_status,
            homeTeam: homeName,
            homeScore: gameData.home_score,
            pickedTeam: '---',
            spreadOdds: (spreadOdds > 0) ? spreadOdds * -1 : spreadOdds,  // spread always negative number
        };
    },
    host: 'http://matsumoto26sunday.appspot.com'
});



// Router
Spread.Router.map(function () {
    this.resource('scoreboard', { path: '/' });
});
Spread.ScoreboardRoute = Ember.Route.extend({
    model: function () {
        var result = this.store.find('scorebox');

        return result;
    }
});

// Controller
Spread.ScoreboardController = Ember.ArrayController.extend({
    totalPoints: function () {
        return 0;
    }.property(),
    actions: {
        darren: function () {
            console.log('Me');
        }
    }
});
Spread.ScoreboxController = Ember.ObjectController.extend({
    actions: {
        flipCard: function () {
            var currentState = this.get('isFlipped');
            this.set('isFlipped', !currentState);
        }
    }
});


// Model
Spread.Scorebox = DS.Model.extend({
    awayTeam: DS.attr('string'),
    awayScore: DS.attr('number'),
    favorite: DS.attr('string'),
    gameStatus: DS.attr('string'),
    homeTeam: DS.attr('string'),
    homeScore: DS.attr('number'),
    pickedTeam: DS.attr('string'),
    spreadOdds: DS.attr('number')
});

Spread.Picks = DS.Model.extend({
    owner: DS.attr('string')
});


// Views

Spread.Selection = Ember.View.extend({
    templateName: 'spreadSelection',
    totalPoints: 1
});