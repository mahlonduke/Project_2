// Creating map object
var map = L.map("map", {
  center: [37.68277135535169,-122.31767190046192],
  zoom: 4
});
//create map tile
L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
  attribution: "Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
  maxZoom: 18,
  id: "mapbox.streets",
  accessToken: "pk.eyJ1IjoibWFobG9uZHVrZSIsImEiOiJjazN2dHB4b2UwZmZ3M2RtZmR5cGY5d3N3In0.q7Tmog7LGaQCv8Ohts6Cdw"
}).addTo(map);

const layerGroup = L.layerGroup().addTo(map);

function renderSalesData(data) {
    // clear all markers currently on the app before adding the new ones
    layerGroup.clearLayers();

    for (var i = 0; i < data.city.length; i++) {
        var lat = data.latitude[i];
        var lon = data.longitude[i];
        var yearbuild2 = data.yearbuilt[i];
        const salepriceElement = data.saleprice[i];
        var priceperbeds2 = salepriceElement === 0 ? 0 : salepriceElement/data.bedrooms[i];

        console.log(lat);
        console.log(lon);
        var data2 = {lat, lon};

        const informationAboutProperty = '<p>Year Built :</p>'+ yearbuild2 + '<p>Price per bed :</p>' + "$"+priceperbeds2;
        const marker = L.marker([lat,lon]);
        marker.bindPopup(informationAboutProperty).openPopup();
        marker.addTo(layerGroup);

        var popup2 = L.popup()
            .setLatLng(data2)
            .setContent(informationAboutProperty)
            .openOn(layerGroup);
    }
}

function renderSummariesData(data) {
    // implement render of summaries data
    // clear all markers currently on the app before adding the new ones
//     layerGroup.clearLayers();

//     for (var i = 0; i < data.city.length; i++) {
//         var totalproperties = data.totalproperties[i];
//         var priceperbed = data.priceperbed[i];
//         var priceperbath = data.priceperbath[i];
//         var averagebeds = data.averagebeds[i];
//         var averagebaths = data.averagebaths[i];
        

//         console.log(totalproperties);
  
 }

function getAndRenderSales(selectedCity, selectedYear) {
    $.get(`/sales/${selectedCity}/${selectedYear}`, function (data, status) {
        console.log("Data: ", data, "\nStatus: ", status);
        renderSalesData(data);
    });
}

function getAndRenderSummaries(selectedCity, selectedYear) {
    $.get(`/summary/${selectedCity}/${selectedYear}`, function (data, status) {
        console.log("Data: ", data, "\nStatus: ", status);
        renderSummariesData(data);
    });
}

$(function () {
    console.log( "Document is ready" );
    window.currentlySelectedCity = 'sanfrancisco';
    window.currentlySelectedYear = '2010';

    getAndRenderSales(window.currentlySelectedCity, window.currentlySelectedYear);

    $("#selDataset").change(function () {
        window.currentlySelectedCity = this.value;
        console.log('City value changed to: ' + window.currentlySelectedCity);

        getAndRenderSales(window.currentlySelectedCity, window.currentlySelectedYear);
        getAndRenderSummaries(window.currentlySelectedCity, window.currentlySelectedYear);
    });

    $(document).on('input', '#myRange', function() {
        window.currentlySelectedYear = $(this).val();
        console.log('Year value changed to:', window.currentlySelectedYear);

        getAndRenderSales(window.currentlySelectedCity, window.currentlySelectedYear);
        getAndRenderSummaries(window.currentlySelectedCity, window.currentlySelectedYear);
    });
});

 //slider function
var slider = document.getElementById("myRange");
var output = document.getElementById("value");
output.innerHTML = slider.value;
slider.oninput = function () {
    output.innerHTML = this.value;
};
