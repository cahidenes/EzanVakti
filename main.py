import gi
import re
import requests
import json
import datetime
from pydbus import SystemBus

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, Gdk
from gi.repository import AppIndicator3 as AppIndicator

CONFIG_FILE = "config.json"
VAKIT_FILE = "vakitler.json"
class Settings():
    def __init__(self):
        with open(CONFIG_FILE) as f:
            self.settings = json.load(f)
    
    def get_ulkeler(self, cache=True):
        try:
            if cache and 'ulkeler' in self.settings:
                self.ulkeler = self.settings['ulkeler']
            else:
                req = requests.get("https://ezanvakti.emushaf.net/ulkeler/").json()
                self.ulkeler = {ulke['UlkeAdi']: ulke['UlkeID'] for ulke in req}
            return list(self.ulkeler.keys())
        except Exception as e:
            print("Ülkeler alınamadı. İnternet bağlantınızı kontrol ediniz.")
            return []
    
    def get_sehirler(self, ulkeAdi, cache=True):
        try:
            id = self.ulkeler[ulkeAdi]
            if cache and 'sehirler' in self.settings:
                self.sehirler = self.settings['sehirler']
            else:
                req = requests.get("https://ezanvakti.emushaf.net/sehirler/" + id).json()
                self.sehirler = {sehir['SehirAdi']: sehir['SehirID'] for sehir in req}
            return list(self.sehirler.keys())
        except Exception as e:
            print("Şehirler alınamadı. İnternet bağlantınızı kontrol ediniz.")
            return []
    
    def get_ilceler(self, sehirAdi, cache=True):
        try:
            id = self.sehirler[sehirAdi]
            if cache and 'ilceler' in self.settings:
                self.ilceler = self.settings['ilceler']
            else:
                req = requests.get("https://ezanvakti.emushaf.net/ilceler/" + id).json()
                self.ilceler = {ilce['IlceAdi']: ilce['IlceID'] for ilce in req}
            return list(self.ilceler.keys())
        except Exception as e:
            print("İlçeler alınamadı. İnternet bağlantınızı kontrol ediniz.")
            return []
    
    def update(self, ulkeAdi, sehirAdi, ilceAdi):
        self.settings['ulke'] = ulkeAdi
        self.settings['ulke_id'] = self.ulkeler[ulkeAdi]
        self.settings['sehir'] = sehirAdi
        self.settings['sehir_id'] = self.sehirler[sehirAdi]
        self.settings['ilce'] = ilceAdi
        self.settings['ilce_id'] = self.ilceler[ilceAdi]
        self.settings['ulkeler'] = self.ulkeler
        self.settings['sehirler'] = self.sehirler
        self.settings['ilceler'] = self.ilceler
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.settings, f)
    
    def save_minute_limits(self, limit1, limit2, limit3, limit4):
        self.settings['vakit_limit_1'] = limit1
        self.settings['vakit_limit_2'] = limit2
        self.settings['vakit_limit_3'] = limit3
        self.settings['vakit_limit_4'] = limit4
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.settings, f)
    

class Vakitler():
    def __init__(self):
        with open(VAKIT_FILE) as f:
            self._vakitler = json.load(f)
        self.yeni_gun_updater()
    
    def yeni_gun_updater(self):
        self.vakitler_seconds = None
        GLib.timeout_add_seconds(86400 - self.get_now_seconds() + 5, self.yeni_gun_updater)
    
    def update(self):
        try:
            self._vakitler = requests.get("https://ezanvakti.emushaf.net/vakitler/" + settings.settings['ilce_id']).json()
            with open(VAKIT_FILE, 'w') as f:
                json.dump(self._vakitler, f)
            self.vakitler_seconds = None
        except Exception as e:
            print("Vakitler alınamadı. İnternet bağlantınızı kontrol ediniz.")
    
    def bugun(self):
        # dd.MM.yyyy
        bugun = datetime.datetime.now().strftime("%d.%m.%Y")
        for vakit in self._vakitler:
            if vakit['MiladiTarihKisa'] == bugun:
                return vakit
        self.update()
        for vakit in self._vakitler:
            if vakit['MiladiTarihKisa'] == bugun:
                return vakit
        return None
    
    def yarin(self):
        yarin = datetime.datetime.now() + datetime.timedelta(days=1)
        yarin = yarin.strftime("%d.%m.%Y")
        for vakit in self._vakitler:
            if vakit['MiladiTarihKisa'] == yarin:
                return vakit
        self.update()
        for vakit in self._vakitler:
            if vakit['MiladiTarihKisa'] == yarin:
                return vakit
        return None

    def time_to_seconds(self, time_string):
        if time_string.count(":") == 1:
            return int(time_string.split(":")[0]) * 3600 + \
                   int(time_string.split(":")[1]) * 60
        else:
            return int(time_string.split(":")[0]) * 3600 + \
                   int(time_string.split(":")[1]) * 60 + \
                   int(time_string.split(":")[2]) * 1
    
    def get_now_seconds(self):
        return self.time_to_seconds(datetime.datetime.now().strftime("%H:%M:%S"))
    
    def get_vakitler_seconds(self):
        if self.vakitler_seconds is None:
            if vakitler.bugun() is None or vakitler.yarin() is None:
                return None
            self.vakitler_seconds = [
                self.time_to_seconds(vakitler.bugun()["Imsak"]),
                self.time_to_seconds(vakitler.bugun()["Gunes"]),
                self.time_to_seconds(vakitler.bugun()["Ogle"]),
                self.time_to_seconds(vakitler.bugun()["Ikindi"]),
                self.time_to_seconds(vakitler.bugun()["Aksam"]),
                self.time_to_seconds(vakitler.bugun()["Yatsi"]),
                self.time_to_seconds(vakitler.yarin()["Imsak"]) + 86400,
            ]
        return self.vakitler_seconds


class MainApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Main Screen")
        self.set_icon_name("ezanvakti.icon")

        self.is_main = True
        self.nereye = ["İmsak'a", "Güneş'e", "Öğle'ye", "İkindi'ye", "Akşam'a", "Yatsı'ya", "İmsak'a"]

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            #top_bar {
                padding: 10px;
            }
            .big-font {
                font-size: 24px;
            }
            .sayac {
                font-size: 40px;
                font-weight: bold;
                color: #6bd067;
            }
            .buvakit {
                color: #6bd067;
                font-size: 21px;
                font-weight: bold;
            }
        """)

        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Header bar
        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_name("top_bar")
        self.header_bar.set_show_close_button(True)
        self.header_bar.set_title("Ezan Vakti")
        self.header_bar.set_decoration_layout(":close")

        settings_button = Gtk.Button()
        settings_button.set_tooltip_text("Open Settings")
        settings_icon = Gtk.Image.new_from_icon_name("settings-symbolic", Gtk.IconSize.BUTTON)
        settings_button.set_image(settings_icon)
        settings_button.connect("clicked", self.open_settings)
        self.header_bar.pack_start(settings_button)
        self.set_titlebar(self.header_bar)

        # Main screen layout
        self.set_default_size(250, 300)
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_margin_start(10)
        self.main_box.set_margin_end(10)
        self.main_box.set_margin_top(20)
        self.main_box.set_margin_bottom(10)
        self.add(self.main_box)

        self.vakit_labels = []
        self.boxes = []
        for time_name in ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.set_margin_start(40)
            box.set_margin_end(40)
            box.pack_start(Gtk.Label(label=time_name), False, True, 0)
            self.vakit_labels.append(Gtk.Label(label="00:00"))
            self.vakit_labels[-1].set_margin_start(30)
            box.pack_end(self.vakit_labels[-1], False, True, 0)
            self.main_box.pack_start(box, True, True, 0)
            self.boxes.append(box)
        
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(10)
        self.main_box.pack_start(sep, True, False, 0)

        self.kalan_label = Gtk.Label(label="İnternet Yok", halign=Gtk.Align.CENTER)
        self.kalan_label.get_style_context().add_class("big-font")
        self.main_box.pack_start(self.kalan_label, True, True, 0)

        self.kalan_time = Gtk.Label(label="00:00:00", halign=Gtk.Align.CENTER)
        self.kalan_time.get_style_context().add_class("sayac")
        self.main_box.pack_start(self.kalan_time, True, True, 0)

        # Settings layout
        self.settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.ulkeler_dropdown = Gtk.ComboBoxText()
        ulkeler = settings.get_ulkeler()
        for ulke in ulkeler:
            self.ulkeler_dropdown.append_text(ulke)
        self.ulkeler_dropdown.set_active(ulkeler.index(settings.settings['ulke']))
        self.settings_box.pack_start(self.ulkeler_dropdown, True, False, 0)

        self.sehirler_dropdown = Gtk.ComboBoxText()
        sehirler = settings.get_sehirler(settings.settings['ulke'])
        for sehir in sehirler:
            self.sehirler_dropdown.append_text(sehir)
        self.sehirler_dropdown.set_active(sehirler.index(settings.settings['sehir']))
        self.settings_box.pack_start(self.sehirler_dropdown, True, False, 0)

        self.ilceler_dropdown = Gtk.ComboBoxText()
        ilceler = settings.get_ilceler(settings.settings['sehir'])
        for ilce in ilceler:
            self.ilceler_dropdown.append_text(ilce)
        self.ilceler_dropdown.set_active(ilceler.index(settings.settings['ilce']))
        self.settings_box.pack_start(self.ilceler_dropdown, True, False, 0)

        def ulke_selected(comboBox):
            self.sehirler_dropdown.remove_all()
            self.ilceler_dropdown.remove_all()
            sehirler = settings.get_sehirler(comboBox.get_active_text(), cache=False)
            for sehir in sehirler:
                self.sehirler_dropdown.append_text(sehir)
        
        def sehir_selected(comboBox):
            if not comboBox.get_active_text():
                return
            self.ilceler_dropdown.remove_all()
            ilceler = settings.get_ilceler(comboBox.get_active_text(), cache=False)
            for ilce in ilceler:
                self.ilceler_dropdown.append_text(ilce)
        
        self.ulkeler_dropdown.connect("changed", ulke_selected)
        self.sehirler_dropdown.connect("changed", sehir_selected)


        def update_settings(button):
            settings.update(self.ulkeler_dropdown.get_active_text(), self.sehirler_dropdown.get_active_text(), self.ilceler_dropdown.get_active_text())
            vakitler.update()
            self.open_settings(button)
            self.update_times()
        button = Gtk.Button.new_with_label("Şehri Ayarla")
        button.connect("clicked", update_settings)
        self.settings_box.pack_start(button, True, False, 0)

        self.settings_box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), True, False, 0)

        self.settings_box.set_margin_start(10)
        self.settings_box.set_margin_end(10)
        self.settings_box.set_margin_top(10)
        self.settings_box.set_margin_bottom(10)

        minute_limits_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.settings_box.pack_start(minute_limits_box, True, False, 0)

        def pack_input(min_range, max_range, var_name, icon_name, last=False):
            def set_entry(entry, value):
                if value < 60:
                    entry.set_text(str(value))
                else:
                    entry.set_text(f'{value//60}:{value%60:02d}')
            def entry_on_insert_text(entry, text, length, position):
                if set(text) & set('0123456789-.:') != set(text):
                    entry.stop_emission_by_name('insert-text')
            def entry_on_focus_out(entry, event):
                try:
                    hour_format = re.fullmatch(r"(\d{1,2})[.:](\d\d)", entry.get_text())
                    if hour_format:
                        hour = int(hour_format.group(1))
                        minute = int(hour_format.group(2))
                        if minute > 60:
                            raise ValueError
                        value = hour * 60 + minute
                    else:
                        value = int(entry.get_text())
                    set_entry(entry, min(max(value, min_range), max_range))
                except ValueError:
                    set_entry(entry, int(settings.settings[var_name]))
            entry = Gtk.Entry()
            entry.set_max_length(5)
            set_entry(entry, int(settings.settings[var_name]))
            entry.connect("insert-text", entry_on_insert_text)
            entry.connect("focus-out-event", entry_on_focus_out)
            entry.set_max_width_chars(5)
            entry.set_width_chars(5)
            minute_limits_box.pack_start(entry, True, True, 0)
            minute_limits_box.pack_start(Gtk.Label(label="≤"), True, True, 0)
            minute_limits_box.pack_start(Gtk.Image.new_from_icon_name(f'ezanvakti.{icon_name}', Gtk.IconSize.DND), True, True, 0)
            if not last: minute_limits_box.pack_start(Gtk.Label(label="<"), True, True, 0)
        pack_input(-9, 0,     'vakit_limit_1', '12'     )
        pack_input(60, 100,   'vakit_limit_2', '3:45'   )
        pack_input(60, 600,   'vakit_limit_3', '6:'     )
        pack_input(60, 24*60, 'vakit_limit_4', '-', True)

        def save_minute_limits(button):
            limit1 = minute_limits_box.get_children()[0].get_value()
            limit2 = minute_limits_box.get_children()[4].get_value()
            limit3 = minute_limits_box.get_children()[8].get_value()
            limit4 = minute_limits_box.get_children()[12].get_value()
            if limit1 <= limit2 <= limit3 <= limit4:
                settings.save_minute_limits(limit1, limit2, limit3, limit4)
                self.open_settings(button)
                tray_icon.update_icon()
            else:
                dialog = Gtk.MessageDialog(parent=self, modal=True, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text="Dakika sınırları sıralı olmalıdır.")
                dialog.run()
                dialog.destroy()
        button = Gtk.Button.new_with_label("Dakika Sınırlarını Kaydet")
        button.connect("clicked", save_minute_limits)
        self.settings_box.pack_start(button, True, False, 0)

        self.settings_box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), True, False, 0)

        self.settings_box.pack_start(Gtk.LinkButton.new_with_label("https://github.com/cahidenes/EzanVakti", "Kaynak koda bak"), True, False, 0)

        self.update_times()
        self.update_sayac()

        def on_destroy(button):
            tray_icon.main_open = False
        self.connect("destroy", on_destroy)

        self.show_all()

    def update_times(self):

        self.header_bar.set_title(settings.settings['ilce'])

        if vakitler.bugun() is None:
            return

        self.header_bar.set_subtitle(vakitler.bugun()['HicriTarihUzun'])

        self.vakit_labels[0].set_label(vakitler.bugun()["Imsak"])
        self.vakit_labels[1].set_label(vakitler.bugun()["Gunes"])
        self.vakit_labels[2].set_label(vakitler.bugun()["Ogle"])
        self.vakit_labels[3].set_label(vakitler.bugun()["Ikindi"])
        self.vakit_labels[4].set_label(vakitler.bugun()["Aksam"])
        self.vakit_labels[5].set_label(vakitler.bugun()["Yatsi"])

    def update_sayac(self):
        today_seconds = vakitler.get_now_seconds()
        vakitler_seconds = vakitler.get_vakitler_seconds()
        if vakitler_seconds is None:
            return
        for i, vakit in enumerate(vakitler_seconds):
            if vakit > today_seconds:
                self.kalan_label.set_label(self.nereye[i])
                self.boxes[(i-1)%6].get_style_context().add_class("buvakit")
                self.boxes[(i-2)%6].get_style_context().remove_class("buvakit")
                fark = vakit - today_seconds
                saat = fark // 3600
                dakika = (fark % 3600) // 60
                saniye = fark % 60

                self.kalan_time.set_label(f"{saat:02d}:{dakika:02d}:{saniye:02d}")
                break
        GLib.timeout_add_seconds(1, self.update_sayac)

    def open_settings(self, button):
        if self.is_main:
            self.remove(self.main_box)
            self.add(self.settings_box)
        else:
            self.remove(self.settings_box)
            self.add(self.main_box)
        self.is_main = not self.is_main
        self.resize(1, 1)
        self.show_all()


class TrayIcon:
    def __init__(self):
        self.main_open = False
        self.minute = '-'

        self.indicator = AppIndicator.Indicator.new(
            "ezan_vakti_tray_icon",
            "ezanvakti.-",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        open_item = Gtk.MenuItem(label="Open")
        open_item.connect("activate", self.open_main)
        self.menu.append(open_item)
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        self.menu.append(quit_item)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        bus = SystemBus()
        login_manager = bus.get("org.freedesktop.login1")
        def on_prepare_for_sleep(sleeping):
            if not sleeping: self.update_icon()
        login_manager.onPrepareForSleep = on_prepare_for_sleep

        self.icon_update_loop()

    def update_icon(self):
        format = "ezanvakti.{}"
        now = vakitler.get_now_seconds()
        seconds = vakitler.get_vakitler_seconds()
        if seconds is None:
            GLib.idle_add(self.indicator.set_icon_full, format.format('-'), "Tray Icon")
            return True

        limit1 = int(settings.settings['vakit_limit_1'])
        limit2 = int(settings.settings['vakit_limit_2'])
        limit3 = int(settings.settings['vakit_limit_3'])
        limit4 = int(settings.settings['vakit_limit_4'])
        newminute = '-'
        for vakit in seconds:
            if vakit + abs(limit1)*60 > now:
                newminute = (vakit - now) // 60
                break
        
        if newminute < limit2:
            newminute = f'{newminute}'
        elif newminute < limit3:
            newminute = f'{newminute // 60}:{newminute % 60:02d}'
        elif newminute < limit4:
            newminute = f'{newminute // 60}:'
        else:
            newminute = '-'

        if newminute != self.minute or newminute == '-':
            GLib.idle_add(self.indicator.set_icon_full, format.format(newminute), "Tray Icon")
            self.minute = newminute
            return True
        
        return False
    
    def icon_update_loop(self):
        now = vakitler.get_now_seconds()
        if self.update_icon():
            GLib.timeout_add_seconds(60 - (now % 60), self.icon_update_loop)
        else:
            GLib.timeout_add_seconds(1, self.icon_update_loop)

    def open_main(self, button):
        if not self.main_open:
            self.main_open = True
            MainApp()
            


if __name__ == "__main__":
    settings = Settings()
    vakitler = Vakitler()
    tray_icon = TrayIcon()
    Gtk.main()