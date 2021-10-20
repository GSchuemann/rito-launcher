#Copyright (C) 2021  <georg.schuemann@web.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import configparser
from pathlib import Path
import wget
import os
import subprocess
import gi

gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, WebKit2, Gdk

wine = ""
wineprefix = ""

button_name = ""
selection = "League of Legends"
update_button = False

###### creating a config file
basedir = Path.home()
data_dir = f"{basedir}/.local/share/rito-launcher/"
conf_file = f"{basedir}/.config/rito-launcher/launcher.cfg"

dir_tuple = [(f"{basedir}/.config/rito-launcher", "configuration directory"),
             (data_dir, "wine directory")]

for (directory, description) in dir_tuple:
    if not Path(directory).is_dir():
        try:
            Path(directory).mkdir(parents=True)
            print(f'Create {description}')
        except OSError as e:
            print(e)
            pass

if not Path(conf_file).exists():
    print('No configuration found')
    with open(conf_file, 'w') as f:
        f.write('''[League]
wine = unknown
location = unknown

[LORE]
wine = unknown
location = unknown

[Browser]
locale = en-us
''')
        f.close()
# check if Lutris installs exist
if Path(f'{basedir}/Games/league-of-legends').exists():  # TODO: find out where the Lutris config file is and use that as determination point, cause right now users with different install locations have the game "uninstalled"
    with open(
            conf_file) as f:  # TODO: rewriting the config file is done multiple times, probably create a function for that
        lines = f.readlines()
    lines[1] = 'wine = $HOME/.local/share/lutris/runners/wine/lutris-ge-lol-6.16-2-x86_64/bin/wine \n'
    lines[2] = 'location = $HOME/Games/league-of-legends/drive_c/Riot\ Games/Riot\ Client/RiotClientServices.exe  \n'
    with open(conf_file, "w") as f:
        f.writelines(lines)
# TODO: Create a proper check for LORE Lutris install later, kinda bad that Lutris uses a non working wine by default
config = configparser.ConfigParser()
config.read([f'{basedir}/rito.launcher/launcher.cfg', conf_file])

startpage = "https://www.leagueoflegends.com/" + config["Browser"]["locale"] + "/news/game-updates/"

def links(url):
    if not url.startswith(':'):
        if not ":" in url:
            if url.startswith('/'):
                href = f'file://{url}'
            elif url.startswith('~'):
                href = f"file://{str(Path(url).expanduser())}"
            else:
                href = f'https://{url}'
        elif url == 'about:home':
            href = startpage
        elif '://' in url:  # Custom "protocols"
            try:
                for key in config['Protocols']:
                    try:
                        href = f"{config['Protocols'][url.split('://', 1)[0]]}{url.split('://', 1)[1]}"
                    except KeyError:
                        href = url
            except KeyError:
                href = url
        else:
            href = url
    else:
        if url.startswith(':exec'):
            os.system(url.split(':exec ', 1)[1])
        elif url == ':home':
            href = startpage
        elif url.startswith(':open') or url.startswith(':o') or url.startswith(':e'):
            href = links(url.split(' ', 1)[1])
        elif url.startswith(':q'):
            Gtk.main_quit()
        else:
            href = url
    try:
        return href
    except UnboundLocalError:
        pass


class Browser(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='rito-launcher')

        styleprovider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        self.context = WebKit2.WebContext.get_default()
        self.view = WebKit2.WebView.new_with_context(self.context)

        self.vbox = Gtk.Box(orientation=Gtk.STYLE_CLASS_VERTICAL)
        self.vbox.expand = True
        self.vbox.set_spacing(10)
        self.menu = Gtk.ComboBoxText()  # TODO: make this in a visually better looking way, preferably with CSD
        options = ['League of Legends', 'Legends of Runeterra', 'Valorant']
        for option in options:
            self.menu.append_text(option)
            # Set first by default
        self.menu.set_active(0)
        self.menu.connect("changed", self.menu_combo_change)
        self.vbox.add(self.menu)
        self.name_icon()

        self.findcontroller = WebKit2.FindController(web_view=self.view)

        self.sw = Gtk.ScrolledWindow()
        self.sw.add(self.view)

        self.vbox.pack_start(self.sw, True, True, 0)
        self.add(self.vbox)
        self.view.load_uri(startpage)
        self.view.connect("notify::uri", self.change_uri)
        self.connect("key-press-event", self.keybinding)
        self.connect("scroll-event", self.mousebindings)

    def create_button(
            self):  # TODO: rewrite this shit, so it makes sense, also a function is probably not needed and probably is a bad idea
        global update_button
        global button_name
        print(update_button)
        if not update_button:
            self.button = Gtk.Button(label=button_name, tooltip_text='Either launches or installs the title')
            self.vbox.add(self.button)
            self.button.connect("clicked", self.launch_game)
            print(button_name)
        else:
            self.button.set_label(button_name)
            print("I do something")
            print(button_name)
        update_button = True

    def change_uri(self, widget, data, *arg):
        uri = widget.get_uri()
        try:
            self.view.load_uri(links(uri))
        except TypeError:
            pass

    def go_back(self, widget):
        self.view.go_back()

    def go_forward(self, widget):
        self.view.go_forward()

    def go_reload(self, widget):
        self.view.reload()

    def go_home(self, widget):
        self.addressbar.set_text(startpage)
        self.view.load_uri(startpage)

    def search_page(self, *args):
        keyword = args[0]
        if not keyword == "":
            self.findcontroller.search(keyword, WebKit2.FindOptions.CASE_INSENSITIVE,
                                       WebKit2.FindOptions.WRAP_AROUND)

    def mousebindings(self, widget, event):
        if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
            scrolldir = event.get_scroll_deltas()[2]
            if scrolldir > 0:
                self.view.set_zoom_level(self.view.get_zoom_level() - 0.1)
            elif scrolldir < 0:
                self.view.set_zoom_level(self.view.get_zoom_level() + 0.1)

    def keybinding(self, widget, event):
        if event.keyval == Gdk.KEY_F5:
            self.view.reload()

    def menu_combo_change(self, combo):
        global selection
        selection = combo.get_active_text()  # definitly a dirty way doing this. TODO: Figure out how to use the index number here
        print(selection)
        if selection == "League of Legends":
            startpage = "https://www.leagueoflegends.com/" + config["Browser"]["locale"] +"/news/game-updates/"
        if selection == "Legends of Runeterra":
            startpage = "https://playruneterra.com/" + config["Browser"]["locale"] +"/news/"
        if selection == "Valorant":
            startpage = "https://playvalorant.com/" + config["Browser"]["locale"] +"/news/"
        self.view.load_uri(startpage)
        self.name_icon()

    def launch_game(self, widget):
        global button_name
        if selection == "League of Legends" and button_name == "Install":
            button_name = "Installation has started"
            self.install_league()
        if selection == "League of Legends" and button_name == "Launch":
            self.launch_league()
        if selection == "Legends of Runeterra" and button_name == "Install":
            self.install_runeterra()
        if selection == "Legends of Runeterra" and button_name == "Launch":
            self.launch_runeterra()
        if selection == "Valorant":
            button_name = "Oh no, sadly Valorant is not supported (yet) under Linux by this launcher"
            self.create_button()

    def install_runeterra(self):
        print("Install runeterra is called")
        global button_name
        global selection
        global wine
        global wineprefix

        button_name = "Installing " + selection
        self.create_button()
        wget.download("https://bacon.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.exe",
                      data_dir)
        wineprefix = "env WINEPREFIX=" + data_dir + "loreprefix "
        wine = "wine "
        self.install_dxvk
        subprocess.Popen([wineprefix + wine + data_dir + "Legends_Of_Runeterra_Installer.exe"],
                         shell=True)
        with open(conf_file) as f:
            lines = f.readlines()
        lines[5] = 'wine = ' + wine + ' \n'
        lines[6] = 'location =' + data_dir + 'loreprefix/drive_c/Riot\ Games/Riot\ Client/RiotClientServices.exe \n'
        with open(conf_file, "w") as f:
            f.writelines(lines)
        Gtk.main_quit()

    def install_league(self):
        global button_name
        global selection
        global wine
        global wineprefix
        button_name = "Installing " + selection
        self.create_button()
        subprocess.Popen(
            "wget https://github.com/GloriousEggroll/wine-ge-custom/releases/download/6.16-2-GE-LoL/lutris-ge-6.16-2-lol-x86_64.tar.xz" + " -O " + data_dir + "lutris-ge-6.16-2-lol-x86_64.tar.xz",
            shell=True).wait()
        wget.download("https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.na.exe",
                      data_dir + "/live.na.exe")
        Path(data_dir + "league_wine").mkdir()
        subprocess.Popen(
            ["tar " + "-xvf " + data_dir + "lutris-ge-6.16-2-lol-x86_64.tar.xz " + "-C " + data_dir + "league_wine "],
            shell=True).wait()
        wineprefix = "env WINEPREFIX=" + data_dir + "leagueprefix "
        wine = data_dir + "league_wine/lutris-ge-6.16-2-lol-x86_64/bin/wine "
        self.install_dxvk()
        subprocess.Popen([wineprefix + wine + data_dir + "live.na.exe"], shell=True)
        with open(conf_file) as f:
            lines = f.readlines()
        lines[1] = 'wine = ' + wine + '\n'
        lines[2] = 'location = ' + data_dir + 'leagueprefix/drive_c/Riot\ Games/Riot\ Client/RiotClientServices.exe \n'
        with open(conf_file, "w") as f:
            f.writelines(lines)
        Gtk.main_quit()

    def launch_league(self):
        command = "env WINEPREFIX=" + data_dir + "leagueprefix " + config["League"]["wine"] + " " + config["League"][
            "location"] + " --launch-patchline=live" + " --launch-product=league_of_legends"
        print(command)
        subprocess.Popen("chmod +x lol-launchhelper.sh", shell=True)
        subprocess.Popen(["./lol-launchhelper.sh & " + command], shell=True)

    def launch_runeterra(self):
        command = "env WINEPREFIX=" + data_dir + "/loreprefix/ " + config["LORE"]["wine"] + " " + config["LORE"][
            "location"] + " --launch-patchline=live" + " --launch-product=bacon"
        print(command)
        subprocess.Popen([command], shell=True).wait()
        Gtk.main_quit()

    ## Correctly Name the Install/Launch button (I don't know why I call this function name_icon, guess I intended it to be an icon at some point, might do this later
    def name_icon(self):
        print("name_icon is called")
        global button_name
        global selection
        print(config['League']['wine'])
        print("here it stops")
        if selection == "League of Legends":
            if (config['League']['wine']) == "unknown":
                button_name = "Install"
            else:
                button_name = "Launch"
        if selection == "Legends of Runeterra":
            if (config['LORE']['wine']) == "unknown":
                button_name = "Install"
            else:
                button_name = "Launch"
        if selection == "Valorant":
            button_name = "Install"
        self.create_button()
        print(button_name)

    def install_dxvk(self):
        global wine
        global wineprefix
        print(wine)
        print(wineprefix)
        if not Path(data_dir + "winetricks").exists():
            subprocess.Popen(
                ["wget" + " http://winetricks.org/winetricks " + "-O" + data_dir + "winetricks"],
                shell=True).wait()
            subprocess.Popen("chmod +x " + data_dir + "winetricks", shell=True)
        subprocess.Popen([wineprefix + " WINE=" + wine + " " + data_dir + "winetricks " + "dxvk"],
                         shell=True).wait()


if __name__ == "__main__":
    browser = Browser()
    browser.maximize()
    browser.connect("delete-event", Gtk.main_quit)
    browser.show_all()
    Gtk.main()
