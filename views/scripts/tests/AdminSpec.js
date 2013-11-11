describe('Player', function() {
    it('should be ok', function() {
        var scores = admin.getScores();
        expect( scores.length ).not.toBe(0);

    });
});
