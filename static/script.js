$(document).ready(function() {
    $('.game-selector').select2();
});

var allGames = [];

function addGame() {
    gameId = $('#game-selector').val();
    gameName = $('#game-selector option:selected').text();
    gameRating = $('#rating-selector').val();

    var alreadyIn = false;

    for(var i = 0; i < allGames.length; ++i) {
        if (allGames[i][1] == gameId) {
            alreadyIn = true;
            allGames[i] = [gameName, gameId, gameRating];
        }
    }

    if (!alreadyIn) {
        allGames.push([gameName, gameId, gameRating]);
    }

    $('#list-games').empty();
    for (var i = 0; i < allGames.length; ++i) {
        $('#list-games').append("<div>" + allGames[i][0] + ": " + allGames[i][2] + "</div>");
    }
    
}

function getRecommendation() {

    jsonData = new Array();
    for (var i = 0; i < allGames.length; ++i) {
        gameData = new Object();
        gameData.name = allGames[i][0];
        gameData.id = allGames[i][1];
        gameData.rating = allGames[i][2];
        jsonData.push(gameData);
    }

    $.post("/get-recommendation", JSON.stringify(jsonData), function( data ) {
        console.log(data);
    });
}