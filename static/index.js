function signup() {
    let name = $("#name").val();
    let email = $("#email").val();
    let password = $("#password").val();
    let ktpfile = document.getElementById("ktp").files[0];

    if (name == '' || email == '' || password == '' || !ktpfile) {
        Swal.fire('Oops', 'Data tidak lengkap!', 'error');
    } else {
        let formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        formData.append("password", password);
        formData.append("ktp", ktpfile);

        $.ajax({
            type: "POST",
            url: "/sign_up/save",
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.result === 'success') {
                    Swal.fire('Berhasil!', 'Akun berhasil didaftarkan', 'success').then(() => {
                        window.location.replace("/signin");
                    });
                } else {
                    Swal.fire('Gagal!', response.message, 'error');
                }
            },
            error: function () {
                Swal.fire('Gagal!', 'Terjadi kesalahan saat mengirim data.', 'error');
            }
        });
    }
}


function sign_in() {
    let email = $("#email").val();
    let password = $("#password").val();

    $.ajax({
        type: "POST",
        url: "/sign_in",
        data: {
            email: email,
            password: password,
        },
        success: function (response) {
            if (response["result"] === "success") {
                $.cookie("mytoken", response["token"], { path: "/" });
                Swal.fire({
                    title: 'Login Berhasil!',
                    text: 'Anda akan diarahkan ke halaman utama.',
                    icon: 'success',
                    showConfirmButton: false,
                    timer: 2000,
                    willClose: () => {
                        window.location.replace("/");
                    }
                });
            } else {
                Swal.fire({
                    title: 'Oops!',
                    text: response["msg"],
                    icon: 'error',
                    confirmButtonText: 'Coba Lagi'
                });
            }
        },
        error: function () {
            Swal.fire({
                title: 'Kesalahan Server!',
                text: 'Terjadi kesalahan pada server. Silakan coba lagi nanti.',
                icon: 'error',
                confirmButtonText: 'Tutup'
            });
        }
    });
}


function admin_signup() {
    let name = $("#name").val();
    let email = $("#email").val();
    let password = $("#password").val();

    if (name == '' || email == '' || password == '') {
        Swal.fire(
            'Oops',
            'Data tidak lengkap!',
            'error'
        )
    } else {
        $.ajax({
            type: "POST",
            url: "/sign_up/admin",
            data: {
                name: name,
                email: email,
                password: password
            },
            success: function (response) {
                Swal.fire(
                    'Done',
                    'You are signed up, nice!',
                    'success'
                )
                window.location.replace("/signin/admin");
            },
        });
    }


}
function admin_sign_in() {
    let email = $("#email").val();
    let password = $("#password").val();

    Swal.fire({
        title: 'Memproses...',
        text: 'Silakan tunggu',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    $.ajax({
        type: "POST",
        url: "/sign_in/admin",
        data: {
            email: email,
            password: password,
        },
        success: function (response) {
            Swal.close();

            if (response["result"] === "success") {
                $.cookie("mytoken", response["token"], { path: "/" });
                
                Swal.fire({
                    title: 'Berhasil!',
                    text: 'Login berhasil, Anda akan diarahkan ke halaman admin...',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    window.location.replace("/home_admin");
                });
            } else {
                Swal.fire(
                    'Oops...',
                    response["msg"],
                    'error'
                );
            }
        },
        error: function () {
            Swal.close();
            Swal.fire(
                'Error',
                'Terjadi kesalahan pada server, coba lagi nanti',
                'error'
            );
        }
    });
}


function sign_out() {
    Swal.fire({
        title: "Anda yakin ingin keluar?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Ya, keluar",
        cancelButtonText: "Batal"
    }).then((result) => {
        if (result.isConfirmed) {
            $.removeCookie("mytoken", { path: "/" });  
            Swal.fire("Berhasil", "Anda telah logout!", "success").then(() => {
                window.location.href = "/";  
            });
        }
    });
}

function sampah(event) {
    event.preventDefault();

    // Ambil nilai data-logged-in dari elemen yang diklik (event.target)
    const loggedIn = event.currentTarget.dataset.loggedIn === "true";

    if (loggedIn) {
        // Langsung arahkan ke halaman detail jika sudah login
        window.location.href = "/detail";
        return;
    }

    // Kalau belum login, munculkan alert
    Swal.fire({
        title: "Harap Login Terlebih Dahulu",
        text: "Anda harus login untuk melakukan pengaduan.",
        icon: "warning",
        confirmButtonText: "OK"
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/signin";
        }
    });
}



function notif() {
    Swal.fire({
        title: "Harap Login Terlebih Dahulu",
        text: "Anda harus login untuk mengirim pesan.",
        icon: "warning",
        confirmButtonText: "OK"
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/signin";
        }
    });
}

function Verified() {
    const el = document.getElementById("verified-status");

    el.classList.add("fade-out-smooth");

    setTimeout(() => {
        if (el.innerText.trim() === "✔ Terverifikasi") {
            el.innerText = "✔";
        } else {
            el.innerText = "✔ Terverifikasi";
        }

        el.classList.remove("fade-out-smooth");
        el.classList.add("fade-in-smooth");

        setTimeout(() => {
            el.classList.remove("fade-in-smooth");
        }, 300);
    }, 300);
}

function cekPengaduan() {
    const isVerified = document.getElementById("user-status").dataset.verified === "true";

    if (!isVerified) {
        Swal.fire({
            icon: 'warning',
            title: 'Akun Belum Terverifikasi',
            text: 'Silakan tunggu verifikasi akun dari admin untuk mengakses menu ini.',
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'OK'
        });
    } else {
        window.location.href = "/cek_pengaduan";
    }
}

function kirim() {
    let nama = $("#nama").val();
    let email = $("#email").val();
    let pesan = $("#pesan").val();

    if (nama === '' || email === '' || pesan === '') {
        Swal.fire({
            title: 'Form tidak boleh kosong',
            text: 'Semua data wajib diisi!',
            icon: 'error',
            confirmButtonText: 'OK'
        });
        return false; 
    } else {
        $.ajax({
            type: "POST",
            url: "/contact",
            data: {
                nama: nama,
                email: email,
                pesan: pesan
            },
            success: function (response) {
                Swal.fire({
                    title: 'Yeayyy!',
                    text: 'Pesan berhasil dikirim',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.reload();
                });
            },
            error: function (xhr, status, error) {
                Swal.fire({
                    title: 'Error',
                    text: 'Terjadi kesalahan, coba lagi nanti!',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        });
        return false;
    }
}


document.addEventListener('DOMContentLoaded', function() {
    var submitButton = document.getElementById('submitButton');
  
    
    submitButton.addEventListener('click', function(event) {
      event.preventDefault(); 
      
      
      var nama = document.getElementById('nama').value;
      var address = document.getElementById('address').value;
      var pesan = document.getElementById('pesan').value;
  
      
      if (nama === "" || address === "" || pesan === "") {
        Swal.fire({
          icon: 'error',
          title: 'Form tidak boleh kosong',
          text: 'Harap isi semua form sebelum mengirimkan pengaduan!',
        });
      } else {
        document.querySelector('form').submit();
      }
    });
  });
  


function openModal() {
    const modal = document.getElementById('modal');
    modal.classList.add('is-active');
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('is-active');
    modal.classList.add('is-closing');

    setTimeout(function () {
        modal.classList.remove('is-closing');
    }, 300);
}


