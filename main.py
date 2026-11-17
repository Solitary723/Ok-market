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
                "name": str(row.get("name", "Nomsiz")),
                "price": int(row.get("price", 0)) if str(row.get("price", "")).isdigit() else 0,
                "stock": int(row.get("stock", 0)) if str(row.get("stock", "")).isdigit() else 0,
                "category": str(row.get("category", "Boshqa")),
                "image": str(row.get("image", ""))
            })
        return products
    except Exception as e:
        print("Xatolik:", e)
        return []

@app.get("/manifest.json")
async def get_manifest():
    return JSONResponse({
        "name": "Truzde",
        "short_name": "Truzde",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#059669",
        "icons": [{
            "src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png",
            "sizes": "512x512",
            "type": "image/png"
        }]
    })

@app.get("/api/products")
async def get_products():
    return load_products()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
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
            <div class="flex items-center space-x-2">
                <div class="bg-emerald-600 text-white w-10 h-10 rounded-xl flex items-center justify-center font-extrabold">TR</div>
                <h1 class="font-bold text-lg">Truzde</h1>
            </div>
            <button onclick="openCart()" class="bg-emerald-50 text-emerald-600 px-3 py-2 rounded-xl relative font-semibold text-sm">
                <i class="fa-solid fa-cart-shopping"></i>
                <span id="cartBadge" class="bg-emerald-600 text-white text-xs px-1.5 py-0.5 rounded-full hidden absolute -top-1 -right-1">0</span>
            </button>
        </div>
    </header>
    <main class="max-w-3xl mx-auto px-4 mt-4">
        <input type="text" id="searchInput" oninput="filterProducts()" placeholder="Mahsulot izlash..." class="w-full bg-white border border-gray-200 text-sm rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500">
        <div id="categoryBar" class="flex gap-2 overflow-x-auto pb-2 mt-3"></div>
        <div id="productsGrid" class="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3"></div>
    </main>
    <div id="cartModal" class="fixed inset-0 bg-black/50 z-50 hidden flex items-end justify-center">
        <div class="bg-white w-full max-w-3xl rounded-t-3xl p-5 max-h-[85vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-lg">Savatcha</h3>
                <button onclick="closeCart()" class="text-gray-400 text-xl"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div id="cartItems" class="space-y-3 mb-4"></div>
            <div class="border-t pt-3 flex justify-between items-center mb-4">
                <span class="text-gray-500 text-sm">Jami:</span><span id="cartTotal" class="font-extrabold text-lg text-emerald-600">0 so'm</span>
            </div>
            <button onclick="checkout()" class="w-full bg-emerald-600 text-white py-3 rounded-xl font-bold">Buyurtma berish</button>
        </div>
    </div>
    <script>
        let products = [], cart = {}, currentCategory = 'all';
        async function init() {
            const res = await fetch('/api/products');
            products = await res.json();
            renderCategories();
            filterProducts();
        }
        function fmt(n) { return n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ") + " so'm"; }
        function renderCategories() {
            const bar = document.getElementById('categoryBar');
            const cats = ['all', ...new Set(products.map(p => p.category).filter(Boolean))];
            bar.innerHTML = cats.map(c => <button onclick="setCategory('${c}')" class="${c === currentCategory ? 'bg-emerald-600 text-white' : 'bg-white text-gray-700 border'} px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap">${c === 'all' ? 'Barchasi' : c}</button>).join('');
        }
        function setCategory(c) { currentCategory = c; renderCategories(); filterProducts(); }
        function filterProducts() {
            const q = document.getElementById('searchInput').value.toLowerCase();
            renderProducts(products.filter(p => (currentCategory === 'all' || p.category === currentCategory) && p.name.toLowerCase().includes(q)));
        }
        function renderProducts(items) {
            const grid = document.getElementById('productsGrid');
            if (!items.length) { grid.innerHTML = '<p class="col-span-full text-center text-gray-400 py-10 text-sm">Topilmadi</p>'; return; }
            grid.innerHTML = items.map(p => 
                <div class="bg-white p-3 rounded-2xl shadow-sm border flex flex-col justify-between ${p.stock <= 0 ? 'opacity-70' : ''}">
                    <div>
                        ${p.image ? <img src="${p.image}" class="w-full h-28 object-cover rounded-xl mb-2"> : <div class="w-full h-28 bg-gray-100 rounded-xl mb-2 flex items-center justify-center text-gray-400 text-xs">Rasm yo'q</div>}
                        <h4 class="font-bold text-sm line-clamp-2">${p.name}</h4>
                        <p class="text-[11px] text-gray-400 mt-1">Qoldiq: ${p.stock}</p>
                    </div>
                    <div class="mt-3 flex items-center justify-between">
                        <span class="font-extrabold text-sm text-emerald-600">${fmt(p.price)}</span>
                        ${p.stock <= 0 ? '<span class="text-xs text-red-500 font-semibold">Tugagan</span>' : <button onclick="addToCart(${p.id})" class="bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white w-8 h-8 rounded-xl font-bold flex items-center justify-center">+</button>}
                    </div>
                </div>
            ).join('');
        }
        function addToCart(id) {
            const p = products.find(i => i.id === id);
            if ((cart[id] || 0) >= p.stock) { alert('Omborda yetarli emas!'); return; }
            cart[id] = (cart[id] || 0) + 1;
            updateCart();
        }
        function updateCart() {
            const total = Object.values(cart).reduce((a, b) => a + b, 0);
            const b = document.getElementById('cartBadge');
            b.innerText = total;
            total > 0 ? b.classList.remove('hidden') : b.classList.add('hidden');
        }
        function openCart() {
            const c = document.getElementById('cartItems'); c.innerHTML = ''; let sum = 0;
            for (let id in cart) {
                const p = products.find(i => i.id == id);
                sum += p.price * cart[id];
                c.innerHTML += `<div class="flex justify-between items-center bg-gray-50 p-3 rounded-xl"><div><h4 class="font-bold text-sm">${p.name}</h4><p class="text-xs text-gray-500">${fmt(p.price)} x ${cart[id]}</p></div><div class="flex items-center gap-2"><button onclick="ch(${id},-1)" class="bg-gray-200w-7 h-7 rounded-lg font-bold">-</button><span class="text-sm font-bold">${cart[id]}</span><button onclick="ch(${id},1)" class="bg-emerald-600 text-white w-7 h-7 rounded-lg font-bold">+</button></div></div>`;
            }
            document.getElementById('cartTotal').innerText = fmt(sum);
            document.getElementById('cartModal').classList.remove('hidden');
        }
        function closeCart() { document.getElementById('cartModal').classList.add('hidden'); }
        function ch(id, d) {
            cart[id] = (cart[id] || 0) + d;
            if (cart[id] <= 0) delete cart[id];
            openCart(); updateCart();
        }
        function checkout() { alert('Buyurtma qabul qilindi!'); cart = {}; closeCart(); updateCart(); }
        init();
    </script>
</body>
</html>
    """
