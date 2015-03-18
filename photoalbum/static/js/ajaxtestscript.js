function submitImage() {
  $('#add_image_errors').text("");
  var post_data = $("#image_form").serialize();
  $.post("/add_image", post_data, loadImage);
  }
  
function loadImage(response) {
  if(response.result == 'ok'){
    $new_image = $('<img>', {class: "user_image", id: response.image_id, src: response.image_url, draggable: "true", height: 100, width: 100, alt: 'Image not found'});
    $new_button = $('<input>', {type: "button", class: "delete_button", id: response.image_url, value: "Delete"});
    $('#images').append($new_image);
    $('#images').append($new_button);
    $new_image.on('dragstart', false, handleDragStart);
    $new_button.click(deleteImage);
  }
  else if(response.result == 'duplicate'){
    $('#add_image_errors').text("That image already exists");
    }
  $('#image_url').val("");
}

function deleteImage() {
  console.log("delete");
  console.log(this.id);
}

function handleDragStart(e) {
  console.log(this.src + " is being dragged");
  e.dataTransfer = e.originalEvent.dataTransfer;
  e.dataTransfer.effectAllowed = 'copy';
  e.dataTransfer.setData('id', this.id);
}

function handleDragOver(e) {
  e.preventDefault();
}

function handleDrop(e) {
   console.log("drop");
   e.preventDefault();
   e.dataTransfer = e.originalEvent.dataTransfer;
   var image_id = e.dataTransfer.getData('id');
   console.log(document.getElementById(image_id));
   // $dropped_image = $('#' + image_id);
   e.target.appendChild(document.getElementById(image_id).cloneNode(true));
   // $(this).append($dropped_image);
   // this.innerHTML = document.getElementById(image_id).cloneNode(true);
   return false;
}

function main() {
  $('#image_url').val("");
  $("#image_button").click(submitImage);
  $("#drop_area").on('dragover', false, handleDragOver);
  $("#drop_area").on('drop', false, handleDrop);
  $("#drop_area2").on('dragover', false, handleDragOver);
  $("#drop_area2").on('drop', false, handleDrop);
}
 
window.onload = main;

