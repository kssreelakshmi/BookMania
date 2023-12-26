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

function handleAddress(id){
  const data ={
    'id':id,
  }

  $.ajax({
    type: "GET",
    url: `/accounts/update-address/`,  // Replace with the actual URL for your view
    dataType: "json", 
    data: data,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },

      //response from backend
    success: (data) => {
      console.log(data);
      document.getElementById('addressId').value = data.formData.id
      document.getElementById('name').value = data.formData.name
      document.getElementById('phone_number').value = data.formData.phone_number
      document.getElementById('address_line_1').value = data.formData.address_line_1
      document.getElementById('address_line_2').value = data.formData.address_line_2
      document.getElementById('city').value = data.formData.city
      document.getElementById('state').value = data.formData.state
      document.getElementById('pincode').value = data.formData.pincode
      const defaultCountry = data.formData.country
      const selectField = document.getElementById('country')

      const validJsonString = data.countries.replace(/,(\s*])/, '$1');
      
      JSON.parse(validJsonString).forEach(element => {
        const option = document.createElement('option')
        if(element[1] == defaultCountry){
          option.selected = true;
        }
        option.value = element[0]
        option.text = element[1]
        selectField.appendChild(option)
        
      });



    },
    error: (error) => {
      console.log(error);
      alert(error)
    }
  });
}

function handleAddressSubmit(){
  const data = {
    "id": document.getElementById('addressId').value,
    "name": document.getElementById('name').value,
    "phone_number": document.getElementById('phone_number').value,
    "address_line_1": document.getElementById('address_line_1').value,
    "address_line_2": document.getElementById('address_line_2').value,
    "city": document.getElementById('city').value,
    "state": document.getElementById('state').value,
    "country": document.getElementById('country').value,
    "pincode": document.getElementById('pincode').value,
    
  }
  console.log(data)
  $.ajax({
    type: "POST",
    url: `/accounts/update-address/`,  // Replace with the actual URL for your view
    dataType: "json", 
    data: data,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"), 
    },
  
      //response from backend
    success: (data) => {
      console.log(data);
      window.location.reload();
    },
    error: (error) => {
      console.log(error);
      alert(error)
    }
  });
  
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