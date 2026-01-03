const input = document.getElementById('navbarSearch');
const resultBox = document.getElementById('searchResult');

input.addEventListener('keyup', async () => {
    const q = input.value.trim();

    if (q.length < 2) {
        resultBox.classList.add('d-none');
        resultBox.innerHTML = '';
        return;
    }

    const res = await fetch(`/search?q=${q}`);
    const data = await res.json();

    if (data.length === 0) {
        resultBox.innerHTML = `
            <div class="search-empty">
                Tidak ada produk ditemukan
            </div>`;
        resultBox.classList.remove('d-none');
        return;
    }

    resultBox.innerHTML = data.map(p => `
        <a href="/#product-${p.id}"
   class="search-item"
   data-id="${p.id}"
   data-img="/static/img/products/${p.gambar}"
   data-name="${p.nama}"
   data-spec="${p.spec || ''}"
   data-price="${p.harga}">

           
            <img src="/static/img/products/${p.gambar}">
            <div>
                <div class="name">${p.nama}</div>
                <div class="price">
                    Rp ${Number(p.harga).toLocaleString('id-ID')}
                </div>
            </div>
        </a>
    `).join('');

    resultBox.classList.remove('d-none');
});

// klik di luar → tutup
document.addEventListener('click', e => {
    if (!input.contains(e.target)) {
        resultBox.classList.add('d-none');
    }
});

document.addEventListener('click', function (e) {
    const item = e.target.closest('.search-item');
    if (!item) return;

    e.preventDefault();

    const id = item.dataset.id;

    // 1. tutup dropdown
    resultBox.classList.add('d-none');

    // 2. scroll ke produk
    const target = document.getElementById(`product-${id}`);
    if (target) {
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });

        target.classList.add('highlight-product');
        setTimeout(() => {
            target.classList.remove('highlight-product');
        }, 2000);
    }

    // 3. buka modal otomatis (delay biar scroll selesai)
    setTimeout(() => {
        handleBuy({
            id: item.dataset.id,
            img: item.dataset.img,
            name: item.dataset.name,
            spec: item.dataset.spec,
            price: item.dataset.price,
        });
    }, 600);
});
