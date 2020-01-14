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
  accessToken: "pk.eyJ1Ijoia2lkaXN0eW9oIiwiYSI6ImNrM3oyd2M4azFraWwzaHQ2bW5mN2hkOTMifQ.Pw9bBZDXWP0Z7XOme4dMog"
}).addTo(map);

//Get csv data
d3.csv("getIncomeCSV", function(data){
    console.log(data);
});

//Create a layergroup 
const layerGroup = L.layerGroup().addTo(map);
//Iterate through data and display info on map
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
    $("#summariesTable").find('tbody tr').empty();

    Object.keys(data).forEach(dataKey => {
        if (dataKey === 'averagesaleyear' || dataKey === 'city') {
            return;
        }

        $("#summariesTable").find('tbody tr')
            .append($('<td>')
                .append($('<span>')
                    .text(data[dataKey][0])
                )
            );
    });
}
        

//get and render sales data 
function getAndRenderSales(selectedCity, selectedYear) {
    $.get(`/sales/${selectedCity}/${selectedYear}`, function (data, status) {
        console.log("Data: ", data, "\nStatus: ", status);
        renderSalesData(data);
    });
}
//Get and render summaries data
function getAndRenderSummaries(selectedCity, selectedYear) {
    $.get(`/summary/${selectedCity}/${selectedYear}`, function (data, status) {
        console.log("Data: ", data, "\nStatus: ", status);
        renderSummariesData(data);
    });
}


//Put Sanfrancisco and 2010 as default on load
$(function () {
    console.log( "Document is ready" );
    window.currentlySelectedCity = 'sanfrancisco';
    window.currentlySelectedYear = '2010';

    getAndRenderSales(window.currentlySelectedCity, window.currentlySelectedYear);
    getAndRenderSummaries(window.currentlySelectedCity, window.currentlySelectedYear);

//Change the data to the seelcted city from dropdown
    $("#selDataset").change(function () {
        window.currentlySelectedCity = this.value;
        console.log('City value changed to: ' + window.currentlySelectedCity);

        getAndRenderSales(window.currentlySelectedCity, window.currentlySelectedYear);
        getAndRenderSummaries(window.currentlySelectedCity, window.currentlySelectedYear);

        if( window.currentlySelectedCity == "sanfrancisco" ){ map.setView([37.7749, -122.4194], map.zoom); }
        else if( window.currentlySelectedCity == "newyork" ) { map.setView([40.7128, -74.0060], map.zoom); }
        else if( window.currentlySelectedCity == "chicago" ) { map.setView([41.8781, -87.6298], map.zoom); }
        else if( window.currentlySelectedCity == "denver" ) { map.setView([39.7392, -104.9903], map.zoom); }
        else if( window.currentlySelectedCity == "austin" ) { map.setView([30.2672, -97.7431], map.zoom); }
  

        
    });
//Change the data to the selected year when slider is moved
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
