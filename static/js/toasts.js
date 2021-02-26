function myFunction() {
  document.getElementById("toast");
}



setTimeout(function(){
  if ($('#toast').length > 0) {
    $('#toast').remove();
  }
}, 5000)