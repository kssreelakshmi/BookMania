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