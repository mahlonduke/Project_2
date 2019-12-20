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
  accessToken: API_KEY 
}).addTo(map);



//json files
var file = "../Samples/sample_response_san_francisco.json";
var file2 = "../Samples/sample_response_denver.json"

// //         d3.select('#selDataset')
//   .on('onchange', function() {
//     var sfdata = (d3.select(this).property('value'));
//     var nydata = (d3.select(this).property('value'));
//     var chicdata = (d3.select(this).property('value'));
//     var dendata = (d3.select(this).property('value'));
//     var ausdata = (d3.select(this).property('value'));
//     updateLegend();
// });

// var overlays = {
//   "sanfrancisco": sfdata.sanfrancisco,
//   "newyork": nydata.newyork,
//   "chicago": chicdata.chicago,
//   "denver": dendata.denver,
//   "austin": ausdata.austin
// };

// var cities = map.map_type === "metro" ? "circle" : "circle, path";
//     $(color_item, map).each(function(index, element) {
//         var city_value = $(this).attr("optionChanged") || $(this).attr("value");
//         city_value = Number(city_value);

//         var cityinfo = "";
//         if (isNaN(city_value)) {
//             cityinfo = ([yearbuild,priceperbeds]); 
//         } else if (city_value = sfdata) {
//             cityinfo = colors[0];
//         } else if (city_value = nydata) {
//             cityinfo = colors[1];
//         } else if (city_value = chicdata) {
//             cityinfo = colors[2];
//         } else if (city_value = dendata ) {
//             cityinfo = colors[3];
//         } else if (city_value = ausdata ) {
//             cityinfo = colors[3];
//         } else {
//             stateColor = colors[4];
//         }

// //Grab a reference to the dropdown select element
// var selector = d3.select("#selDataset");

// // Use the list of sample names to populate the select options
// d3.json("/selection").then((sampleNames) => {
//   sampleNames.forEach((sample) => {
//     selector
//       .append("option")
//       .text(sample)
//       .property("value", sample);
//   });


//   var selector = d3.select("#selDataset");
//   selector.on('onchange', function() {
//       var newData = eval(d3.select(this).property('selection'));
//        updateLegend(newData);
//   });

//Denver
d3.json(file2).then(function(d2)  {
  // console.log(d2.property[0].location.latitude);
  // var x = [data.property[0].location.latitude, data.property[0].location.longitude]
  var latlonArray = [];
  for (var i = 0; i < d2.property.length; i++) {
      var lat = d2.property[i].location.latitude;
      var lon = d2.property[i].location.longitude;
      var yearbuild2 = d2.property[i].summary.yearbuilt;
      var priceperbeds2 = d2.property[i].sale.calculation.priceperbed;
      
      console.log(lat);
      console.log(lon);
      var data2 = {lat, lon};

      L.marker([lat,lon]).addTo(map);

        var popup2 = L.popup()
    .setLatLng(data2)
    .setContent('<p>Year Built :</p>'+ yearbuild2 + '<p>Price per bed :</p>' + "$"+priceperbeds2)
    .openOn(map);
        }

});

d3.json(file).then(function(d1)  {
    // console.log(data.property[0].location.latitude);
    // var x = [data.property[0].location.latitude, data.property[0].location.longitude]
    var latlonArray = [];
  for (var i = 0; i < d1.property.length; i++) {
      var lat = d1.property[i].location.latitude;
      var lon = d1.property[i].location.longitude;
      var yearbuild = d1.property[i].summary.yearbuilt;
      var priceperbeds = d1.property[i].sale.calculation.priceperbed;
      
      console.log(lat);
      console.log(lon);
      var data1 = {lat, lon};

      L.marker([lat,lon]).addTo(map);

        var popup = L.popup()
    .setLatLng(data1)
    .setContent('<p>Year Built :</p>'+ yearbuild + '<p>Price per bed :</p>' + "$"+priceperbeds)
    .openOn(map);
        }});
        
      
 //slider function
 var slider = document.getElementById("myRange");
      var output = document.getElementById("value");
      output.innerHTML = slider.value;
      slider.oninput = function() {
      output.innerHTML = this.value;
        }    


       





