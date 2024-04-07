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


      // ORDERPRODUCT STATUS CHANGE
    function orderProductStatusChange(selectElement, orderProductId) {
      console.log("ivide ethiiii");
      var selectedOption = selectElement.value
      console.log (selectedOption);
      var data = {
        selectedOption: selectedOption,
        orderProductId: orderProductId

      };
      console.log(data);
      $.ajax({
        type: "POST",
        url: "/admin-control/order-management/change-order-product-status/",
        dataType: "json", 
        data: JSON.stringify(data),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"), 
        },
        success: (data) => {
          console.log(data);
          swal(data.status, data.message);

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
  const title = document.getElementById('reasonsModalTitle')
  const reasonElement = document.getElementById('user-reason')
  document.getElementById('temp-input').value = order_product_id
      
      
  if(operation === 'cancel')
  {
    title.innerHTML = 'Inspect Cancellation Reason and Proceed...'
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
     
  let startDate = document.getElementById('start_date').value;
  let endDate = document.getElementById('end_date').value;

  if(! startDate){
    document.getElementById('start_date_error').hidden = false;
    return
  }
  else{
    document.getElementById('filterbutton').disabled = false;
  }

  if(! endDate){
    endDate = ''
  }
  const url = new URL(window.location.href)
  url.search =''
  const urlParams = new URLSearchParams(window.location.search);
  urlParams.set('start-date', startDate);
  urlParams.set('end-date', endDate);
  const newUrl = `${window.location.pathname}?${urlParams.toString()}`;

  console.log(url);
  window.location.href = newUrl;

  };


  
function getDashboardSalesData(){
  $.ajax({
    type: "GET",
    url: "/admin-control/api/dashboard/data/sales",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
    success: (data) => {
      if (data.status === "success") {
          setChartSalesData(data.data)
      } else {
        console.log(data);
    }
      
  },
  error: (xhr, status, error) => {
      // Display the error message on the page
      console.log("error");
      console.log(error);
  }
});
}


function setChartSalesData(data)
{
  const salesChart = document.getElementById('sales-chart');
  const labels = Object.keys(data);
  const datasetData = Object.values(data);
  new Chart(salesChart, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: datasetData,
        backgroundColor:['#ABEBC6','#AED6F1','#F5B7B1','#FCF3CF','#F6DDCC','#D5D8DC'],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

// Bar chart of top 5 selling products(variants)
function getDashboardProduct2SalesData(){
  console.log('sdfghjkl');
  $.ajax({
    type: "GET",
    url: "/admin-control/api/dashboard/data/product2sales",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
    success: (data) => {
      if (data.status === "success") {
        console.log(data);
        setDashboardProduct2SalesData(data.data)
        
      } else {
        console.log(data);
    }
      
  },
  error: (xhr, status, error) => {
      // Display the error message on the page
      console.log("error");
      console.log(error);
  }
});
} 

function setDashboardProduct2SalesData(data)
{
  
  const topProductsChart = document.getElementById('top-products-sale');
  const labels = Object.keys(data);  
 
  const datasetData = Object.values(data);
  
  new Chart(topProductsChart, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'No Of Sales vs Products',
        data: datasetData,
        backgroundColor:['#ABEBC6','#AED6F1','#F5B7B1','#FCF3CF','#F6DDCC','#D5D8DC','#EDBB99','#CD6155','#5D6D7E','#1ABC9C','#BB8FCE'],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  }
  );

}

