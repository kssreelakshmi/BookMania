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

  console.log(field)

  var data = {
    field: field.name,
    value: field.value,
  };
  $.ajax({
    type: "POST",
    url: `/accounts/profile-update/ `,  // Replace with the actual URL for your view
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
      alert(error)
    }
  });

}


function EditProfileField(number){
  component = document.getElementById('userprofilefield' + number)
  component.readOnly = false;
  component.focus();
  component.setSelectionRange(component.value.length, component.value.length);
}

function SendMobileNumberChangeOtp(){
  var new_number = document.getElementById('MobileNumberChange')
  document.getElementById('MobileNumberChangeError').innerText = ""
  if(!new_number.value){
    document.getElementById('MobileNumberChangeError').innerText = "Please Enter Your New Number"
    return
  }
  var data = {
    new_number : new_number.value,
  }
  $.ajax({
    type : "POST",
    url: `/accounts/mobile-number-change/ `,  // Replace with the actual URL for your view
    dataType: "json", 
    data: JSON.stringify(data),
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"), 
    },

      //response from backend
    success: (data) => {
      if (data.status === "success"){
        console.log(data)
        document.getElementById('MobileNumberChangeOtpDiv').classList.remove('d-none')
        document.getElementById('MobileNumberChangeOtpbtn').classList.add('d-none')
        document.getElementById('MobileNumberChange').setAttribute('readonly', true);
       
      }
      else{
        console.log(data);
        document.getElementById('MobileNumberChangeOtpErrors').innerText = data.message

      }
      
    },
    error: (error) => {
      console.log(error);
    }

  });
}

function MobileNumberChangeOtpVerify(){
  var new_number = document.getElementById('MobileNumberChange')
  var otp = document.getElementById('MobileNumberChangeOtp')

  document.getElementById('MobileNumberChangeError').innerText = ""
  if(!otp.value){
    document.getElementById('MobileNumberChangeError').innerText = "Please Enter Your New Number"
    return
  }
  var data = {
    new_number : new_number.value,
    otp : otp.value ,
  }
  $.ajax({
    type : "POST",
    url: `/accounts/mobile-number-change/verify/ `,  // Replace with the actual URL for your view
    dataType: "json", 
    data: JSON.stringify(data),
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"), 
    },

      //response from backend
    success: (data) => {
      if (data.status === "success"){
        console.log(data);
        location.reload();
      }
      else{
        console.log(data);
        document.getElementById('MobileNumberChangeOtpErrors').innerText = data.message

      }
      
    },
    error: (error) => {
      console.log(error);
    }

  });
}

function sendEmailChangeOtpMail(){
  console.log('asdfghjkldfghj');
  var email_id = document.getElementById('EmailChangeOtpNewMail')
  console.log(email_id)
  document.getElementById('sendEmailChangeOtpMailNewMailError').innerText = ''
  if (!email_id.value){
    document.getElementById('sendEmailChangeOtpMailNewMailError').innerText = 'Please enter a Email-ID'
    return
  }

  var data = {
    new_email: email_id.value,
  };

  $.ajax({
    type: "POST",
    url: `/accounts/email-change/`,  // Replace with the actual URL for your view
    dataType: "json",
    data: JSON.stringify(data),
    headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"), 
      },
      success: (data) => {
        if (data.status === "success") {
          console.log(data);
          document.getElementById('EmailChangeOtpNewMailDiv').classList.remove('d-none')
          document.getElementById('EmailChangeOtpNewMailbtn').classList.add('d-none')
          document.getElementById('EmailChangeOtpNewMailOtp').setAttribute('readonly', true);

      } else {
          console.log(data);
          document.getElementById('sendEmailChangeOtpMailNewMailError').innerText = data.message

      }
        
    },
    error: (xhr, status, error) => {
        console.log("error");
        console.log(error);
    }
});
  
}


function sendEmailChangeOtpMailVerify(){
  console.log("ok");
  var email_id = document.getElementById('EmailChangeOtpNewMail')
  var otp = document.getElementById('EmailChangeOtpMailOtp')

  document.getElementById('EmailChangeOtpMailOtpError').innerText = ''
  if (!otp.value){
    document.getElementById('EmailChangeOtpMailOtpError').innerText = 'Please enter the '
    return
  }

  var data = {
    new_email: email_id.value,
    otp : otp.value
  };

  $.ajax({
    type: "POST",
    url: `/accounts/email-change/verify/`,
    dataType: "json",
    data: JSON.stringify(data),
    headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"), 
      },
      success: (data) => {
        if (data.status === "success") {
          // email success
          console.log(data);
          location.reload();

      } else {
          // Password change error
          console.log(data);
          document.getElementById('sendEmailChangeOtpMailNewMailOtpError').innerText = data.message
      }
        
    },
    error: (xhr, status, error) => {
        console.log("error");
        console.log(error);
    }
});
  
}

function UpdateFieldUserProfilePassword(get_old_password,get_password1,get_password2) {

  document.getElementById(get_old_password+'Error').innerText = ''
  document.getElementById(get_password1+'Error').innerText = ''
  document.getElementById(get_password2+'Error').innerText = ''

  var old_password = document.getElementById(get_old_password)
  var password1 = document.getElementById(get_password1)
  var password2 = document.getElementById(get_password2)

  if (!old_password.value){
    document.getElementById(get_old_password+'Error').innerText = 'Please Enter Password'
    return
  }

  if (!password1.value){
    document.getElementById(get_password1+'Error').innerText = 'Please Enter Password'
    return
  }

  if (!password2.value){
    document.getElementById(get_password2+'Error').innerText = 'Please Enter Password'
    return
  }

  if(matchPassword(get_password1,get_password2))
  {
    url = '/users/basic/changepassword'
    var data = {
      old_password: old_password.value,
      password2: password2.value,
    };
    
    $.ajax({
        type: "POST",
        url: url,  // Replace with the actual URL for your view
        dataType: "json",
        data: JSON.stringify(data),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"), 
          },
          success: (data) => {
            if (data.status === "success") {
              // Password change success
              console.log(data);
              location.reload();
          } else {
              // Password change error
              console.log(data);
              // Display the error message on the page
              document.getElementById(get_old_password + 'Error').innerText =data.message;
          }
        },
        error: (xhr, status, error) => {
            // Display the error message on the page
            document.getElementById(get_old_password + 'Error').innerText = 'Error: ' + xhr.responseText;
            console.log("error");
            console.log(error);
        }
    });
    
  }
  else{
    document.getElementById(get_password2+'Error').innerText = 'Password Not Match'
  }

};


//password change user send mail 
function sendPasswordResetOtpMail() {
  document.getElementById('sendPasswordResetOtpMailSpinnner').classList.remove('d-none')
  document.getElementById('sendPasswordResetOtpMailBtn').classList.add('disabled')
  console.log("call");


  $.ajax({
      type: "POST",
      url: `accounts/password-change/`,  // Replace with the actual URL for your view
      dataType: "json",
      // data: JSON.stringify(data),
      headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"), 
        },
        success: (data) => {
          if (data.status === "success") {
            // Password change success
            var inTwoMinutes = new Date(new Date().getTime() + 2 * 60 * 1000);
            Cookies.set('can_otp_enter', 'True', { expires: inTwoMinutes, path: '/' });
            window.location = data.redirect_url;
        } else {
            // Password change error
            console.log(data);
            // Display the error message on the page
        }
          
      },
      error: (xhr, status, error) => {
          // Display the error message on the page
          console.log("error");
          console.log(error);
      }
  });
    

};







