import flet as ft
from datetime import datetime
from models import init_db, SessionLocal, User, PasienPrana, PasienHypno, KunjunganPrana, KunjunganHypno
from werkzeug.security import check_password_hash

def main(page: ft.Page):
    init_db()
    db = SessionLocal()

    page.title = "Symmetria Clinic"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.primary_color = "#00897B"
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO

    current_user = None

    # --- HELPER UTILS ---
    def hitung_umur(tgl_lahir):
        if not tgl_lahir:
            return "-"
        if isinstance(tgl_lahir, str):
            try:
                tgl_lahir = datetime.strptime(tgl_lahir, "%Y-%m-%d").date()
            except ValueError:
                return "-"
        today = datetime.now().date()
        return f"{today.year - tgl_lahir.year - ((today.month, today.day) < (tgl_lahir.month, tgl_lahir.day))} thn"

    # --- HANDLER LOGIN ---
    def handle_login(username, password):
        nonlocal current_user
        if not username or not password:
            page.snack_bar = ft.SnackBar(ft.Text("Username dan Password wajib diisi!"))
            page.snack_bar.open = True
            page.update()
            return

        user = db.query(User).filter(User.username == username).first()
        is_valid = False
        if user:
            if hasattr(user, 'password_hash') and user.password_hash:
                is_valid = check_password_hash(user.password_hash, password)
            elif hasattr(user, 'password') and user.password:
                is_valid = (user.password == password) or check_password_hash(user.password, password)

        if user and is_valid:
            current_user = user
            show_dashboard_view()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Username atau Password salah!"))
            page.snack_bar.open = True
            page.update()

    # --- 1. HALAMAN LOGIN ---
    def show_login_view():
        page.clean()
        page.navigation_bar = None
        
        username_input = ft.TextField(label="Username", width=300, autofocus=True)
        password_input = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)

        login_btn = ft.ElevatedButton(
            text="Login",
            width=300,
            bgcolor="#00897B",
            color="white",
            on_click=lambda _: handle_login(username_input.value, password_input.value)
        )

        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Symmetria Clinic", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Silakan login untuk melanjutkan", size=14, color=ft.colors.GREY_600),
                        ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                        username_input,
                        password_input,
                        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                        login_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                padding=30,
            )
        )

        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(login_card)
        page.update()

    # --- NAVBAR UTAMA ---
    def setup_navbar(selected_idx=0):
        def nav_change(e):
            idx = e.control.selected_index
            if idx == 0:
                show_dashboard_view()
            elif idx == 1:
                show_pasien_list("prana")
            elif idx == 2:
                show_pasien_list("hypno")

        page.navigation_bar = ft.NavigationBar(
            selected_index=selected_idx,
            on_change=nav_change,
            destinations=[
                ft.NavigationDestination(icon=ft.icons.DASHBOARD, label="Dashboard"),
                ft.NavigationDestination(icon=ft.icons.SPA, label="Prana"),
                ft.NavigationDestination(icon=ft.icons.PSYCHOLOGY, label="Hypnotherapi"),
            ]
        )

    # --- 2. HALAMAN DASHBOARD ---
    def show_dashboard_view():
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        setup_navbar(0)

        total_prana = db.query(PasienPrana).count()
        total_hypno = db.query(PasienHypno).count()

        prana_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Pasien Prana", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(str(total_prana), size=36, color="#00897B", weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=20, width=150, alignment=ft.alignment.center
            )
        )

        hypno_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Pasien Hypno", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(str(total_hypno), size=36, color="#00897B", weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=20, width=150, alignment=ft.alignment.center
            )
        )

        username_display = current_user.username if current_user else "Admin"

        page.add(
            ft.AppBar(
                title=ft.Text(f"Halo, {username_display}"),
                bgcolor="#00897B",
                color="white",
                actions=[
                    ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: show_login_view())
                ]
            ),
            ft.Column([
                ft.Text("Ringkasan Data Klinik", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([prana_card, hypno_card], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=20)
        )
        page.update()

    # --- 3. HALAMAN DAFTAR PASIEN ---
    def show_pasien_list(tipe="prana"):
        page.clean()
        setup_navbar(1 if tipe == "prana" else 2)

        if tipe == "prana":
            pasien_list = db.query(PasienPrana).all()
            title_text = "Daftar Pasien Prana"
        else:
            pasien_list = db.query(PasienHypno).all()
            title_text = "Daftar Pasien Hypnotherapi"

        list_tiles = []
        for p in pasien_list:
            age_str = hitung_umur(p.tanggal_lahir)
            list_tiles.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.PERSON),
                    title=ft.Text(p.nama, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"Domisili: {p.domisili or '-'} | Usia: {age_str}"),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=lambda e, pid=p.id: show_pasien_form(tipe, pid)
                )
            )

        page.add(
            ft.AppBar(
                title=ft.Text(title_text),
                bgcolor="#00897B",
                color="white",
                actions=[
                    ft.IconButton(ft.icons.ADD, on_click=lambda _: show_pasien_form(tipe))
                ]
            ),
            ft.ListView(controls=list_tiles, expand=True, spacing=10) if list_tiles else ft.Text("Belum ada data pasien.", size=16)
        )
        page.update()

    # --- 4. FORM PASIEN & RIWAYAT KUNJUNGAN ---
    def show_pasien_form(tipe="prana", pasien_id=None):
        page.clean()
        setup_navbar(1 if tipe == "prana" else 2)

        ModelPasien = PasienPrana if tipe == "prana" else PasienHypno
        ModelKunjungan = KunjunganPrana if tipe == "prana" else KunjunganHypno

        pasien = db.query(ModelPasien).get(pasien_id) if pasien_id else None

        tgl_val = str(pasien.tanggal_lahir) if (pasien and pasien.tanggal_lahir) else ""

        nama_field = ft.TextField(label="Nama Pasien", value=pasien.nama if pasien else "")
        domisili_field = ft.TextField(label="Domisili", value=pasien.domisili if pasien else "")
        ibu_field = ft.TextField(label="Nama Ibu Kandung", value=pasien.nama_ibu if pasien else "")
        tgl_lahir_field = ft.TextField(label="Tanggal Lahir (YYYY-MM-DD)", hint_text="Contoh: 1990-08-17", value=tgl_val)

        # Fields Kunjungan Baru
        keluhan_field = ft.TextField(label="Keluhan & Gejala", multiline=True, min_lines=2)
        diagnosa_field = ft.TextField(label="Diagnosa", multiline=True, min_lines=2)
        terapi_field = ft.TextField(label="Therapi", multiline=True, min_lines=2)
        hasil_field = ft.TextField(label="Hasil / Progress", multiline=True, min_lines=2)

        # Menampilkan Riwayat Kunjungan Lama jika ada
        riwayat_controls = []
        if pasien and hasattr(pasien, 'kunjungan') and pasien.kunjungan:
            riwayat_controls.append(ft.Text("Riwayat Kunjungan:", weight=ft.FontWeight.BOLD, size=16))
            for k in pasien.kunjungan:
                riwayat_controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"Tgl Kunjungan: {k.tanggal_kunjungan}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Keluhan: {k.keluhan or '-'}"),
                                ft.Text(f"Diagnosa: {k.diagnosa or '-'}"),
                                ft.Text(f"Terapi: {k.terapi or '-'}"),
                                ft.Text(f"Hasil: {k.hasil or '-'}"),
                            ], spacing=5),
                            padding=10
                        )
                    )
                )

        def simpan_data(e):
            nonlocal pasien
            try:
                parsed_tgl = datetime.strptime(tgl_lahir_field.value, "%Y-%m-%d").date() if tgl_lahir_field.value else datetime.now().date()
            except ValueError:
                parsed_tgl = datetime.now().date()

            if not pasien:
                pasien = ModelPasien(
                    nama=nama_field.value,
                    domisili=domisili_field.value,
                    nama_ibu=ibu_field.value,
                    tanggal_lahir=parsed_tgl
                )
                db.add(pasien)
                db.commit()
                db.refresh(pasien)
            else:
                pasien.nama = nama_field.value
                pasien.domisili = domisili_field.value
                pasien.nama_ibu = ibu_field.value
                pasien.tanggal_lahir = parsed_tgl
                db.commit()

            if keluhan_field.value or terapi_field.value or diagnosa_field.value:
                kunjungan = ModelKunjungan(
                    pasien_id=pasien.id,
                    tanggal_kunjungan=datetime.now().date(),
                    keluhan=keluhan_field.value,
                    diagnosa=diagnosa_field.value,
                    terapi=terapi_field.value,
                    hasil=hasil_field.value
                )
                db.add(kunjungan)
                db.commit()

            show_pasien_list(tipe)

        form_items = [
            ft.Text("Data Pribadi Pasien", weight=ft.FontWeight.BOLD, size=16),
            nama_field,
            domisili_field,
            ibu_field,
            tgl_lahir_field,
            ft.Divider(),
            ft.Text("Tambah Kunjungan Baru", weight=ft.FontWeight.BOLD, size=16),
            keluhan_field,
            diagnosa_field,
            terapi_field,
            hasil_field,
            ft.Row([
                ft.ElevatedButton("Simpan Data", on_click=simpan_data, bgcolor="#00897B", color="white"),
                ft.OutlinedButton("Batal", on_click=lambda _: show_pasien_list(tipe))
            ], spacing=10),
            ft.Divider()
        ] + riwayat_controls

        page.add(
            ft.AppBar(
                title=ft.Text(f"Form Pasien {tipe.capitalize()}"),
                bgcolor="#00897B",
                color="white"
            ),
            ft.Column(form_items, scroll=ft.ScrollMode.AUTO)
        )
        page.update()

    # Jalankan awal
    show_login_view()

if __name__ == "__main__":
    ft.app(target=main)