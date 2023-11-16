import customtkinter as ctk
from time import sleep
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from infi.systray import SysTrayIcon
from thread_manager import ThreadManager

# Created by Ahmed Cemil Bilgin


class MicManagerApp:
    def __init__(self):
        self.initialize()

    def initialize(self):
        # thread manager
        self.thm = ThreadManager()

        # mic
        self.mic_devices = AudioUtilities.GetMicrophone()
        self.mic_interface = self.mic_devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None,
        )
        self.mic_volume = self.mic_interface.QueryInterface(IAudioEndpointVolume)
        # 0 is unmuted, 1 is muted
        self.mic_state_previous = self.mic_volume.GetMute()

        # systray
        self.hover_text = "Mic Manager App by ACB"
        self.menu_options = (
            (
                "Unmute",
                "mic_unmuted.ico",
                self.mic_unmute,
            ),
            (
                "Mute",
                "mic_muted.ico",
                self.mic_mute,
            ),
            (
                "Exit",
                "exit.ico",
                self.exit,
            ),
        )

    def start(self):
        self.sysTrayIcon = SysTrayIcon(
            icon="mic_unmuted.ico" if self.mic_state_previous == 0 else "mic_muted.ico",
            hover_text=self.hover_text,
            menu_options=self.menu_options,
            on_quit=None,
        )
        self.sysTrayIcon._menu_options.pop()
        self.sysTrayIcon.start()

        self.thm.add_thread(thread_name="mma", func=self.mic_thread)
        self.thm.start_thread(thread_name="mma")

    def notify(self):
        self.ctk_notify = ctk.CTk()
        self.ctk_notify.geometry(
            f"300x100+{self.ctk_notify.winfo_screenwidth()-325}+25"
        )
        self.ctk_notify._set_appearance_mode("dark")
        self.ctk_notify.configure(fg_color="black")
        self.ctk_notify.resizable(width=False, height=False)
        self.ctk_notify.overrideredirect(True)
        # self.ctk_notify.withdraw()
        self.ctk_notify.attributes("-topmost", True)
        self.ctk_notify.attributes("-disabled", True)
        self.ctk_notify.attributes("-transparentcolor", "black")
        self.ctk_notify.config(bg="")

        self.ctk_label = ctk.CTkButton(
            master=self.ctk_notify,
            text="Unmuted!" if self.mic_state_previous == 0 else "Muted!",
            text_color="lightgreen" if self.mic_state_previous == 0 else "red",
            fg_color="transparent",
            font=ctk.CTkFont(family="Calibri", size=50, weight="bold"),
        )
        self.ctk_label.pack(anchor="center")
        self.ctk_notify.after(1000, self.ctk_notify.destroy)
        self.ctk_notify.mainloop()

    def mic_unmute(self, *args):
        self.mic_volume.SetMute(0, None)

    def mic_mute(self, *args):
        self.mic_volume.SetMute(1, None)

    def notify_mic_state(self):
        self.sysTrayIcon.update(
            icon="mic_unmuted.ico" if self.mic_state_previous == 0 else "mic_muted.ico"
        )
        self.notify()

    def mic_thread(self):
        _mic_state = self.mic_volume.GetMute()
        if _mic_state != self.mic_state_previous:
            self.mic_state_previous = _mic_state
            self.notify_mic_state()
        sleep(0.1)

    def exit(self, *args):
        self.thm.stop_all_threads()
        self.sysTrayIcon._destroy(None, None, None, None)


if __name__ == "__main__":
    app = MicManagerApp()
    app.start()
