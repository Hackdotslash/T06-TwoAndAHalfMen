function initMap() {

    navigator.geolocation.getCurrentPosition(async (pos) => {
        let latitude = pos.coords.latitude
        let longitude = pos.coords.longitude
        document.getElementById("latInput").value = latitude
        document.getElementById("lngInput").value = longitude

        var map = new google.maps.Map(document.getElementById('map'), {
            center: { lat: latitude, lng: longitude },
            scrollwheel: false,
            zoom: 15
        });

        var myLatlng = new google.maps.LatLng(latitude, longitude);

        // Place a draggable marker on the map
        var marker = new google.maps.Marker({
            position: myLatlng,
            map: map,
            draggable:true,
            title:"Drag me!"
        });
    
        //get marker position and store in hidden input
        google.maps.event.addListener(marker, 'dragend', function (evt) {
            document.getElementById("latInput").value = evt.latLng.lat().toFixed(3);
            document.getElementById("lngInput").value = evt.latLng.lng().toFixed(3);
        });
    
    })

}

function submitLocation() {
    const form = document.getElementsByName("docRegLocation")[0]
    console.log(form)
    console.log(form["id"].value)
    console.log(form["lat"].value)
    console.log(form["lng"].value)
    form.submit()
}