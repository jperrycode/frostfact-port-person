document.addEventListener('DOMContentLoaded', function() {
  var form = document.querySelector('form');
  var saveButton = document.querySelector('.submit-row input[type="submit"]');

  saveButton.addEventListener('click', function() {
    // Create the spinner overlay
    var spinnerOverlay = document.createElement('div');
    spinnerOverlay.classList.add('spinner-overlay');

    // Create the spinner
    var spinner = document.createElement('div');
    spinner.classList.add('spinner');

    // Append spinner to overlay
    spinnerOverlay.appendChild(spinner);

    // Append the overlay to the body
    document.body.appendChild(spinnerOverlay);

    // Show the spinner
    spinnerOverlay.style.display = 'flex';
  });
});
