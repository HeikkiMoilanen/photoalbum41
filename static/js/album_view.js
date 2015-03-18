/* Global variables */
var layout = 1;
var current_album;
var pages;
var current_page = 1;
var page_id = "right_page";
var empty_src = "/photoalbum/static/images/insert_pic.jpg";
/*var empty_src = "{% static 'images/insert_pic.jpg' %}";*/
var empty_caption = "insert your caption here"
/* This is for error messages to disappear after a duration */
var timer;



function update_image_on_page(response) {
  console.log(response);
}

/* Fetches next spread. Hides pages you came from. */
function nextSpread() {

  /* Checking if navigation is possible is done here to avoid an extra post to server.
  If it's not, error text is displayed and disappears after 3 seconds. */
  if (current_page + 1 === pages) {
    console.log("last page");
    $('#navigate_page_error').text("You are already at the last page");
    timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  } else {
    if (current_page <= 2) {
      $("#previous_spread").removeClass("hidden");
    }
    hidePage(current_page);
    hidePage(current_page + 1);
    current_page = current_page + 2;
    viewSpread(current_page);
  }
}

/* Fetches previous spread. Hides pages you came from. */
function previousSpread() {
  /* Checking if navigation is possible is done here to avoid an extra post to server.
  If it's not, error text is displayed and disappears after 3 seconds. */
  if (current_page > 1) {

    if (pages - current_page <= 2) {
      $("#next_spread").removeClass("hidden");
    }

    hidePage(current_page);
    hidePage(current_page + 1);
    current_page = current_page - 2;
    viewSpread(current_page);
  } 

  else {
    
    $('#navigate_page_error').text("You are already at the first page");
    timer = setInterval(function(){clearErrorText("navigate")}, 3000);
  }
}

/* Views two pages at a time. */
function viewSpread(pageNumber) {
  console.log("attempted pagenumber " + pageNumber);
  if (pageNumber <= 2) {
    $("#previous_spread").addClass("hidden");
  }
  if (pages - pageNumber <= 2) {
    $("#next_spread").addClass("hidden");
  }
  revealPage(pageNumber);
  revealPage(pageNumber + 1);
}


/* clears error texts */
function clearErrorText(error) {
  if (error == "navigate") {
    $('#navigate_page_error').text("");
    clearInterval(timer);
  }
}

function setEventHandlers() {
  $("#previous_spread").click(previousSpread);
  $("#next_spread").click(nextSpread);
}

/* Sets even pages to right hand side */
function setSpreads() {

  for (var i = 1; i <= pages; i++) {
    if (i%2 === 0) {
      $("#page_" + i).removeClass("left_page").addClass("right_page");
      $("#page_number_" + i).removeClass("left_page_number").addClass("right_page_number");
    }
  }
}

/* Helper function to hide a given page */
function hidePage(pageNumber) {

  $("#page_" + pageNumber).addClass("hidden");
}

/* Helper function to reveal a given page */
function revealPage(pageNumber) {

  $("#page_" + pageNumber).removeClass("hidden");
}

function main() {
  current_album = album_id;
  pages = max_pages;
  console.log("album name is " + album_name);
  $('#image_url').val("");
  setSpreads();
  viewSpread(1);
  setEventHandlers();
}
  
window.onload = main;