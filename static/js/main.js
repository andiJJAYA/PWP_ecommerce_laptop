
window.IS_LOGGED_IN =
    document.body.dataset.loggedIn === "true";

/* =========================
   NAV ACTIVE ON SCROLL
========================= */
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-scroll");

function setActiveMenu() {
    let current = "home";

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 80;
        if (scrollY >= sectionTop) {
            current = section.getAttribute("id");
        }
    });

    navLinks.forEach(link => {
        link.classList.remove("active");
        if (link.getAttribute("href") === "#" + current) {
            link.classList.add("active");
        }
    });
}

window.addEventListener("load", setActiveMenu);
window.addEventListener("scroll", setActiveMenu);


/* =========================
   PRODUCT SLIDER
========================= */
document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".product-card");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    if (!cards.length) return;

    let currentIndex = 0;
    const visibleCount = 4;
    let isAnimating = false;

    function showCards() {
        cards.forEach((card, index) => {
            card.classList.remove("fade-in", "fade-out");

            if (index >= currentIndex && index < currentIndex + visibleCount) {
                card.style.display = "block";
                requestAnimationFrame(() => card.classList.add("fade-in"));
            } else {
                card.style.display = "none";
            }
        });
    }

    function animateChange(direction) {
        if (isAnimating) return;
        isAnimating = true;

        cards.forEach((card, index) => {
            if (index >= currentIndex && index < currentIndex + visibleCount) {
                card.classList.add("fade-out");
            }
        });

        setTimeout(() => {
            currentIndex += direction;
            showCards();
            isAnimating = false;
        }, 300);
    }

    nextBtn?.addEventListener("click", () => {
        if (currentIndex + visibleCount < cards.length) {
            animateChange(1);
        }
    });

    prevBtn?.addEventListener("click", () => {
        if (currentIndex > 0) {
            animateChange(-1);
        }
    });

    showCards();
});


/* =========================
   LOGIN GUARD (GLOBAL)
========================= */
function requireLogin() {
    if (!window.IS_LOGGED_IN) {
        alert("Silakan login terlebih dahulu!");
        window.location.href = "/login";
        return false;
    }
    return true;
}


/* =========================
   ORDER MODAL (BUY)
========================= */
let selectedPrice = 0;

function openOrder(product) {
    document.getElementById("orderModal").style.display = "flex";
    document.getElementById("orderImg").src = product.img;
    document.getElementById("orderName").innerText = product.name;
    document.getElementById("orderSpec").innerText = product.spec;
    document.getElementById("orderPrice").innerText = product.price;

    selectedPrice = product.price.replace(/\./g, "");
}

// Tunggu DOM selesai dimuat
document.addEventListener("DOMContentLoaded", () => {
    const orderModal = document.getElementById("orderModal");
    const closeBtn = document.querySelector(".close");

    if (closeBtn) {
        closeBtn.onclick = function() {
            orderModal.style.display = "none";
        }
    }

    window.onclick = function(event) {
        if (event.target == orderModal) {
            orderModal.style.display = "none";
        }
    }
});

/* =========================
   ORDER MODAL & CHECKOUT
========================= */
function handleBuy(product) {
    if (!window.IS_LOGGED_IN) {
        alert("Silakan login terlebih dahulu.");
        window.location.href = "/login";
        return;
    }

    document.getElementById("orderModal").style.display = "flex";
    document.getElementById("orderImg").src = product.img;
    document.getElementById("orderName").innerText = product.name;
    document.getElementById("orderSpec").innerText = product.spec; 
    document.getElementById("orderPrice").innerText = "Rp " + Number(product.price).toLocaleString("id-ID");
    document.getElementById("productIdInput").value = product.id;
    selectedPrice = product.price;
}

// Update klik bank
document.querySelectorAll(".bank-item").forEach(bank => {
    bank.addEventListener("click", () => {
        document.querySelectorAll(".bank-item").forEach(b => b.classList.remove("active"));
        bank.classList.add("active");
        
        const namaBank = bank.getAttribute("data-bank");
        document.getElementById("bankPilihanInput").value = namaBank;
        
        document.getElementById("paymentTotal").style.display = "block";
        document.getElementById("finalPrice").innerText = Number(selectedPrice).toLocaleString("id-ID");
    });
});

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".buy-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            handleBuy({
                id: btn.dataset.id,
                img: btn.dataset.img,
                name: btn.dataset.name,
                spec: btn.dataset.spec,
                price: btn.dataset.price
            });
        });
    });
});


// Proses Kirim ke Backend
document.getElementById("orderForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    if (!document.getElementById("bankPilihanInput").value) {
        alert("Pilih bank terlebih dahulu!");
        return;
    }

    const formData = new FormData(this);

    fetch('/checkout', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById("orderModal").style.display = "none";
            document.getElementById("successModal").style.display = "flex";
            this.reset();
        } else {
            alert("Gagal: " + data.message);
        }
    });
});

/* =========================
   CONSULTATION FORM
========================= */
document.addEventListener("DOMContentLoaded", () => {
    const consultForm = document.getElementById("consultForm");
    const successModal = document.getElementById("successModal");

    if (consultForm) {
        consultForm.addEventListener("submit", function(e) {
            e.preventDefault(); // Mencegah refresh halaman

            const formData = new FormData(this);

            // Kirim data ke Flask via Fetch
            fetch('/submit_consultation', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // 1. Munculkan Popup Sukses
                    if (successModal) {
                        successModal.style.display = "flex";
                    }
                    // 2. Kosongkan Form
                    consultForm.reset();
                } else {
                    alert("Gagal mengirim: " + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("Terjadi kesalahan koneksi.");
            });
        });
    }
});

// Fungsi untuk menutup modal
function closeSuccess() {
    const successModal = document.getElementById("successModal");
    if (successModal) {
        successModal.style.display = "none";
    }
}


