const form = document.getElementById('inputForm');
const first_name = document.getElementById('id_first_name');
const last_name = document.getElementById('id_last_name');
const username = document.getElementById('id_username');
const email = document.getElementById('id_email');
const password = document.getElementById('id_password');
const confirm_password = document.getElementById('id_confirm_password');
const phone_number = document.getElementById('id_phone_number');

// form.addEventListener('submit', e => {
//     let isFormValid = false
//     if (! isFormValid){
//         e.preventDefault();
//     }
//     isFormValid = validateInputs();

// });

const setError = (element, message) => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error');

    errorDisplay.innerText = message;
    inputControl.classList.add('error');
    inputControl.classList.remove('success')
}

const setSuccess = element => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error');

    errorDisplay.innerText = '';
    inputControl.classList.add('success');
    inputControl.classList.remove('error');
};

const isValidFirstName = first_name => {
    const re = /^[A-Za-z]+$/;
    return re.test(first_name);
}
const isValidEmail = email => {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}
const isValidPhoneNumber = phone_number => {
    const re = /^\+?\d{10,12}$/;
    const noRepeatedDigitsRegex = /(.)\1{6,}/;
    return re.test(phone_number) && !noRepeatedDigitsRegex.test(phone_number);
}
const isValidPassword = password => {
    const re = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,8}$/;
    return re.test(password) && !/\s/.test(password);
}

const validateInputs = () => {
    const firstNameValue = first_name.value.trim();
    const lastNameValue = last_name.value.trim();
    const usernameValue = username.value.trim();
    const phoneNumberValue = phone_number.value.trim();
    const emailValue = email.value.trim();
    const passwordValue = password.value.trim();
    const confirmPasswordValue = confirm_password.value.trim();
    let isFormValid = false; 
    if(firstNameValue === '') {
        setError(first_name, 'First name is required');
        isFormValid = false; 
    } else if(! isValidFirstName(firstNameValue)){
        setError(last_name, 'First name should not contain numbers and special characters!');
        const isFormValid = false; 

    }else{
        setSuccess(first_name);
        isFormValid = true; 
    }
    if(lastNameValue === '') {
        setError(last_name, 'Last name is required');
        const isFormValid = false; 
    } else {
        setSuccess(last_name);
        isFormValid = true; 
        
    }
    if(usernameValue === '') {
        setError(username, 'Username is required');
        isFormValid = false; 
    } else {
        setSuccess(username);
        isFormValid = true; 
        
    }
    if(phoneNumberValue === '') {
        setError(phone_number, 'Username is required');
        isFormValid = false; 
    }else if(!isValidPhoneNumber(phoneNumberValue)){
        setError(phone_number, 'Phone number is not valid.')
        isFormValid = false; 
    } 
    else {
        setSuccess(phone_number);
        isFormValid = true; 
    }
    
    if(emailValue === '') {
        setError(email, 'Email is required');
        isFormValid = false; 
    } else if (!isValidEmail(emailValue)) {
        setError(email, 'Provide a valid email address');
        isFormValid = false; 
    } else {
        setSuccess(email);
        isFormValid = true; 
    }
    
    if(passwordValue === '') {
        setError(password, 'Password is required');
        isFormValid = false; 
    } else if (! isValidPassword(passwordValue)) {
        setError(password, 'Password should contain minimum 1 special character, 1 digit, 1 alphabet and should be 6 to 8 characters long!.')
        isFormValid = false; 
    } else {
        setSuccess(password);
        isFormValid = true; 
    }
    
    if(confirmPasswordValue === '') {
        setError(confirm_password, 'Please confirm your password');
        isFormValid = false; 
    } else if (confirmPasswordValue !== passwordValue) {
        setError(confirm_password, "Passwords doesn't match");
        isFormValid = false; 
    } else {
        setSuccess(confirm_password);
        isFormValid = true; 
    }
    return isFormValid

};
