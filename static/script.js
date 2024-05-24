document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('artistForm').addEventListener('submit', function(event) {
        event.preventDefault();
        var artistName = document.getElementById('artist_name').value;

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/get_recommendations', true);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                if (data.error) {
                    document.getElementById('recommendations').innerHTML = 'アーティストが見つかりません。';
                } else {
                    displayRecommendations(data);
                }
            }
        };
        xhr.send(JSON.stringify({ artist_name: artistName }));
    });
});

function displayRecommendations(data) {
    var recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = ''; // Clear previous results

    var topArtistsList = data.top_artists_list;
    var topTracksDict = data.top_tracks_dict;

    topArtistsList.forEach(function(artist) {
        var artistElement = document.createElement('div');
        artistElement.innerHTML = '<h2>' + artist + '</h2>';

        var tracks = topTracksDict[artist];
        var tracksList = document.createElement('ul');
        tracks.forEach(function(track) {
            var trackElement = document.createElement('li');
            trackElement.innerHTML = track.name + ' (' + track.release_date + ')<br>';
            if (track.image_url) {
                trackElement.innerHTML += '<img src="' + track.image_url + '" alt="' + track.name + 'のアルバムアート" width="100" height="100"><br>';
            }
            tracksList.appendChild(trackElement);
        });

        artistElement.appendChild(tracksList);
        recommendationsDiv.appendChild(artistElement);
    });
}
