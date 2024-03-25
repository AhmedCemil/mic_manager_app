import customtkinter as ctk
from time import sleep
from comtypes import CLSCTX_ALL
from threading import Thread, Event
from PyQt6.QtGui import QAction, QIcon
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

# Created by Ahmed Cemil Bilgin


class mic_control:
    def __init__(self):
        self.mic_devices = AudioUtilities.GetMicrophone()
        self.mic_interface = self.mic_devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        self.mic_volume = self.mic_interface.QueryInterface(IAudioEndpointVolume)
        # 0 is unmuted, 1 is muted
        self.mic_state = self.get_state()

    def get_state(self):
        return self.mic_volume.GetMute()

    def set_state(self, mute):
        # 0 is unmuted, 1 is muted
        self.mic_volume.SetMute(1 if mute else 0, None)


class mic_thread:
    def __init__(self):
        self.stop_event = Event()

    def set_and_start_thread(self, func):
        self.stop_event.clear()
        self.mic_thread = Thread(target=self.thread_func, args=(func, self.stop_event))
        self.mic_thread.start()

    def thread_func(self, func, stop_event):
        while not stop_event.is_set():
            func()
            # Wait for the stop event to be set before exiting the thread function
            # sys.stdout.write("\r")
            sleep(0.001)


class systray:
    def __init__(self):
        self.mic = mic_control()
        self.mic_thread_control = mic_thread()
        Thread(target=self.Window).start()

        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)

        # Create the tray
        self.tray = QSystemTrayIcon()
        self.set_icon()
        self.tray.setVisible(True)

        # Create the menu
        self.menu = QMenu()

        # Add options to the menu.
        self.mic_unmute = QAction("Unmute")
        self.mic_mute = QAction("Mute")
        self.quit = QAction("Exit")

        # Add icons to the options.
        self.mic_unmute.setIcon(QIcon("mic_unmuted.ico"))
        self.mic_mute.setIcon(QIcon("mic_muted.ico"))
        self.quit.setIcon(QIcon("exit.ico"))

        # Add actions to the options.
        self.mic_unmute.triggered.connect(self.set_mic_unmute)
        self.mic_mute.triggered.connect(self.set_mic_mute)
        self.quit.triggered.connect(self.exit)

        # Add options to the menu.
        self.menu.addAction(self.mic_unmute)
        self.menu.addAction(self.mic_mute)
        self.menu.addAction(self.quit)

        # Start thread
        self.mic_thread_control.set_and_start_thread(func=self.control_mic_state)

        # Add the menu to the tray
        self.tray.setContextMenu(self.menu)

        self.app.exec()

    def set_icon(self):
        self.tray.setIcon(
            QIcon("mic_unmuted.ico" if self.mic.mic_state == 0 else "mic_muted.ico")
        )

    def set_mic_mute(self):
        self.mic.set_state(mute=True)

    def set_mic_unmute(self):
        self.mic.set_state(mute=False)

    def control_mic_state(self):
        _state = self.mic.get_state()
        if self.mic.mic_state != _state:
            self.mic.mic_state = _state
            self.set_icon()
            try:
                self.ctk_label.configure(
                    text="Muted" if self.mic.mic_state else "Unmuted",
                    text_color="red" if self.mic.mic_state else "lightgreen",
                )
            except:
                pass
            self.ctk_notify.deiconify()
            sleep(0.5)
            self.ctk_label.configure(text="")
            self.ctk_notify.withdraw()

    def Window(self):
        self.ctk_notify = ctk.CTk()
        self.ctk_notify.geometry(
            f"300x100+{self.ctk_notify.winfo_screenwidth()-325}+25"
        )
        self.ctk_notify._set_appearance_mode("dark")
        self.ctk_notify.configure(fg_color="black")
        self.ctk_notify.resizable(width=False, height=False)
        self.ctk_notify.overrideredirect(True)
        self.ctk_notify.withdraw()
        self.ctk_notify.deiconify()
        self.ctk_notify.attributes("-topmost", True)
        self.ctk_notify.attributes("-disabled", True)
        self.ctk_notify.attributes("-transparentcolor", "black")
        self.ctk_notify.attributes("-toolwindow", "True")
        self.ctk_notify.config(bg="")

        self.ctk_label = ctk.CTkButton(
            master=self.ctk_notify,
            text="",
            text_color="red",
            fg_color="transparent",
            font=ctk.CTkFont(family="Calibri", size=50, weight="bold"),
        )
        self.ctk_label.pack(anchor="center")
        # self.ctk_notify.after(600, self.ctk_notify.destroy)
        self.ctk_notify.mainloop()

    def exit(self):
        self.mic_thread_control.stop_event.set()
        self.ctk_notify.quit()
        self.app.quit()


if __name__ == "__main__":
    systray()
