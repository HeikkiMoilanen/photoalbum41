/* Global variables */

var csrftoken = getCookie('csrftoken');
var layout = 1;
var current_album;
var current_page = 1;
var page_id = "right_page";
var empty_src = "http://i1093.photobucket.com/albums/i430/moiheikki/insert_pic_zps8f368144.jpg";
var empty_caption = "insert your caption here"
/* This is for error messages to disappear after a duration */
var timer;

/* This one didn't work:
var empty_src = "{% static 'images/insert_pic.jpg' %}";
This one was used in dev:
var empty_src = "/photoalbum/static/images/insert_pic.jpg";
*/

/* Gets a certain token from cookies, used for getting csrf token */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/* POSTs a new image to the server with imgage's URL in payload. */
function submitImage() {
  if ($("#image_url").val() === '') {
    $('#add_image_error').text("You didn't give a link.");
    timer = setInterval(function(){clearErrorText("image")}, 3000);
  }

  else {
  var post_data = $("#image_form").serialize();
  $.post("/add_image", post_data, loadImage);
  }
}

/* Handles the response from server to adding a new image. If adding was successful, 
   the new image is added to the image list. If not, an error is shown. */  
function loadImage(response) {
  if(response.result == 'ok'){
    $new_image = $('<img>', {id: response.image_id, src: response.image_url, class: 'new_image', draggable: 'true', ondragstart: 'handleDragStart(event)', alt: 'Image not found'});
    $('#image_list').append("<li class='list_image'>");
    $('#image_list').append($new_image);
    $('#image_list').append("</li>");
  }
  else if(response.result == 'duplicate'){
    $('#add_image_error').text("That image already exists");
    timer = setInterval(function(){clearErrorText("image")}, 3000);
    }
  $('#image_url').val("");
}

/* This is executed when user starts dragging images. event.target is the draggable image. */
function handleDragStart(event){
  event.dataTransfer.setData("src", event.target.src);
  event.dataTransfer.setData("id", event.target.id);
}

/* This is needed just to override some browser default behaviour related to to drop events. */
function handleDragOver(event){
  event.preventDefault();
}

/* This is executed when the user drops the image to the drop area. event.target is the drop area. */
function handleDrop(event){
  event.preventDefault();
  
  /* This checks which image got dragged to. This software is planned for maximum of 3 images per page*/
target_index = 1;
  if (event.target.id == "photo1") {
    target_index = 1;
  }   
  else if (event.target.id == "photo2") {
    target_index = 2;
  }
  else if (event.target.id == "photo3") {
    target_index = 3;
  }
  if (event.dataTransfer.getData("id") == "eraser") {
    var post_data = {album_id: current_album, page_number: current_page, index: target_index, 'csrfmiddlewaretoken': csrftoken};
    $.post("/delete_image_on_page", post_data, deleted_image_on_page);
  }
  else if (event.dataTransfer.getData("src") != '') {
    event.target.src = event.dataTransfer.getData("src");
    var post_data = {album_id: current_album, page_number: current_page, index: target_index, image_url: event.dataTransfer.getData("src"), caption: empty_caption, 'csrfmiddlewaretoken': csrftoken};
    $.post("/update_image_on_page", post_data, update_image_on_page);
  } 
}

function deleted_image_on_page(response) {
  viewPage(current_page);
}
function update_image_on_page(response) {
  /* The update is seen by the user so this is not needed at the moment, but left in for possible future development.*/
}

/* Sets the layout to be as given as an argument*/
function setLayout(setLayout) {

  /*[0] is required to be equal to document.getElementByID and thus use className
    The current class is fully overwritten, so if the classes there are changed at some point,
    changes have to be made here too.*/
  if (setLayout == 1) {
    $("#photobox1")[0].className = "photobox layout1";
    $("#caption1")[0].className = "textbox layout1";
    $("#photobox2")[0].className = "photobox layout1";
    $("#caption2")[0].className = "textbox layout1";
    $("#photobox3")[0].className = "photobox layout1";
    $("#caption3")[0].className = "textbox layout1";
    layout = 1;
  }

  else if (setLayout == 2) {
    $("#photobox1")[0].className = "photobox layout2";
    $("#caption1")[0].className = "textbox layout2";
    $("#photobox2")[0].className = "photobox layout2";
    $("#caption2")[0].className = "textbox layout2";
    $("#photobox3")[0].className = "photobox layout2";
    $("#caption3")[0].className = "textbox layout2";
    layout = 2;
    };
}

/* Called when user wants to save a layout */
function saveLayout() {
  var post_data = {album_id: current_album, page_number: current_page, layout: layout, 'csrfmiddlewaretoken': csrftoken};
  $.post("/add_layout", post_data, layoutSaved);
}

/* Called to notify a layout was saved */
function layoutSaved() {
  $('#navigate_page_error').text("layout set to " + layout);
  timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  hideLayoutOptions();
}

/* Called to create a new page */
function createPage(pageNumber) {
  var post_data = {album_id: current_album, page_number: pageNumber, 'csrfmiddlewaretoken': csrftoken};
  $.post("/create_page", post_data, pageCreated);
}

/* Callback for createPage */
function pageCreated(response) {
  $('#navigate_page_error').text("A new page was created!");
  timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  showLayoutOptions();
  viewPage(response.page_number);
}

/* Shows layout options when creating a page. Options are normally hidden. */
function showLayoutOptions() {
  $("#layout_options")[0].className = "";
}

/* Hides layout options, since they can't be chosen after a page has been created. */
function hideLayoutOptions() {
  $("#layout_options")[0].className = "hidden";
}

/* Checking if next page exists is done in viewPage and pageViewed */
function nextPage() {
  viewPage(current_page + 1)
}

function previousPage() {
  /* Checking if navigation is possible is done here to avoid an extra post to server.
  If it's not, error text is displayed and disappears after 3 seconds. */
  if (current_page > 1) {
    viewPage(current_page - 1)
  } else {
    $('#navigate_page_error').text("You are already at the first page");
    timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  }
}

function viewPage(pageNumber) {
  var post_data = {album_id: current_album, page_number: pageNumber, 'csrfmiddlewaretoken': csrftoken};
  $.post("/view_page", post_data, pageViewed);
}

/* Called when successfully viewing a page to set the page to a new page */
function pageViewed(response) {
  if(response.result == 'ok'){
    for (i = 1; i <= 3; i++) {
      if (response[i] == null) {
        $("#photo" + i)[0].src = empty_src;
        $("#caption" + i).val(empty_caption);
      }
      else {
        photo = "#photo" + i;
        $("#photo" + i)[0].src = response[i][0];
        $("#caption" + i).val(response[i][1]);
      }
    }
    current_page = response.pagenumber;
    $("#left_page_number").text(current_page);
    setLayout(response.layout);
  }else{
    $('#navigate_page_error').text("You are already at the last page");
    timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  }
}

/* clears error texts */
function clearErrorText(error) {
  if (error == "navigate") {
    $('#navigate_page_error').text("");
    clearInterval(timer);
  }
  else if (error == "image") {
    $('#add_image_error').text("");
    clearInterval(timer);
  }
}

/* Captions are updated when unfocusing from a caption. A picture has to exist, though. */
function updateCaption(target_index) {
   image_url = $("#photo" + target_index)[0].src;

  /* image_url == empty_src doesn't work as itself since the empty src is not in empty_src format when the server is running.
    Thus we check if the part of image_url after the last / matches with empty_src */
  if (endsWith(image_url, empty_src.substring(empty_src.lastIndexOf('/') + 1))) {
    $('#navigate_page_error').text("Add a picture before adding a caption");
    timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  }else{
    caption = $("#caption" + target_index).val();
    var post_data = {album_id: current_album, page_number: current_page, index: target_index, image_url: image_url, caption: caption, 'csrfmiddlewaretoken': csrftoken};
    $.post("/update_image_on_page", post_data, update_image_on_page);
  }
}

/* A helper function for updatecaption to check if the image related to a caption is an "empty" image */
function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

/* Album name is updated when album title is unfocused */
function updateAlbumName() {
  album_name = $("#album_name").text();
  var post_data = {album_id: current_album, album_name: album_name, 'csrfmiddlewaretoken': csrftoken};
  $.post("/album/rename", post_data, albumRenamed);
}

function albumRenamed(response) {
  if (response.result == 'too_long') {
    $('#navigate_page_error').text("The maximum title length is 30 characters.");
    timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  }
}

/* A function to be called in main */
function setEventHandlers() {
  $("#image_button").click(submitImage);
  $("#layout_button").click(saveLayout);
  $("#previous_page").click(previousPage);
  $("#next_page").click(nextPage);
  $("#add_page").click(function() {
    createPage(current_page + 1);
  });

  /* Caption-change listeners*/
  $(".page").on("change", "#caption1", function() {updateCaption(1)});
  $(".page").on("change", "#caption2", function() {updateCaption(2)});
  $(".page").on("change", "#caption3", function() {updateCaption(3)});

  /* Album-title change listener*/
  $("#album_name").focusout(updateAlbumName);

}

function main() {
  current_album = album_id;
  $("#album_name").focus();
  $('#image_url').val("");
  viewPage(1);
  setEventHandlers();
}
  
window.onload = main;