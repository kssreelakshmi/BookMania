function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  
  
  function send_data(inputid, variant_slug, image_id='thumbnail') {
      var formData = new FormData();
      var files = $('#photo'+ inputid)[0].files[0]
      formData.append('file', files);
      formData.append('image_id', image_id);
  
      $.ajax({
        type: "POST",
        url: `/admin-control/product-management/product-variant-update/additional-product-images/${variant_slug}/`, 
        dataType: "json", 
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            "X-Requested-With" : "XMLHttpRequest",
            "X-CSRFToken" : getCookie("csrftoken"), 
          },
        success: (data) => {
          console.log(data);
          document.getElementById('image'+ inputid).setAttribute('src', data['new_image'])
          },
        error: (error) => {
            console.log(error);
            alert(error)
          }
      });
    }

    


    const handleImage = (id) =>{
      const image_input_field = document.getElementById(id)
      let images = image_input_field.files
      console.log(images);

      if (image_input_field.value){

        for(const file of Object.values(images)){

            if(!file.type.includes('image')){
              image_input_field.value = null;
              document.getElementById('image_warning').hidden = false;
              setTimeout(function(){
                $('#image_warning').fadeOut('slow')
            }, 4000)
              break;
            }
            else{
              console.log('supported file');
            }

          }
      }

      // if (thumbnail_field.value){
      //   if (!thumbnailImage.type.includes('image')){
      //     thumbnail_field.value = null;
      //     alert('Not supported file, kindly re-enter')
      //   }
      //   else{
      //     console.log('supports');
      //   }
      // }

      // if(additional_image_field.value){
      //   console.log(additional_image_field.files);


      // }


    }
    
    function showSelectedOption(selectElement, order_number) {
      var selectedOption = selectElement.value
      console.log (selectedOption);
      var data = {
        selected_option: selectedOption
      };
      $.ajax({
        type: "POST",
        url: `/admin-control/order-management/order-details/${order_number}/`,
        dataType: "json", 
        data: JSON.stringify(data),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"), 
        },
        success: (data) => {
          console.log(data);
          swal(data.status, `Order has been updated with the status : ${data.selected_option}`);
          
        },
        error: (error) => {
                console.log(error);
                alert(error)
              }
        });
      }

// order detail page on modal operation order_product_id accessing to handleOperation function  
      
$(document).ready(function(){
  $('#reasonsModal').on('show.bs.modal', function (e) {
    console.log('showwwwww');
    const reasonDiv = document.getElementById('reason-div')
    const tempInput = document.createElement('input')
    tempInput.id = 'temp-input'
    tempInput.hidden = true

    reasonDiv.appendChild(tempInput)
    
  });
  
  $('#reasonsModal').on('hide.bs.modal', function (e) {
    console.log('leave');
    document.getElementById('temp-input').remove();
  });
});

    
    
function order_operation(order_product_id, operation, reason, otherReason = null){
  console.log('working');
  const title = document.getElementById('reasonsModalTitle')
  const reasonElement = document.getElementById('user-reason')
  document.getElementById('temp-input').value = order_product_id
      
      
  if(operation === 'cancel')
  {
    title.innerHTML = 'Inspect Cancellation Reason and Proceed...'
    console.log('sdfrttgyhujikolp');
    if(otherReason){
      reasonElement.innerHTML = 'REASON : ' + reason;
      reasonElement.classList.add('reason_others');
      document.getElementById('user-other-reason').innerHTML = otherReason;
    }
    else{
      reasonElement.innerHTML = reason;
    }
  }
  else if(operation === 'return'){
    title.innerHTML = 'Inspect  Return Reason and Proceed...'
    if(otherReason){
      reasonElement.innerHTML = 'REASON : ' + reason;
      reasonElement.classList.add('reason_others');
      document.getElementById('user-other-reason').innerHTML = otherReason;
    }
    else{
      reasonElement.innerHTML = reason;
    }
  }
  
  
  
}

function handleOperation(operation){
  let order_product_id = document.getElementById('temp-input').value
  

  var data = {
    order_product_id: order_product_id,
    operation: operation
  };
  $.ajax({
      type: "POST",
      url: '/admin-control/order-management/order-cancel-or-return/',
      dataType: "json", 
      data: JSON.stringify(data),
      headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"), 
        },
      success: (data) => {
          console.log(data);
          swal(data.message, data.additional_message);
          setTimeout(() =>{
            window.location.reload();
          }, 3000)
        },
      error: (error) => {
          console.log(error);
          alert(error)
        }
  });
  document.getElementById('modal-close').click();

}

function saleHandle() {
  var startDate = document.getElementById('start_date');
  var endDate = document.getElementById('end_date').;
 console.log(startDate);
  var data = {
      'start_date': startDate,
      'end_date': endDate
  };

  // Send data to Python backend using AJAX
  $.ajax({
      type: 'POST',
      url:`/admin-control/`,
      data: JSON.stringify(data),
      
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"), 
      },
      success: function(response) {
          console.log(response);
      },
      error: function(error) {
          console.log(error);
      }
  });
}
