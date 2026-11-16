from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI()

orders_db = []

class OrderItem(BaseModel):
    name: str
    price: int
    qty: int

class Order(BaseModel):
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]
    total: int

@app.post("/api/order")
async def create_order(order: Order):
    order_data = order.dict()
    order_data["id"] = len(orders_db) + 1
    order_data["time"] = datetime.datetime.now().strftime("%H:%M, %d.%m.%Y")
    orders_db.append(order_data)
    return {"status": "success", "order_id": order_data["id"]}

@app.get("/api/orders")
async def get_orders():
    return orders_db

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OK Market — Oziq-ovqat do‘koni</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f4f6f5; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="pb-24">

    <!-- Yuqori Header -->
    <header class="sticky top-0 z-40 bg-white shadow-sm px-4 py-3">
        <div class="max-w-3xl mx-auto flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
                <div class="w-9 h-9 rounded-xl bg-emerald-500 flex items-center justify-center text-white font-bold text-lg shadow-sm">OK</div>
                <div>
                    <h1 class="font-extrabold text-lg text-gray-800 leading-none">OK Market</h1>
                    <span class="text-[11px] text-emerald-600 font-medium">Tezkor yetkazib berish</span>
                </div>
            </div>
            
            <button onclick="openAdminModal()" class="text-xs bg-emerald-50 text-emerald-700 px-3 py-2 rounded-xl font-semibold border border-emerald-200 active:scale-95 transition">
                <i class="fa-solid fa-clipboard-list mr-1"></i> Buyurtmalar
            </button>
        </div>

        <!-- Qidiruv satri -->
        <div class="max-w-3xl mx-auto mt-3 relative">
            <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-gray-400 text-sm"></i>
            <input type="text" id="searchInput" oninput="filterProducts()" placeholder="Mahsulot va tovarlarni izlash..." 
                   class="w-full bg-gray-100 text-sm rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:bg-white transition">
        </div>

        <!-- Kategoriyalar -->
        <div class="max-w-3xl mx-auto mt-3 flex gap-2 overflow-x-auto no-scrollbar pb-1" id="categoryBar">
            <button onclick="setCategory('all', this)" class="cat-btn active bg-emerald-500 text-white px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">Barchasi</button>
            <button onclick="setCategory('shirinlik', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">🍰 Shirinliklar</button>
            <button onclick="setCategory('masalliq', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">🧈 Masalliqlar</button>
            <button onclick="setCategory('ichimlik', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">🥤 Ichimliklar</button><button onclick="setCategory('meva', this)" class="cat-btn bg-gray-100 text-gray-700 px-4 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition">🍓 Meva-sabzavot</button>
        </div>
    </header>

    <!-- Aksiya Banner -->
    <div class="max-w-3xl mx-auto px-4 mt-4">
        <div class="bg-gradient-to-r from-emerald-500 to-teal-400 rounded-2xl p-4 text-white shadow-md flex items-center justify-between">
            <div>
                <span class="bg-white/20 text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold">Yangi do‘kon</span>
                <h2 class="text-lg font-bold mt-1">Bepul yetkazib berish!</h2>
                <p class="text-xs text-emerald-50 mt-0.5">50 000 so‘mdan yuqori xaridlarga</p>
            </div>
            <div class="text-4xl">🛍️</div>
        </div>
    </div>

    <!-- Mahsulotlar Grid -->
    <main class="max-w-3xl mx-auto px-4 mt-4">
        <div id="productsGrid" class="grid grid-cols-2 sm:grid-cols-3 gap-3"></div>
    </main>

    <!-- Pastki Savat Paneli -->
    <div id="bottomCartBar" class="hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-3 z-40 shadow-lg">
        <div class="max-w-3xl mx-auto flex items-center justify-between">
            <div>
                <span class="text-xs text-gray-500 block">Jami summa:</span>
                <span id="barTotalPrice" class="text-lg font-extrabold text-gray-900">0 so‘m</span>
            </div>
            <button onclick="openCartModal()" class="bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-6 py-3 rounded-xl shadow-md active:scale-95 transition flex items-center gap-2">
                <span>Savatga o‘tish</span>
                <span id="barBadge" class="bg-white text-emerald-600 text-xs font-extrabold px-2 py-0.5 rounded-full">0</span>
            </button>
        </div>
    </div>

    <!-- Savat va Buyurtma Modali -->
    <div id="cartModal" class="hidden fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center">
        <div class="bg-white w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-5 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3">
                <h3 class="text-lg font-bold text-gray-800">🛒 Sizning savatingiz</h3>
                <button onclick="closeCartModal()" class="w-8 h-8 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <div id="cartItemsList" class="divide-y my-3 max-h-60 overflow-y-auto"></div>

            <div class="bg-emerald-50 p-3 rounded-xl flex justify-between items-center mb-4">
                <span class="font-semibold text-gray-700">To‘lov summasi:</span>
                <span id="modalTotalPrice" class="text-lg font-extrabold text-emerald-600">0 so‘m</span>
            </div>

            <form id="orderForm" onsubmit="submitOrder(event)" class="space-y-3">
                <div>
                    <label class="text-xs font-semibold text-gray-600">Ismingiz</label>
                    <input type="text" id="custName" required placeholder="Masalan: Jasur" class="w-full mt-1 border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-emerald-500">
                </div>
                <div>
                    <label class="text-xs font-semibold text-gray-600">Telefon raqamingiz</label>
                    <input type="tel" id="custPhone" required placeholder="+998 90 123 45 67" class="w-full mt-1 border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-emerald-500">
                </div>
                <div>
                    <label class="text-xs font-semibold text-gray-600">Yetkazib berish manzili</label><input type="text" id="custAddress" required placeholder="Ko‘cha, uy raqami yoki mo‘ljal" class="w-full mt-1 border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-emerald-500">
                </div>
                <button type="submit" class="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-3.5 rounded-xl shadow-md transition">
                    Buyurtmani tasdiqlash
                </button>
            </form>
        </div>
    </div>

    <!-- Admin Buyurtmalar Modali -->
    <div id="adminModal" class="hidden fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center">
        <div class="bg-white w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-5 max-h-[85vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3">
                <h3 class="text-lg font-bold text-gray-800">📋 Kelgan buyurtmalar</h3>
                <button onclick="closeAdminModal()" class="w-8 h-8 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div id="adminOrdersList" class="space-y-3 mt-3"></div>
        </div>
    </div>

    <script>
        const products = [
            { id: 1, name: "Medovik torti (1 kg)", price: 85000, category: "shirinlik", emoji: "🍰", desc: "Asalli yumshoq krem bilan" },
            { id: 2, name: "Shokoladli brauni", price: 24000, category: "shirinlik", emoji: "🍫", desc: "Belgiya shokoladidan" },
            { id: 3, name: "Qaymoq (400 gr)", price: 22000, category: "masalliq", emoji: "🥛", desc: "Tabiiy 35% li qaymoq" },
            { id: 4, name: "Sariyog‘ (200 gr)", price: 26000, category: "masalliq", emoji: "🧈", desc: "82.5% oliy nav" },
            { id: 5, name: "Qulupnay (1 kg)", price: 38000, category: "meva", emoji: "🍓", desc: "Yangi uzilgan shirin" },
            { id: 6, name: "Banan (1 kg)", price: 23000, category: "meva", emoji: "🍌", desc: "Ekvador bananlari" },
            { id: 7, name: "Tabiiy olma sharbati 1L", price: 14000, category: "ichimlik", emoji: "🧃", desc: "Shakarsiz tabiiy sharbat" },
            { id: 8, name: "Gazsiz suv 1.5L", price: 4000, category: "ichimlik", emoji: "💧", desc: "Tog‘ buloq suvi" }
        ];

        let cart = {};
        let currentCategory = 'all';

        function formatPrice(num) {
            return num.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ") + " so‘m";
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
        }

        function filterProducts() {
            const q = document.getElementById('searchInput').value.toLowerCase();
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = '';

            const filtered = products.filter(p => {
                const matchCat = currentCategory === 'all' || p.category === currentCategory;
                const matchSearch = p.name.toLowerCase().includes(q) || p.desc.toLowerCase().includes(q);
                return matchCat && matchSearch;
            });

            filtered.forEach(p => {
                const qty = cart[p.id] || 0;
                const card = document.createElement('div');
                card.className = "bg-white rounded-2xl p-3 shadow-sm border border-gray-100 flex flex-col justify-between";
                card.innerHTML = `
                    <div><div class="h-28 bg-emerald-50/70 rounded-xl flex items-center justify-center text-5xl mb-2.5">
                            ${p.emoji}
                        </div>
                        <div class="font-bold text-emerald-600 text-sm">${formatPrice(p.price)}</div>
                        <h3 class="font-semibold text-gray-800 text-xs sm:text-sm mt-0.5 line-clamp-1">${p.name}</h3>
                        <p class="text-[11px] text-gray-400 mt-0.5 line-clamp-1">${p.desc}</p>
                    </div>
                    <div class="mt-3">
                        ${qty === 0 ? 
                            <button onclick="addToCart(${p.id})" class="w-full bg-emerald-50 hover:bg-emerald-500 hover:text-white text-emerald-700 font-semibold text-xs py-2 rounded-xl transition flex items-center justify-center gap-1.5">
                                <i class="fa-solid fa-cart-plus"></i> Savatga
                            </button>
                         : 
                            <div class="flex items-center justify-between bg-emerald-500 text-white rounded-xl py-1.5 px-3">
                                <button onclick="changeQty(${p.id}, -1)" class="w-6 h-6 font-bold text-base flex items-center justify-center">−</button>
                                <span class="font-bold text-xs">${qty}</span>
                                <button onclick="changeQty(${p.id}, 1)" class="w-6 h-6 font-bold text-base flex items-center justify-center">+</button>
                            </div>
                        }
                    </div>
                ;
                grid.appendChild(card);
            });
        }

        function addToCart(id) {
            cart[id] = 1;
            updateUI();
        }

        function changeQty(id, delta) {
            cart[id] = (cart[id] || 0) + delta;
            if (cart[id] <= 0) delete cart[id];
            updateUI();
        }

        function updateUI() {
            filterProducts();
            let totalQty = 0;
            let totalPrice = 0;

            for (let id in cart) {
                const p = products.find(item => item.id == id);
                if (p) {
                    totalQty += cart[id];
                    totalPrice += p.price * cart[id];
                }
            }

            const bar = document.getElementById('bottomCartBar');
            if (totalQty > 0) {
                bar.classList.remove('hidden');
                document.getElementById('barTotalPrice').innerText = formatPrice(totalPrice);
                document.getElementById('barBadge').innerText = totalQty;
            } else {
                bar.classList.add('hidden');
            }
        }

        function openCartModal() {
            const list = document.getElementById('cartItemsList');
            list.innerHTML = '';
            let total = 0;

            for (let id in cart) {
                const p = products.find(item => item.id == id);
                const sub = p.price * cart[id];
                total += sub;
                list.innerHTML += 
                    <div class="py-2.5 flex items-center justify-between">
                        <div>
                            <div class="font-semibold text-sm text-gray-800">${p.emoji} ${p.name}</div>
                            <div class="text-xs text-gray-500">${formatPrice(p.price)} x ${cart[id]}</div>
                        </div>
                        <div class="font-bold text-sm text-emerald-600">${formatPrice(sub)}</div>
                    </div>
                `;
            }

            document.getElementById('modalTotalPrice').innerText = formatPrice(total);
            document.getElementById('cartModal').classList.remove('hidden');
        }

        function closeCartModal() {
            document.getElementById('cartModal').classList.add('hidden');
        }async function submitOrder(e) {
            e.preventDefault();
            let items = [];
            let total = 0;
            for (let id in cart) {
                const p = products.find(item => item.id == id);
                items.push({ name: p.name, price: p.price, qty: cart[id] });
                total += p.price * cart[id];
            }

            const payload = {
                customer_name: document.getElementById('custName').value,
                phone: document.getElementById('custPhone').value,
                address: document.getElementById('custAddress').value,
                items: items,
                total: total
            };

            const res = await fetch('/api/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                alert("✅ Buyurtmangiz qabul qilindi! Buyurtma raqami: #" + data.order_id);
                cart = {};
                closeCartModal();
                updateUI();
            }
        }

        async function openAdminModal() {
            const res = await fetch('/api/orders');
            const orders = await res.json();
            const list = document.getElementById('adminOrdersList');
            list.innerHTML = '';

            if (orders.length === 0) {
                list.innerHTML = '<p class="text-center text-gray-400 text-sm py-6">Hozircha buyurtmalar yo‘q</p>';
            } else {
                orders.reverse().forEach(o => {
                    const itemsHtml = o.items.map(i => <span class="text-xs bg-gray-100 px-2 py-0.5 rounded">${i.name} (${i.qty} ta)</span>).join(' ');
                    list.innerHTML += 
                        <div class="border border-gray-200 rounded-2xl p-3 bg-gray-50">
                            <div class="flex justify-between items-center">
                                <span class="font-bold text-emerald-600 text-sm">Buyurtma #${o.id}</span>
                                <span class="text-[11px] text-gray-400">${o.time}</span>
                            </div>
                            <div class="text-xs text-gray-800 font-semibold mt-1">👤 ${o.customer_name} | 📞 ${o.phone}</div>
                            <div class="text-xs text-gray-600 mt-0.5">📍 ${o.address}</div>
                            <div class="flex flex-wrap gap-1 mt-2">${itemsHtml}</div>
                            <div class="text-right font-extrabold text-sm text-gray-900 mt-2">Jami: ${formatPrice(o.total)}</div>
                        </div>
                    ;
                });
            }
            document.getElementById('adminModal').classList.remove('hidden');
        }

        function closeAdminModal() {
            document.getElementById('adminModal').classList.add('hidden');
        }

        filterProducts();
    </script>
</body>
</html>
"""