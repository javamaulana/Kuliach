from os import system as clear_cmd
from os import name as os_name
from os.path import exists
import time
import random

from termcolor import colored, cprint
import pygame

SAVE_FILE = "harvest_moon.txt"
MUSIC_FILE = "Harvest Moon_ Back to Nature  Spring  OST.mp3" 
INITIAL_MONEY = 10
INITIAL_APPLE_SEEDS = 3
INITIAL_LAND_SIZE_ROWS = 2
INITIAL_LAND_SIZE_COLS = 2
INITIAL_WATER_CAPACITY = 4
MAX_LAND_SIZE = 5
MAX_WATER_CAPACITY = 15
WATER_UPGRADE_COST = 75
LAND_EXPAND_COST_MULTIPLIER = 10
MAX_LOAN_AMOUNT = 20
SEED_PRICES = {"apel": 5, "tomat": 12, "lettuce": 20}
CROP_SELL_PRICES = {"apel": 2, "tomat": 4, "lettuce": 10}
GROWTH_DAYS = {"apel": 2, "tomat": 3, "lettuce": 4}
CROP_EMOJIS = {"apel": "🍎", "tomat": "🍅", "lettuce": "🥬"}


def clear_screen():
    """Membersihkan layar terminal."""
    clear_cmd('cls' if os_name == 'nt' else 'clear')


def print_header(text):
    """Mencetak header yang menarik perhatian."""
    cprint(f"\n{'=' * 42}", 'yellow')
    cprint(f"{text.center(42)}", 'yellow', attrs=['bold'])
    cprint(f"{'=' * 42}", 'yellow')


def print_feedback(text, status="info"):
    """Mencetak pesan feedback dengan ikon dan warna yang sesuai."""
    if status == "success":
        cprint(f"✅ {text}", 'green')
    elif status == "error":
        cprint(f"❌ {text}", 'red')
    elif status == "info":
        cprint(f"ℹ {text}", 'cyan')


def press_enter_to_continue():
    """Menjeda permainan dan menunggu pengguna menekan Enter."""
    cprint("\n[ Tekan Enter untuk melanjutkan... ]", 'white', 'on_grey')
    input()


def animate_welcome():
    """Menampilkan animasi selamat datang di awal permainan."""
    clear_screen()
    cprint("=" * 42, 'green'); cprint("=" + " ".center(40) + "=", 'green')
    cprint("=" + "Selamat Datang di Dunia 👨‍🌾".center(39) + "=", 'green', attrs=['bold'])
    cprint("=" + "HARVEST MOON".center(40) + "=", 'green', attrs=['bold'])
    cprint("=" + " ".center(40) + "=", 'green'); cprint("=" * 42, 'green'); time.sleep(1.5)


def init_music():
    """Menginisialisasi pygame mixer dan memuat file musik."""
    if not exists(MUSIC_FILE):
        print_feedback(f"Peringatan: File musik '{MUSIC_FILE}' tidak ditemukan.", "error")
        return False
    pygame.mixer.init(); pygame.mixer.music.load(MUSIC_FILE)
    print_feedback(f"File musik '{MUSIC_FILE}' berhasil dimuat.", "info")
    return True


def toggle_music(player_data, music_available):
    """Menyalakan atau mematikan musik latar."""
    if not music_available:
        print_feedback("Fungsi musik tidak tersedia.", "error")
        return
    if player_data.get("music_on", False):
        pygame.mixer.music.stop(); player_data["music_on"] = False
        print_feedback("Musik telah dimatikan. 🔇", "info")
    else:
        pygame.mixer.music.play(loops=-1); player_data["music_on"] = True
        print_feedback("Musik telah dinyalakan. 🎵", "info")

def new_game():
    """Menciptakan data untuk permainan baru."""
    initial_land = [[None] * INITIAL_LAND_SIZE_COLS for _ in range(INITIAL_LAND_SIZE_ROWS)]
    return {
        "money": INITIAL_MONEY, "seeds": {"apel": INITIAL_APPLE_SEEDS, "tomat": 0, "lettuce": 0},
        "inventory": {}, "land_rows": INITIAL_LAND_SIZE_ROWS, "land_cols": INITIAL_LAND_SIZE_COLS,
        "land": initial_land, "day": 1, "debt": 0, "water_capacity": INITIAL_WATER_CAPACITY,
        "water_left_today": INITIAL_WATER_CAPACITY, "unlocked_tomat": False,
        "unlocked_lettuce": False, "music_on": True,
    }


def save_game(player_data):
    """Menyimpan data permainan ke file teks."""
    with open(SAVE_FILE, 'w') as f:
        for key, value in player_data.items():
            f.write(f"{key}:{repr(value)}\n")


def load_game():
    """Memuat data permainan dari file, dengan pengaman dari kerusakan file."""
    if not exists(SAVE_FILE): return None
    player_data = {}
    with open(SAVE_FILE, 'r') as f:
        for line in f:
            if ':' in line:
                key, value_str = line.strip().split(':', 1)
                try:
                    player_data[key] = eval(value_str)
                except Exception:
                    print_feedback(f"Peringatan: data '{key}' rusak dan diabaikan.", "error")
                    continue
    return player_data

def show_tutorial():
    """Menampilkan panduan cara bermain."""
    print_header("📖 TUTORIAL PERMAINAN 📖")
    print_feedback("Tujuanmu adalah menjadi petani sukses!", "info")
    print(f"1. Tanam bibit di tanah kosong 🟫.")
    print(f"2. {colored('Siram tanamanmu setiap hari 💧', 'blue')} agar tidak layu.")
    print(f"3. Pergi ke {colored('Market 🛒', 'yellow')} untuk beli bibit/upgrade.")
    print(f"4. Panen 🧺 dan jual untuk dapat {colored('uang 💰', 'yellow')}.")
    print_feedback("Selamat menikmati kehidupan bertani!", "success"); press_enter_to_continue()


def display_land(player_data):
    """Menampilkan kondisi ladang pemain saat ini."""
    print_header("🏡 LADANGMU 🏡")
    cprint(f"Sisa Air Hari Ini: {player_data['water_left_today']}/{player_data['water_capacity']} 💧", 'blue')
    for i in range(player_data["land_rows"]):
        row_display = []
        for j in range(player_data["land_cols"]):
            plant = player_data["land"][i][j]
            if plant is None:
                display_str = colored("[🟫]", 'white', 'on_grey')
            else:
                days_left = plant["days_to_grow"]
                plant_emoji = CROP_EMOJIS.get(plant["name"], "❓")
                water_status = "" if plant.get("watered") else colored("🚱", 'red')
                if days_left <= 0:
                    display_str = colored(f"[{plant_emoji}P]", 'green', attrs=['bold'])
                elif days_left == GROWTH_DAYS.get(plant["name"]):
                    display_str = colored(f"[.🌱{water_status}]", 'yellow')
                else:
                    display_str = colored(f"[🌿{water_status}]", 'cyan')
            row_display.append(display_str)
        print(" ".join(row_display) + f"  Baris {i+1}")
    print("\n" + " ".join([f" Kol {k+1} " for k in range(player_data['land_cols'])]))
    cprint("\nCatatan: 🟫Kosong, .🌱Benih, 🌿Tunas, P-Panen, 🚱Belum Disiram", 'grey')


def plant_seed(player_data):
    clear_screen(); display_land(player_data); print_header("🌱 MENANAM BIBIT 🌱")
    if not any(v > 0 for v in player_data["seeds"].values()):
        print_feedback("Kamu tidak punya bibit!", "error")
        return
    print_feedback("Bibit yang kamu miliki:", "info")
    for seed, count in player_data["seeds"].items():
        if count > 0:
            print(f" - {CROP_EMOJIS.get(seed, '')} {seed.capitalize()}: {count} buah")
    
    row_input = input(f"\nPilih baris (1-{player_data['land_rows']}) atau 'batal': ").lower()
    if row_input == 'batal': return
    col_input = input(f"Pilih kolom (1-{player_data['land_cols']}): ").lower()
    seed_to_plant = input("Pilih bibit yang ingin ditanam: ").lower()

    if not row_input.isdigit() or not col_input.isdigit():
        print_feedback("Input baris dan kolom harus angka.", "error")
        return
    
    row, col = int(row_input) - 1, int(col_input) - 1
    
    if seed_to_plant in player_data["seeds"] and player_data["seeds"][seed_to_plant] > 0:
        if 0 <= row < player_data["land_rows"] and 0 <= col < player_data["land_cols"]:
            if player_data["land"][row][col] is None:
                player_data["land"][row][col] = {"name": seed_to_plant, "days_to_grow": GROWTH_DAYS[seed_to_plant], "watered": False}
                player_data["seeds"][seed_to_plant] -= 1
                print_feedback(f"Bibit {seed_to_plant} berhasil ditanam di ({row+1}, {col+1})!", "success")
            else:
                print_feedback("Lokasi tersebut sudah terisi.", "error")
        else:
            print_feedback("Lokasi tidak valid.", "error")
    else:
        print_feedback(f"Bibit '{seed_to_plant}' tidak ada!", "error")


def water_plants(player_data):
    """Memproses aksi pemain untuk menyiram tanaman."""
    while True:
        clear_screen(); display_land(player_data); print_header("💧 MENYIRAM TANAMAN 💧")
        if player_data["water_left_today"] <= 0:
            print_feedback("Air Anda sudah habis hari ini!", "error"); time.sleep(2); break
        print_feedback("Pilih petak yang ingin disiram.", "info")
        row_input = input(f"Pilih baris (1-{player_data['land_rows']}) atau ketik 'selesai': ").lower()
        if row_input == 'selesai': break
        col_input = input(f"Pilih kolom (1-{player_data['land_cols']}): ").lower()
        if not row_input.isdigit() or not col_input.isdigit():
            print_feedback("Input baris dan kolom harus angka.", "error"); time.sleep(2); continue
        row, col = int(row_input) - 1, int(col_input) - 1
        if not (0 <= row < player_data['land_rows'] and 0 <= col < player_data['land_cols']):
            print_feedback("Koordinat tidak valid!", "error"); time.sleep(2); continue
        plant = player_data['land'][row][col]
        if not plant:
            print_feedback("Tidak ada tanaman di petak ini!", "error"); time.sleep(2); continue
        if plant.get("watered"):
            print_feedback("Tanaman ini sudah disiram.", "info"); time.sleep(2); continue
        plant["watered"] = True
        player_data["water_left_today"] -= 1
        print_feedback(f"Tanaman {plant['name']} di ({row+1}, {col+1}) berhasil disiram!", "success"); time.sleep(1.5)


def sleep(player_data):
    """Memproses akhir hari dengan aturan khusus hari pertama."""
    if player_data["day"] == 1:
        pemain_sudah_menanam = any(petak is not None for baris in player_data["land"] for petak in baris)
        if not pemain_sudah_menanam:
            print_feedback("Kamu harus menanam setidaknya satu bibit di hari pertama sebelum tidur!", "error")
            return False
        ada_tanaman_belum_disiram = any(t is not None and not t.get("watered") for b in player_data["land"] for t in b)
        if ada_tanaman_belum_disiram:
            print_feedback("Di hari pertama, kamu harus menyiram semua tanamanmu sebelum tidur!", "error")
            return False
            
    print_header("🌙 WAKTUNYA TIDUR 🌙")
    cprint("Selamat malam...", 'grey'); time.sleep(1.5); cprint("ZzzZzz...", 'grey'); time.sleep(1.5); clear_screen()
    cprint("☀  Matahari terbit...", 'yellow'); time.sleep(1.5)
    player_data["day"] += 1
    player_data["water_left_today"] = player_data["water_capacity"]
    print_feedback(f"Selamat Pagi! Selamat datang di Hari ke-{player_data['day']}!", "success")
    print_feedback(f"Air telah diisi ulang penuh ({player_data['water_capacity']} 💧).", "info")
    for r_idx, row in enumerate(player_data["land"]):
        for p_idx, plant in enumerate(row):
            if plant:
                if plant.get("watered"):
                    plant["days_to_grow"] -= 1
                    plant["watered"] = False
                else:
                    cprint(f"❌ Tanaman {plant['name']} di ({r_idx+1},{p_idx+1}) layu dan mati!", 'magenta')
                    player_data["land"][r_idx][p_idx] = None
    return True


def harvest(player_data):
    """Memanen semua tanaman yang sudah siap."""
    print_header("🧺 WAKTUNYA PANEN 🧺")
    harvested_something = False
    for i in range(player_data["land_rows"]):
        for j in range(player_data["land_cols"]):
            plant = player_data["land"][i][j]
            if plant and plant["days_to_grow"] <= 0:
                harvested_something = True
                crop_name = plant["name"]
                amount = random.randint(2, 5)
                player_data["inventory"][crop_name] = player_data["inventory"].get(crop_name, 0) + amount
                print_feedback(f"Kamu memanen {amount} {CROP_EMOJIS.get(crop_name, '')} {crop_name}!", "success")
                player_data["land"][i][j] = None
                if crop_name == "apel" and not player_data.get("unlocked_tomat", False):
                    player_data["unlocked_tomat"] = True
                    print_feedback("Kamu telah membuka bibit Tomat!", "info")
                elif crop_name == "tomat" and not player_data.get("unlocked_lettuce", False):
                    player_data["unlocked_lettuce"] = True
                    print_feedback("Kamu telah membuka bibit Lettuce!", "info")
    if not harvested_something:
        print_feedback("Tidak ada tanaman yang siap panen.", "error")


def show_inventory(player_data):
    """Menampilkan status dan barang milik pemain."""
    print_header("🎒 STATUS & INVENTARIS 🎒")
    print_feedback(f"Uang: ${player_data['money']} 💰 | Hutang: ${player_data['debt']} 🏦", "info")
    cprint("\n--- Kantung Bibit ---", attrs=['bold'])
    seeds_owned = {s: c for s, c in player_data["seeds"].items() if c > 0}
    if not seeds_owned:
        print("Kosong.")
    else:
        for s, c in seeds_owned.items():
            print(f" - {CROP_EMOJIS.get(s, '')} {s.capitalize()}: {c} buah")
    cprint("\n--- Keranjang Panen ---", attrs=['bold'])
    if not player_data["inventory"]:
        print("Kosong.")
    else:
        for i, c in player_data["inventory"].items():
            print(f" - {CROP_EMOJIS.get(i, '')} {i.capitalize()}: {c} buah")


def sell(player_data):
    """Menjual hasil panen dari inventaris."""
    print_header("💸 JUAL HASIL PANEN 💸")
    if not player_data["inventory"]:
        print_feedback("Keranjang panenmu kosong!", "error")
        return
    print_feedback("Isi keranjang panenmu:", "info")
    for item, count in player_data["inventory"].items():
        print(f"- {CROP_EMOJIS.get(item, '')} {item.capitalize()}: {count} (Harga: ${CROP_SELL_PRICES[item]}/buah)")
    item_to_sell = input("\nApa yang ingin kamu jual? (atau 'batal'): ").lower()
    if item_to_sell == 'batal': return
    if item_to_sell in player_data["inventory"] and player_data["inventory"][item_to_sell] > 0:
        quantity_input = input(f"Berapa banyak {item_to_sell}? ")
        if not quantity_input.isdigit():
            print_feedback("Jumlah harus angka.", "error")
            return
        quantity = int(quantity_input)
        if 0 < quantity <= player_data["inventory"][item_to_sell]:
            earnings = CROP_SELL_PRICES[item_to_sell] * quantity
            player_data["money"] += earnings
            player_data["inventory"][item_to_sell] -= quantity
            if player_data["inventory"][item_to_sell] == 0:
                del player_data["inventory"][item_to_sell]
            print_feedback(f"Berhasil menjual {quantity} {item_to_sell} dan dapat ${earnings}!", "success")
        else:
            print_feedback("Jumlah tidak valid.", "error")
    else:
        print_feedback("Item tidak ada di inventaris.", "error")


def expand_land(player_data):
    """Memperluas lahan pertanian."""
    print_header("🏞️ PERLUAS LADANG 🏞️")
    if player_data["land_rows"] >= MAX_LAND_SIZE:
        print_feedback("Ladangmu sudah maksimal!", "info")
        return
    cost = (player_data["land_rows"] * player_data["land_cols"]) * LAND_EXPAND_COST_MULTIPLIER
    next_size = f"{player_data['land_rows'] + 1}x{player_data['land_cols'] + 1}"
    print_feedback(f"Biaya perluasan menjadi {next_size} adalah ${cost}", "info")
    choice = input("Perluas ladang? (y/n) ").lower()
    if choice == 'y':
        if player_data["money"] >= cost:
            player_data["money"] -= cost
            player_data["land_rows"] += 1
            player_data["land_cols"] += 1
            old_land = player_data["land"]
            new_land = [[None] * player_data["land_cols"] for _ in range(player_data["land_rows"])]
            for i in range(len(old_land)):
                for j in range(len(old_land[0])):
                    new_land[i][j] = old_land[i][j]
            player_data["land"] = new_land
            print_feedback("Ladang berhasil diperluas!", "success")
        else:
            print_feedback("Uang tidak cukup.", "error")


def bank(player_data):
    """Menu bank untuk pinjam dan bayar hutang."""
    print_header("🏦 BANK WAKANDA 🏦")
    print_feedback(f"Hutangmu saat ini: ${player_data['debt']}", "info")
    print("\n1. 💵 Pinjam Uang\n2. 🧾 Bayar Hutang\n3. 🔙 Kembali")
    choice = input("> ")
    if choice == '1':
        if player_data["debt"] > 0:
            print_feedback("LUNASI dulu hutang sebelumnya!", "error")
            return
        amount_input = input(f"Jumlah pinjaman (maks ${MAX_LOAN_AMOUNT}): ")
        if not amount_input.isdigit():
            print_feedback("Input harus angka.", "error")
            return
        amount = int(amount_input)
        if 0 < amount <= MAX_LOAN_AMOUNT:
            player_data["money"] += amount
            player_data["debt"] += amount
            print_feedback(f"Berhasil meminjam ${amount}.", "success")
        else:
            print_feedback(f"Jumlah pinjaman tidak valid.", "error")
    elif choice == '2':
        if player_data["debt"] == 0:
            print_feedback("Kamu tidak punya hutang.", "info")
            return
        amount_input = input(f"Jumlah pembayaran (maks ${player_data['debt']}): ")
        if not amount_input.isdigit():
            print_feedback("Input harus angka.", "error")
            return
        amount = int(amount_input)
        if 0 < amount <= player_data["money"]:
            pay_amount = min(amount, player_data["debt"])
            player_data["money"] -= pay_amount
            player_data["debt"] -= pay_amount
            print_feedback(f"Berhasil membayar hutang ${pay_amount}.", "success")
        else:
            print_feedback("Uang tidak cukup atau jumlah tidak valid.", "error")


def market(player_data):
    """Menu market untuk membeli bibit dan upgrade."""
    while True:
        clear_screen(); print_header("🛒 MARKET 🛒"); print_feedback(f"Uangmu saat ini: ${player_data['money']} 💰", "info")
        print("\n1. Beli Bibit Tanaman 🌱\n2. Upgrade Kapasitas Air 💧\n3. Kembali ke Ladang 🔙")
        choice = input("> ")
        if choice == '1':
            print_header("🌱 BELI BIBIT 🌱")
            for seed, price in SEED_PRICES.items():
                if (seed == "tomat" and not player_data.get("unlocked_tomat")) or \
                   (seed == "lettuce" and not player_data.get("unlocked_lettuce")): continue
                print(f"- {CROP_EMOJIS.get(seed, '')} {seed.capitalize()}: ${price}")
            seed_to_buy = input("\nApa yang ingin kamu beli? (atau 'batal'): ").lower()
            if seed_to_buy == 'batal': continue
            if seed_to_buy in SEED_PRICES:
                quantity_input = input(f"Berapa banyak bibit {seed_to_buy}? ")
                if not quantity_input.isdigit() or int(quantity_input) <= 0:
                    print_feedback("Jumlah harus angka positif.", "error")
                else:
                    quantity = int(quantity_input)
                    cost = SEED_PRICES[seed_to_buy] * quantity
                    if player_data["money"] >= cost:
                        player_data["money"] -= cost; player_data["seeds"][seed_to_buy] += quantity
                        print_feedback(f"Berhasil membeli {quantity} bibit {seed_to_buy}!", "success")
                    else:
                        print_feedback("Uang tidak cukup.", "error")
            else:
                print_feedback("Bibit tidak tersedia.", "error")
            press_enter_to_continue()
        elif choice == '2':
            print_header("💧 UPGRADE KAPASITAS AIR 💧")
            if player_data.get("water_capacity", INITIAL_WATER_CAPACITY) >= MAX_WATER_CAPACITY:
                print_feedback("Kapasitas air Anda sudah maksimal!", "info")
            else:
                print_feedback(f"Kapasitas saat ini: {player_data['water_capacity']} 💧", "info")
                print_feedback(f"Upgrade ke: {MAX_WATER_CAPACITY} 💧", "info")
                print_feedback(f"Biaya: ${WATER_UPGRADE_COST} 💰", "info")
                confirm = input("Apakah Anda ingin upgrade? (y/n): ").lower()
                if confirm == 'y':
                    if player_data['money'] >= WATER_UPGRADE_COST:
                        player_data['money'] -= WATER_UPGRADE_COST
                        player_data['water_capacity'] = MAX_WATER_CAPACITY
                        player_data['water_left_today'] = MAX_WATER_CAPACITY
                        print_feedback("Selamat! Kapasitas air berhasil di-upgrade!", "success")
                    else:
                        print_feedback("Uang Anda tidak cukup untuk upgrade.", "error")
            press_enter_to_continue()
        elif choice == '3':
            break
        else:
            print_feedback("Pilihan tidak valid.", "error")
            time.sleep(1)


def settings(player_data, music_available):
    """Menu untuk pengaturan game."""
    clear_screen(); print_header("⚙️ PENGATURAN ⚙️")
    music_status = "ON 🎵" if player_data.get("music_on", False) else "OFF 🔇"
    print(f"1. Musik Latar: {music_status}\n2. Kembali")
    choice = input("\nPilih opsi: ")
    if choice == '1':
        toggle_music(player_data, music_available)

def main():
    """Fungsi utama yang menjalankan seluruh alur permainan."""
    animate_welcome(); music_available = init_music(); press_enter_to_continue()
    player_data = None
    while player_data is None:
        clear_screen(); print_header("MENU UTAMA"); print("1. 🎮 New Game\n2. 💾 Load Game")
        choice = input("> ")
        if choice == '1':
            if exists(SAVE_FILE):
                cprint("Memulai game baru akan menghapus data lama.", 'yellow')
                confirm = input("Lanjutkan? (y/n) ").lower()
                if confirm == 'y':
                    player_data = new_game(); show_tutorial()
            else:
                player_data = new_game(); show_tutorial()
        elif choice == '2':
            player_data = load_game()
            if player_data:
                print_feedback("Game berhasil dimuat!", "success"); time.sleep(1.5)
            else:
                print_feedback("Tidak ada data game tersimpan.", "error"); time.sleep(1.5)
    
    if music_available and player_data.get("music_on", True):
        pygame.mixer.music.play(loops=-1)
    
    running = True
    while running:
        clear_screen(); cprint(f"🗓 HARI KE-{player_data['day']} | 💰 UANG: ${player_data['money']} | 🏦 HUTANG: ${player_data['debt']} ", 'white', 'on_blue'); display_land(player_data)
        print_header("PILIH AKSI")
        menu_items = [
            "1. 🌱 Tanam Bibit", "2. 🛒 Market", "3. 💧 Siram Tanaman", "4. 🧺 Panen",
            "5. 💸 Jual Hasil Panen", "6. 🎒 Lihat Inventaris", "7. 🏞️ Perluas Tanah",
            "8. 😴 Tidur", "9. 🏦 Bank", "10. ⚙️ Pengaturan", "11. 💾 Simpan & Keluar"
        ]; rows = 6
        for i in range(rows):
            left_col = menu_items[i]; right_col_index = i + rows
            right_col = menu_items[right_col_index] if right_col_index < len(menu_items) else ""
            print(f"{left_col:<25}{right_col}")
        action = input("> ")
        
        clear_screen()
        
        if action == '1': plant_seed(player_data); press_enter_to_continue()
        elif action == '2': market(player_data)
        elif action == '3': water_plants(player_data)
        elif action == '4': harvest(player_data); press_enter_to_continue()
        elif action == '5': sell(player_data); press_enter_to_continue()
        elif action == '6': show_inventory(player_data); press_enter_to_continue()
        elif action == '7': expand_land(player_data); press_enter_to_continue()
        elif action == '8':
            if not sleep(player_data):
                press_enter_to_continue()
            else:
                save_game(player_data)
        elif action == '9': bank(player_data); press_enter_to_continue()
        elif action == '10': settings(player_data, music_available); press_enter_to_continue()
        elif action == '11':
            save_game(player_data)
            print_feedback("Game berhasil disimpan. Sampai jumpa! 👋", "success")
            running = False
            time.sleep(2)
        else:
            print_feedback("Aksi tidak valid.", "error")
            press_enter_to_continue()
            
    if music_available: pygame.mixer.music.stop()

if __name__ == "__main__":
    main()
