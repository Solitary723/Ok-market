import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()


def load_products():
    try:
        # Fayl yo'lini aniq ko'rsatamiz
        file_path = "products.xlsx"
        if not os.path.exists(file_path):
            print("Excel fayl topilmadi!")
            return []
            
        df = pd.read_excel(file_path)
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
    except Exception as e:
        print("Excel o'qishda xatolik:", e)
        return []

@app.get("/manifest.json")
async def get_manifest():
    return JSONResponse({
        "name": "Truzde",
        "short_name": "Truzde",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f3f4f6",
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
    <style>
        .brand-tr { color: #00824b; }
        .brand-de { color: #047857; }
        .bg-brand { background-color: #00824b; }
    </style>
</head>
<body class="bg-gray-100 text-gray-900 pb-28">
    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center space-x-1.5">
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
        <div id="categoryBar" class="flex gap-2 overflow-x-auto px-4 pb-3 scrollbar-none"></div>
    </header>

    <!-- Main Content -->
    <main class="max-w-md mx-auto px-3 mt-3">
        <div id="productsGrid" class="grid grid-cols-2 gap-2.5"></div>
    </main>

    <!-- Cart Modal -->
    <div id="cartModal" class="fixed inset-0 bg-black/50 z-50 hidden flex items-end justify-center">
        <div class="bg-white w-full max-w-md rounded-t-3xl p-4 max-h-[85vh] overflow-y-auto"><div class="flex justify-between items-center mb-4">
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
        let products = [], cart = {}, currentCategory = 'Barchasi';
        async function init() {
            try {
                const res = await fetch('/api/products');
                products = await res.json();
                renderCategories();
                filterProducts();
            } catch (e) {
                console.error("Xatolik:", e);
            }
        }
        function fmt(n) { return n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ") + " so'm"; }
        
        function renderCategories() {
            const bar = document.getElementById('categoryBar');
            const cats = ['Barchasi', ...new Set(products.map(p => p.category).filter(Boolean))];
            bar.innerHTML = cats.map(c => 
                <button onclick="setCategory('${c}')" class="${c === currentCategory ? 'bg-emerald-600 text-white' : 'bg-white text-gray-700 border border-gray-200'} px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap shadow-xs">${c}</button>
            ).join('');
        }
        
        function setCategory(c) { currentCategory = c; renderCategories(); filterProducts(); }
        
        function filterProducts() {
            const q = document.getElementById('searchInput').value.toLowerCase();
            const filtered = products.filter(p => (currentCategory === 'Barchasi' || p.category === currentCategory) && p.name.toLowerCase().includes(q));
            renderProducts(filtered);
        }
        
        function renderProducts(items) {
            const grid = document.getElementById('productsGrid');
            if (!items.length) {
                grid.innerHTML = '<div class="col-span-2 text-center py-16 text-gray-400 text-xs">Mahsulotlar topilmadi yoki Excel fayli bo‘sh</div>';
                return;
            }
            grid.innerHTML = items.map(p => 
                <div class="bg-white p-2.5 rounded-2xl shadow-xs border border-gray-100 flex flex-col justify-between">
                    <div>
                        ${p.image ? <img src="${p.image}" class="w-full h-32 object-cover rounded-xl mb-2"> : <div class="w-full h-32 bg-gray-50 rounded-xl mb-2 flex items-center justify-center text-gray-300 text-xs"><i class="fa-solid fa-image text-xl"></i></div>}
                        <h4 class="font-medium text-xs text-gray-800 line-clamp-2 h-8">${p.name}</h4>
                    </div>
                    <div class="mt-2">
                        <div class="font-black text-xs text-emerald-700 mb-2">${fmt(p.price)}</div>
                        ${p.stock <= 0 ? '<span class="text-[10px] text-red-500 font-semibold">Tugagan</span>' : <button onclick="addToCart(${p.id})" class="w-full bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white py-1.5 rounded-xl text-xs font-bold transition">Savatga</button>}
                    </div>
                </div>
            ).join('');
        }
        
        function addToCart(id) {
            const p = products.find(i => i.id === id);
            if ((cart[id] || 0) >= p.stock) { alert('Omborda yetarli miqdor yo‘q!'); return; }cart[id] = (cart[id] || 0) + 1;
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
                c.innerHTML += <div class="flex justify-between items-center bg-gray-50 p-2.5 rounded-xl"><div><h4 class="font-bold text-xs">${p.name}</h4><p class="text-[11px] text-gray-500">${fmt(p.price)} x ${cart[id]}</p></div><div class="flex items-center gap-2"><button onclick="ch(${id},-1)" class="bg-gray-200 w-6 h-6 rounded-lg text-xs font-bold">-</button><span class="text-xs font-bold">${cart[id]}</span><button onclick="ch(${id},1)" class="bg-emerald-600 text-white w-6 h-6 rounded-lg text-xs font-bold">+</button></div></div>;
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
        
        function checkout() { 
            alert('Buyurtmangiz qabul qilindi!'); 
            cart = {}; 
            closeCart(); 
            updateCart(); 
        }
        
        init();
    </script>
</body>
</html>
    """
