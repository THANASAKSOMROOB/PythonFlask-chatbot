const form = document.getElementById('form');
const name_ = document.getElementById('name');
const email = document.getElementById('email');
const message = document.getElementById('message');

/* toastr */
toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": false,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "3000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
}


form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (name_.value === '' || name_.value === null) {
        showerror(name_, 'กรุณากรอกชื่อ')
    } else {
        showsuccess(name_);
    }
    if (email.value === '' || email.value === null) {
        showerror(email, 'กรุณากรอกอีเมล')
    } else if (!validateEmail(email.value)) {
        showerror(email, 'รูปแบบอีเมลไม่ถูกต้อง ตัวอย่างเช่น example01@gmail.com');
    }
    else {
        showsuccess(email);
    }
    if (message.value === '' || message.value === null) {
        showerror(message, 'กรุณากรอกรายละเอียดข้อเสนอแนะ')
    } else {
        showsuccess(message);
    }
    if (name_.value !== '' && email.value !== '' && message.value !== '' && name_.value !== null && email.value !== null && message.value !== null && validateEmail(email.value)) {
        $(function () {
            toastr.success("บันทึกข้อเสนอแนะสำเร็จ")
        });
        /* $(function(){
            toastr.options.onHidden = function(){
                window.location.href = 'http://localhost:200/feedback'
            }
            toastr.success("success")
        }); */
        e.currentTarget.submit();
    }
});



function showerror(input, message) {
    const formwrap_input1 = input.parentElement;
    formwrap_input1.className = 'wrap-input1 error'
    const small = formwrap_input1.querySelector('small');
    small.innerText = message;
}

function showsuccess(input) {
    const formwrap_input1 = input.parentElement;
    formwrap_input1.className = 'wrap-input1 success'
    const small = formwrap_input1.querySelector('small');

}

const validateEmail = (email) => {
    return String(email)
        .toLowerCase()
        .match(
            /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        );
};



