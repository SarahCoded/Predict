document.addEventListener('DOMContentLoaded', () => {

// Change the colour of the table depending on how badly the prediction went

let points = document.querySelectorAll('.points');
let colorChange = document.querySelectorAll('.tablerow');

for (j = 0; j < points.length; j++) (function(j) {
if (points[j].innerHTML == 0) {
    colorChange[j].style.backgroundColor = 'green';
    colorChange[j].style.color = 'white';
}
else if (points[j].innerHTML <= 3) {
    colorChange[j].style.backgroundColor = 'yellow';
}
else if (points[j].innerHTML <= 5) {
    colorChange[j].style.backgroundColor = 'orange';
}
else if (points[j].innerHTML >= 6) {
    colorChange[j].style.backgroundColor = 'red';
}
})(j);

// Generate a random key to create a league
let generator = document.getElementsByClassName('keygenerator');
let generatorfield = document.getElementsByClassName('randomkey');

// When user clicks on the button, populate input with a random string
for (k = 0; k < generator.length; k++) (function(k) {
    generator[k].onclick = () => {
    // Use math function to generate a string of 6
    let randomstring = Math.random().toString(36).substr(2, 6);
    // Put the random string in the value field
    generatorfield[k].value = randomstring;
}
})(k);

})