$(document).ready(function() {
    $('.game-selector').select2();
    $('.user-selector').select2();
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
        $('#list-games').append("<tr><td>" + allGames[i][0] + "</td><td>" + allGames[i][2] + "</td></tr>");
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
        recommendationData = JSON.parse(data);
        console.log(recommendationData)
        $('#list-recommendations-list').empty();
        for (var i = 0; i < recommendationData.length; i++) {
            console.log(recommendationData[i])
            $('#list-recommendations-list').append("<tr><td>" + recommendationData[i][0] + "</td><td>" + recommendationData[i][1] + "</td></tr>");
        }
        console.log(allGames)
    });
}

function getRecommendationUser() {
    jsonData = new Array();
    userData = new Object();
    userData.name = $('#user-selector option:selected').text();
    jsonData.push(userData);

    $.post("/get-recommendation-user", JSON.stringify(jsonData), function( data ) {
        // console.log(data);
        recommendationData = JSON.parse(data)[0];
        usersGames = JSON.parse(data)[1];
        // console.log(recommendationData)
        $('#list-recommendations-list').empty();
        for (var i = 0; i < recommendationData.length; i++) {
            // console.log(recommendationData[i])
            $('#list-recommendations-list').append("<tr><td>" + recommendationData[i][0] + "</td><td>" + recommendationData[i][1] + "</td></tr>");
        }

        $('#list-games').empty();
        for (var i = 0; i < usersGames.length; i++) {
            $('#list-games').append("<tr><td>" + usersGames[i][0] + "</td><td>" + usersGames[i][1] + "</td></tr>");
        }
        // console.log(allGames)
    });
}