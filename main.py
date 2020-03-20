import sys
import time
import os
import json
import tkinter

from discord_webhook import DiscordWebhook, DiscordEmbed

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

class MinecraftWatcher:
    def __init__(self):
        self.__profiles_path = Main.data['minecraft_path']
        self.__screenshots_path = os.path.join(Main.data['minecraft_path'],'screenshots')
        self.__logs_path = os.path.join(Main.data['minecraft_path'],'logs')

        self.__screenshots_event_handler = ScreenshotsEventHandler()
        self.__logs_event_handler = LogsEventHandler()
        self.__profiles_event_handler = ProfilesEventHandler()

        self.__event_observer = Observer()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        self.__event_observer.schedule(
            self.__profiles_event_handler,
            self.__profiles_path,
            recursive=False
        )
        self.__event_observer.schedule(
            self.__screenshots_event_handler,
            self.__screenshots_path,
            recursive=False
        )
        self.__event_observer.schedule(
            self.__logs_event_handler,
            self.__logs_path,
            recursive=False
        )

class ProfilesEventHandler(RegexMatchingEventHandler):
    def __init__(self):
        super().__init__([r".*launcher_profiles\.json$"])

    def on_modified(self, event):
        self.process(event)

    def process(self, event):
        Main.update()

class ScreenshotsEventHandler(RegexMatchingEventHandler):
    def __init__(self):
        super().__init__([r".*\.png$"])

    def on_created(self, event):
        self.process(event)

    def process(self, event):
        time.sleep(1)
        _, filename = os.path.split(event.src_path) 
        with open(event.src_path, "rb") as f:
            webhook = DiscordWebhook(url=Main.data['webhook'])
            webhook.add_file(file=f.read(), filename=filename)
            embed = DiscordEmbed(title="Capture d'écran de "+Main.data['playername'], description=filename, color=242424)
            embed.set_thumbnail(url='attachment://'+filename)
            webhook.add_embed(embed)
            webhook.execute()

class LogsEventHandler(RegexMatchingEventHandler):
    def __init__(self):
        super().__init__([r".*latest\.log$"])
        with open(os.path.join(Main.data['minecraft_path'],'logs','latest.log')) as f:
            self.previousLinesCount = len(f.readlines())

    def on_modified(self, event):
        self.process(event)

    def process(self, event):
        time.sleep(1)
        with open(event.src_path) as f:
            lines = f.readlines()
            self.currentLinesCount = len(lines)
            newLines = lines[self.previousLinesCount:self.currentLinesCount]
            self.previousLinesCount = self.currentLinesCount
            for line in newLines:
                if "[CHAT] <"+Main.data['playername']+"> ::" in line:
                    command = line.partition("::")[2]
                    if command.startswith("msg "):
                        message = command[4:]
                        webhook = DiscordWebhook(url=Main.data['webhook'])
                        embed = DiscordEmbed(title="Message de "+Main.data['playername'], description=message, color=242424)
                        webhook.add_embed(embed)
                        webhook.execute()

class Main:
    data = None

    def __init__(self):
        Main.data = dict()

    @staticmethod
    def update():
        with open(os.path.join(Main.data['minecraft_path'],'launcher_profiles.json')) as jsonFile:
            infos = json.load(jsonFile)
            Main.data['playername'] = infos["authenticationDatabase"][infos["selectedUser"]["account"]]["profiles"][infos["selectedUser"]["profile"]]["displayName"]


    def testConfig(self):
        Main.data['minecraft_path'] = self.EntryMinecraftPathValue.get()
        Main.data['webhook'] = self.EntryWebhookValue.get()

        print(self.EntryMinecraftPathValue.get())
        print(self.EntryWebhookValue.get())
        print(Main.data['minecraft_path'])
        print(Main.data['webhook'])

        webhook = DiscordWebhook(url=Main.data['webhook'])
        embed = DiscordEmbed(title="Message de "+Main.data['playername'], description="Test de configuration.", color=484848)
        webhook.add_embed(embed)
        webhook.execute()
        try:
            with open(os.path.join(os.getenv('APPDATA'),'Minecraft-Discord.json'),mode='w') as jsonFile:
                jsonData = dict()
                jsonData["webhook"] = Main.data['webhook']
                jsonData["minecraft_path"] = Main.data['minecraft_path']
                json.dump(jsonData, jsonFile)
        except Exception as e:
            print(e)
        self.watcher.stop()
        self.watcher = MinecraftWatcher()
        self.watcher.start()
        
    def main(self):
        Main.data['webhook'] = "Ask your Discord's admin for the correct webhook"
        Main.data['minecraft_path'] = os.path.join(os.getenv('APPDATA'),'.minecraft')
        try:
            with open(os.path.join(os.getenv('APPDATA'),'Minecraft-Discord.json')) as jsonFile:
                jsonData = json.load(jsonFile)
                Main.data['webhook'] = jsonData["webhook"]
                Main.data['minecraft_path'] = jsonData["minecraft_path"]
        except:
            pass

        Main.update()

        self.window = tkinter.Tk()
        self.window.title("Jumbef's Minecraft-Discord-sender - 1.2.0")
        
        self.EntryMinecraftPathValue = tkinter.StringVar(self.window, value=Main.data['minecraft_path'])
        self.EntryMinecraftPath = tkinter.Entry(self.window, textvariable=self.EntryMinecraftPathValue,width=150)
        self.EntryWebhookValue = tkinter.StringVar(self.window, value=Main.data['webhook'])
        self.EntryWebhook = tkinter.Entry(self.window, textvariable=self.EntryWebhookValue,width=150)
        
        self.lblMinecraftPath = tkinter.Label(self.window, text="Minecraft folder: ")
        self.lblWebhook = tkinter.Label(self.window, text="Discord webhook: ")
        self.lblMessage = tkinter.Label(self.window, text="Close window to quit.")

        self.ButtonTestConfig = tkinter.Button(self.window, text="Test/Save", command=self.testConfig)

        self.lblMinecraftPath.grid(row=0)
        self.EntryMinecraftPath.grid(row=0, column=1)
        self.lblWebhook.grid(row=1)
        self.EntryWebhook.grid(row=1, column=1)
        self.lblMessage.grid(row=2, column=1)
        self.ButtonTestConfig.grid(row=0, column=2, rowspan=2)

        
        self.watcher = MinecraftWatcher()
        self.watcher.start()
        self.window.mainloop()
        self.watcher.stop()

if __name__ == "__main__":
    Main().main()
