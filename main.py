from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OK Market - Oziq-ovqat do'koni</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50 text-gray-800 pb-20">

    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center space-x-2">
                <div class="bg-emerald-600 text-white p-2 rounded-xl font-bold text-lg">OK</div>
                <div>
                    <h1 class="font-bold text-lg leading-tight">OK Market</h1>
                    <p class="text-xs text-gray-500">Tezkor yetkazib berish</p>
                </div>
            </div>
            <button onclick="openCart()" class="bg-emerald-50 text-emerald-600 p-2.5 rounded-xl relative">
                <i class="fa-solid fa-cart-shopping"></i>
                <span id="cartBadge" class="absolute -top-1 -right-1 bg-emerald-600 text-white text-[10px] w-5 h-5 rounded-full flex items-center justify-center font-bold hidden">0</span>
            </button>
        </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 mt-3">
        <!-- Qidiruv satri -->
        <div class="relative">
            <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-gray-400 text-sm"></i>
            <input type="text" id="searchInput" oninput="filterProducts()" placeholder="Mahsulot va tovarlarni izlash..." class="w-full bg-gray-100 text-sm rounded-xl pl-10 pr-4 py-2.5 focus:bg-white transition">
        </div>

        <!-- Kategoriyalar -->
        <div id="categoryBar" class="flex gap-2 overflow-x-auto no-scrollbar pb-1 mt-3">
            <button onclick="setCategory('all', this)" class="cat-btn active bg-emerald-500 text-white px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">Barchasi</button>
            <button onclick="setCategory('shirinlik', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">Shirinliklar</button>
            <button onclick="setCategory('masalliq', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">Masalliqlar</button>
            <button onclick="setCategory('ichimlik', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">Ichimliklar</button>
            <button onclick="setCategory('meva', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">Meva-sabzavot</button>
        </div>

        <!-- Aksiya Banner -->
        <div class="max-w-3xl mx-auto px-4 mt-4">
            <div class="bg-gradient-to-r from-emerald-500 to-teal-400 rounded-2xl p-4 text-white shadow-md flex items-center justify-between">
                <div>
                    <span class="bg-white/20 text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold">Yangi do'kon</span>
                    <h2 class="text-lg font-bold mt-1">Bepul yetkazib berish!</h2>
                    <p class="text-xs opacity-90 mt-0.5">50 000 so'mdan yuqori xaridlarga</p>
                </div>
                <div class="text-3xl bg-white/20 p-3 rounded-2xl">🚚</div>
            </div>
        </div>

        <!-- Mahsulotlar ro'yxati -->
        <div id="productsGrid" class="grid grid-cols-2 gap-3 mt-4">
            <!-- JavaScript orqali to'ldiriladi -->
        </div>
    </main><!-- Savatcha tugmasi / Paneli -->
    <div id="cartModal" class="fixed inset-0 bg-black/50 z-50 hidden flex items-end">
        <div class="bg-white w-full rounded-t-3xl p-5 max-h-[80vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-lg">Buyurtmangiz</h3>
                <button onclick="closeCart()" class="text-gray-400 hover:text-gray-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <div id="cartItems" class="space-y-3 mb-4">
                <!-- Savatcha elementlari -->
            </div>
            <div class="border-t pt-3 flex justify-between items-center mb-4">
                <span class="text-gray-500 text-sm">Jami summa:</span>
                <span id="cartTotal" class="font-bold text-lg text-emerald-600">0 so'm</span>
            </div>
            <button onclick="checkout()" class="w-full bg-emerald-600 text-white py-3 rounded-xl font-bold text-sm shadow-lg shadow-emerald-600/30">Buyurtmani rasmiylashtirish</button>
        </div>
    </div>

    <script>
        let products = [
            { id: 1, name: "Medovik torti (1 kg)", price: 85000, category: "shirinlik", emoji: "🍯", desc: "Tabiiy asal va qaymoqli" },
            { id: 2, name: "Shokoladli brauni", price: 24000, category: "shirinlik", emoji: "🍫", desc: "Noyob shokoladli shirinlik" },
            { id: 3, name: "Qaymoq (400 gr)", price: 22000, category: "masalliq", emoji: "🥛", desc: "Tabiiy uy qaymog'i" },
            { id: 4, name: "Sariyog' (200 gr)", price: 26000, category: "masalliq", emoji: "🧈", desc: "Yuqori sifatli sariyog'" },
            { id: 5, name: "Qulupnay (1 kg)", price: 38000, category: "meva", emoji: "🍓", desc: "Yangi uzilgan shirin qulupnay" },
            { id: 6, name: "Banan (1 kg)", price: 23000, category: "meva", emoji: "🍌", desc: "Ekvador bananlari" },
            { id: 7, name: "Tabiiy olma sharbati 1L", price: 14000, category: "ichimlik", emoji: "🧃", desc: "100% tabiiy olma sharbati" },
            { id: 8, name: "Gazsiz suv 1.5L", price: 4000, category: "ichimlik", emoji: "💧", desc: "Tog' buloq suvi" }
        ];

        let cart = {};
        let currentCategory = 'all';

        function formatPrice(num) {
            return num.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ") + " so'm";
        }

        function renderProducts(items) {
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = '';
            items.forEach(p => {
                grid.innerHTML += 
                    <div class="bg-white p-3 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
                        <div>
                            <div class="text-3xl mb-2 bg-gray-50 p-3 rounded-xl text-center">${p.emoji}</div>
                            <h4 class="font-bold text-sm leading-tight">${p.name}</h4>
                            <p class="text-xs text-gray-400 mt-1">${p.desc}</p>
                        </div>
                        <div class="mt-4 flex items-center justify-between">
                            <span class="font-extrabold text-sm text-emerald-600">${formatPrice(p.price)}</span>
                            <button onclick="addToCart(${p.id})" class="bg-emerald-50 text-emerald-600 w-8 h-8 rounded-xl flex items-center justify-center font-bold hover:bg-emerald-600 hover:text-white transition">+</button>
                        </div>
                    </div>
                ;
            });
        }

        function setCategory(cat, btn) {
            currentCategory = cat;
            document.querySelectorAll('.cat-btn').forEach(b => {
                b.classList.remove('bg-emerald-500', 'text-white');
                b.classList.add('bg-gray-100', 'text-gray-700');
            });
            btn.classList.remove('bg-gray-100', 'text-gray-700');
            btn.classList.add('bg-emerald-500', 'text-white');
            filterProducts();
        }function filterProducts() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            const filtered = products.filter(p => {
                const matchesCat = currentCategory === 'all' || p.category === currentCategory;
                const matchesQuery = p.name.toLowerCase().includes(query);
                return matchesCat && matchesQuery;
            });
            renderProducts(filtered);
        }

        function addToCart(id) {
            cart[id] = (cart[id] || 0) + 1;
            updateCartUI();
        }

        function updateCartUI() {
            const badge = document.getElementById('cartBadge');
            const totalItems = Object.values(cart).reduce((a, b) => a + b, 0);
            if (totalItems > 0) {
                badge.innerText = totalItems;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }

        function openCart() {
            const modal = document.getElementById('cartModal');
            const container = document.getElementById('cartItems');
            const totalEl = document.getElementById('cartTotal');
            container.innerHTML = '';
            let total = 0;

            for (let id in cart) {
                if (cart[id] > 0) {
                    const p = products.find(item => item.id == id);
                    total += p.price * cart[id];
                    container.innerHTML += 
                        <div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl">
                            <div>
                                <h4 class="font-bold text-sm">${p.name}</h4>
                                <p class="text-xs text-gray-500">${formatPrice(p.price)} x ${cart[id]}</p>
                            </div>
                            <div class="flex items-center space-x-2">
                                <button onclick="changeQty(${id}, -1)" class="bg-gray-200 w-7 h-7 rounded-lg font-bold">-</button>
                                <span class="text-sm font-bold">${cart[id]}</span>
                                <button onclick="changeQty(${id}, 1)" class="bg-emerald-600 text-white w-7 h-7 rounded-lg font-bold">+</button>
                            </div>
                        </div>
                    ;
                }
            }
            totalEl.innerText = formatPrice(total);
            modal.classList.remove('hidden');
        }

        function closeCart() {
            document.getElementById('cartModal').classList.add('hidden');
        }

        function changeQty(id, delta) {
            cart[id] = (cart[id] || 0) + delta;
            if (cart[id] <= 0) delete cart[id];
            openCart();
            updateCartUI();
        }

        function checkout() {
            alert("Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.");
            cart = {};
            closeCart();
            updateCartUI();
        }

        renderProducts(products);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return html_content
