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

function update_wishlist(product_id, action){
  const data = {
    'product_id' : product_id,
    'action' : action,
  }
  $.ajax({
    type: "POST",
    url: `/wishlist/wishlist-update/`,  // Replace with the actual URL for your view
    dataType: "json", 
    data: JSON.stringify(data),
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"), 
    },

      //response from backend
    success: (data) => {
      console.log(data);
      
    },
    error: (error) => {
      console.log(error);
      alert(error)
    }
  });

}


$(".custom-carousel").owlCarousel({
    autoWidth: true,
    loop: true
  });
  $(document).ready(function () {
    $(".custom-carousel .item").click(function () {
      $(".custom-carousel .item").not($(this)).removeClass("active");
      $(this).toggleClass("active");
    });
  });
  

function UpdateProfileField(field){

  var data = {
    field: field.name,
    value: field.value,
  };
  $.ajax({
    type: "POST",
    url: `/accounts/my-account/profile-update/`,  // Replace with the actual URL for your view
    dataType: "json", 
    data: JSON.stringify(data),
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"), 
    },

      //response from backend
    success: (data) => {
      console.log(data.status);
      
    },
    error: (error) => {
      console.log(error);
      alert(error)
    }
  });

}

function EditProfileField(number){
  component =document.getElementById('userprofilefield' + number)
  component.readonly = false
  component.focus()
  component.save()
}