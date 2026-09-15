// Hitung usia otomatis di Form Pasien
const dobInput = document.getElementById('tanggal_lahir');
const usiaInput = document.getElementById('usia');

if(dobInput && usiaInput) {
    dobInput.addEventListener('change', function() {
        if(this.value){
            const dob = new Date(this.value);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const m = today.getMonth() - dob.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
                age--;
            }
            usiaInput.value = age;
        }
    });
    // Trigger saat load halaman edit
    dobInput.dispatchEvent(new Event('change'));
}

// Fungsi Pencarian di List View
function cariPasien() {
    let input = document.getElementById("searchInput").value.toLowerCase();
    let table = document.getElementById("pasienTable");
    let tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        let tdNama = tr[i].getElementsByTagName("td")[2]; 
        if (tdNama) {
            let txtValue = tdNama.textContent || tdNama.innerText;
            if (txtValue.toLowerCase().indexOf(input) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }       
    }
}