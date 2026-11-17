import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

def load_products():
    try:
        df = pd.read_excel("products.xlsx")
        df = df.fillna("")
        products = []
        for idx, row in df.iterrows():
            products.append({
                "id": idx + 1,
                "name": str(row.get("name", "Nomsiz mahsulot")),
                "price": int(row.get("price", 0)) if str(row.get("price", "")).isdigit() else 0,
                "stock": int(row.get("stock", 0)) if str(row.get("stock", "")).isdigit() else 0,
                "category": str(row.get("category", "Boshqa")),
                "image": str(row.get("image", ""))
            })
        return products
    except Exception as e:
        print("Excel o'qishda xatolik:", e)
        return []

@app.get("/manifest.json")
async def get_manifest():
    return JSONResponse({
        "name": "Truzde",
        "short_name": "Truzde",
        "description": "Truzde onlayn do'koni",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#059669",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })

@app.get("/api/products")
async def get_products():
    return load_products()

html_content = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Truzde</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#059669">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50 text-gray-800 pb-24">

    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center space-x-2.5">
                <div class="bg-emerald-600 text-white w-10 h-10 rounded-xl flex items-center justify-center font-extrabold text-lg">TR</div>
                <div>
                    <h1 class="font-bold text-lg leading-none">Truzde</h1>
                    <p class="text-xs text-gray-500 mt-1">Onlayn do'kon</p>
                </div>
            </div>
            <button onclick="openCart()" class="bg-emerald-50 text-emerald-600 px-3.5 py-2.5 rounded-xl relative flex items-center gap-2 font-semibold text-sm">
                <i class="fa-solid fa-cart-shopping"></i>
                <span id="cartBadge" class="bg-emerald-600 text-white text-xs px-2 py-0.5 rounded-full hidden">0</span>
            </button>
        </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 mt-4">
        <div class="relative">
            <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3.5 text-gray-400 text-sm"></i>
            <input type="text" id="searchInput" oninput="filterProducts()" placeholder="Mahsulot izlash..." class="w-full bg-white border border-gray-200 text-sm rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:border-emerald-500">
        </div>

        <div id="categoryBar" class="flex gap-2 overflow-x-auto pb-2 mt-3"></div>
        <div id="productsGrid" class="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3"></div>
    </main>

    <div id="cartModal" class="fixed inset-0 bg-black/50 z-50 hidden flex items-end justify-center">
        <div class="bg-white w-full max-w-3xl rounded-t-3xl p-5 max-h-[85vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-lg">Savatcha</h3><button onclick="closeCart()" class="text-gray-400 hover:text-gray-700 p-1"><i class="fa-solid fa-xmark text-xl"></i></button>
            </div>
            <div id="cartItems" class="space-y-3 mb-4"></div>
            <div class="border-t pt-3 flex justify-between items-center mb-4">
                <span class="text-gray-500 text-sm">Jami summa:</span>
                <span id="cartTotal" class="font-extrabold text-lg text-emerald-600">0 so'm</span>
            </div>
            <button onclick="checkout()" class="w-full bg-emerald-600 text-white py-3.5 rounded-xl font-bold text-sm">Buyurtma berish</button>
        </div>
    </div>

    <script>
        let products = [];
        let cart = {};
        let currentCategory = 'all';

        async function init() {
            const res = await fetch('/api/products');
            products = await res.json();
            renderCategories();
            filterProducts();
        }

        function formatPrice(num) {
            return num.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ") + " so'm";
        }

        function renderCategories() {
            const bar = document.getElementById('categoryBar');
            const cats = ['all', ...new Set(products.map(p => p.category).filter(Boolean))];
            bar.innerHTML = cats.map(c => {
                const label = c === 'all' ? 'Barchasi' : c;
                const activeClass = c === currentCategory ? 'bg-emerald-600 text-white' : 'bg-white text-gray-700 border border-gray-200';
                return <button onclick="setCategory('${c}')" class="${activeClass} px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">${label}</button>;
            }).join('');
        }

        function setCategory(cat) {
            currentCategory = cat;
            renderCategories();
            filterProducts();
        }

        function filterProducts() {
            const q = document.getElementById('searchInput').value.toLowerCase();
            const filtered = products.filter(p => {
                const matchCat = currentCategory === 'all' || p.category === currentCategory;
                const matchName = p.name.toLowerCase().includes(q);
                return matchCat && matchName;
            });
            renderProducts(filtered);
        }

        function renderProducts(items) {
            const grid = document.getElementById('productsGrid');
            if (items.length === 0) {
                grid.innerHTML = '<p class="col-span-full text-center text-gray-400 py-10 text-sm">Mahsulot topilmadi</p>';
                return;
            }
            grid.innerHTML = items.map(p => {
                const isOutOfStock = p.stock <= 0;
                const imgHtml = p.image 
                    ? <img src="${p.image}" alt="${p.name}" class="w-full h-28 object-cover rounded-xl mb-2 bg-gray-100">
                    : <div class="w-full h-28 bg-gray-100 rounded-xl mb-2 flex items-center justify-center text-gray-400 text-xs">Rasm yo'q</div>;
                
                const btnHtml = isOutOfStock
                    ? <span class="text-xs font-semibold text-red-500 bg-red-50 px-2.5 py-1.5 rounded-lg">Tugagan</span>
                    : <button onclick="addToCart(${p.id})" class="bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white w-9 h-9 rounded-xl flex items-center justify-center font-bold transition">+</button>;

                return `
                    <div class="bg-white p-3 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between ${isOutOfStock ? 'opacity-70' : ''}">
                        <div>
                            ${imgHtml}
                            <h4 class="font-bold text-sm leading-snug line-clamp-2">${p.name}</h4><p class="text-[11px] text-gray-400 mt-1">Qoldiq: ${p.stock} ta/kg</p>
                        </div>
                        <div class="mt-3 flex items-center justify-between">
                            <span class="font-extrabold text-sm text-emerald-600">${formatPrice(p.price)}</span>
                            ${btnHtml}
                        </div>
                    </div>
                ;
            }).join('');
        }

        function addToCart(id) {
            const p = products.find(item => item.id === id);
            const currentQty = cart[id] || 0;
            if (currentQty >= p.stock) {
                alert(Kechirasiz, "${p.name}" omborda atigi ${p.stock} ta/kg qolgan!);
                return;
            }
            cart[id] = currentQty + 1;
            updateCartUI();
        }

        function updateCartUI() {
            const badge = document.getElementById('cartBadge');
            const total = Object.values(cart).reduce((a, b) => a + b, 0);
            if (total > 0) {
                badge.innerText = total;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }

        function openCart() {
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
            document.getElementById('cartModal').classList.remove('hidden');
        }

        function closeCart() {
            document.getElementById('cartModal').classList.add('hidden');
        }

        function changeQty(id, delta) {
            const p = products.find(item => item.id == id);
            const newQty = (cart[id] || 0) + delta;
            if (newQty > p.stock) {
                alert(Omborda atigi ${p.stock} ta/kg mavjud!`);
                return;
            }
            cart[id] = newQty;
            if (cart[id] <= 0) delete cart[id];
            openCart();
            updateCartUI();
        }

        function checkout() {
            if (Object.keys(cart).length === 0) return;
            alert("Buyurtmangiz qabul qilindi! Tez orada bog'lanamiz.");
            cart = {};
            closeCart();
            updateCartUI();
        }

        init();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return html_content
