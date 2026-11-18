from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
import os

app = FastAPI()

def load_json_products():
    if os.path.exists("products.json"):
        try:
            with open("products.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return [
        {
            "id": 1,
            "name": "Olma Qizil",
            "price": 20000,
            "stock": 25,
            "category": "Mevalar",
            "image": "https://images.unsplash.com/photo-1560806887-1e4cd06bcd67?w=400"
        }
    ]

@app.get("/api/products")
def get_products():
    return load_json_products()

@app.head("/")
@app.get("/", response_class=HTMLResponse)
def read_root():
    products_json = json.dumps(load_json_products(), ensure_ascii=False)
    html = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Truzde</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .brand-tr { color: #00824b; }
        .brand-de { color: #047857; }
        .bg-brand { background-color: #00824b; }
    </style>
</head>
<body class="bg-gray-100 text-gray-900 pb-28">
    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center space-x-1">
                <span class="text-xl font-black brand-tr">Tr</span>
                <span class="text-xl font-bold brand-de">de</span>
            </div>
            <div class="flex-1 mx-3">
                <div class="relative">
                    <i class="fa-solid fa-magnifying-glass absolute left-3 top-3 text-gray-400 text-xs"></i>
                    <input type="text" id="searchInput" oninput="filterProducts()" placeholder="Mahsulotlarni qidirish..." class="w-full bg-gray-100 text-xs rounded-xl pl-9 pr-3 py-2.5 focus:outline-none focus:bg-white focus:ring-1 focus:ring-emerald-600">
                </div>
            </div>
            <button onclick="openCart()" class="bg-emerald-50 text-emerald-700 w-9 h-9 rounded-xl relative flex items-center justify-center font-bold">
                <i class="fa-solid fa-cart-shopping text-sm"></i>
                <span id="cartBadge" class="bg-emerald-600 text-white text-[10px] px-1.5 py-0.2 rounded-full hidden absolute -top-1 -right-1">0</span>
            </button>
        </div>
        <div id="categoryBar" class="flex gap-2 overflow-x-auto px-4 pb-3"></div>
    </header>

    <main class="max-w-md mx-auto px-3 mt-3">
        <div id="productsGrid" class="grid grid-cols-2 gap-2.5"></div>
    </main>

    <div id="cartModal" class="fixed inset-0 bg-black/50 z-50 hidden flex items-end justify-center">
        <div class="bg-white w-full max-w-md rounded-t-3xl p-4 max-h-[85vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-base">Savatcha</h3>
                <button onclick="closeCart()" class="text-gray-400 text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div id="cartItems" class="space-y-3 mb-4"></div>
            <div class="border-t pt-3 flex justify-between items-center mb-4">
                <span class="text-gray-500 text-sm">Jami summa:</span>
                <span id="cartTotal" class="font-black text-base text-emerald-700">0 so'm</span>
            </div>
            <button onclick="checkout()" class="w-full bg-brand text-white py-3 rounded-xl font-bold text-sm shadow-md">Buyurtma berish</button>
        </div>
    </div>

    <script>
        let products = PRODUCTS_DATA;
        let cart = {}, currentCategory = 'Barchasi';function fmt(n) { return n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ") + " so'm"; }
        
        function renderCategories() {
            const bar = document.getElementById('categoryBar');
            const cats = ['Barchasi', ...new Set(products.map(p => p.category).filter(Boolean))];
            bar.innerHTML = cats.map(c => 
                <button onclick="setCategory('${c}')" class="${c === currentCategory ? 'bg-emerald-600 text-white' : 'bg-white text-gray-700 border border-gray-200'} px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap">${c}</button>
            ).join('');
        }
        
        function setCategory(c) { 
            currentCategory = c; 
            renderCategories(); 
            filterProducts(); 
        }
        
        function filterProducts() {
            const q = document.getElementById('searchInput').value.toLowerCase();
            const filtered = products.filter(p => (currentCategory === 'Barchasi' || p.category === currentCategory) && p.name.toLowerCase().includes(q));
            renderProducts(filtered);
        }
        
        function renderProducts(items) {
            const grid = document.getElementById('productsGrid');
            if (!items || !items.length) {
                grid.innerHTML = '<div class="col-span-2 text-center py-16 text-gray-400 text-xs">Mahsulotlar topilmadi</div>';
                return;
            }
            grid.innerHTML = items.map(p => 
                <div class="bg-white p-2.5 rounded-2xl border border-gray-100 flex flex-col justify-between">
                    <div>
                        <img src="${p.image}" class="w-full h-32 object-cover rounded-xl mb-2">
                        <h4 class="font-medium text-xs text-gray-800 line-clamp-2">${p.name}</h4>
                    </div>
                    <div class="mt-2">
                        <div class="font-black text-xs text-emerald-700 mb-2">${fmt(p.price)}</div>
                        <button onclick="addToCart(${p.id})" class="w-full bg-emerald-50 text-emerald-700 py-1.5 rounded-xl text-xs font-bold">Savatga</button>
                    </div>
                </div>
            ).join('');
        }
        
        function addToCart(id) {
            cart[id] = (cart[id] || 0) + 1;
            updateCart();
            alert('Savatga qo\\'shildi!');
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
                c.innerHTML += <div class="flex justify-between items-center bg-gray-50 p-2.5 rounded-xl"><div><h4 class="font-bold text-xs">${p.name}</h4><p class="text-[11px] text-gray-500">${fmt(p.price)} x ${cart[id]}</p></div></div>;
            }
            document.getElementById('cartTotal').innerText = fmt(sum);
            document.getElementById('cartModal').classList.remove('hidden');
        }
        
        function closeCart() { document.getElementById('cartModal').classList.add('hidden'); }
        
        function checkout() { 
            alert('Buyurtmangiz qabul qilindi!'); 
            cart = {}; 
            closeCart(); 
            updateCart(); 
        }

        renderCategories();
        renderProducts(products);
    </script>
</body>
</html>
    """
    return html.replace("PRODUCTS_DATA", products_json)
