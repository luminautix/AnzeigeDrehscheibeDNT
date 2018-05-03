from socketserver import BaseRequestHandler, UDPServer
from threading import Thread
from queue import Queue, Empty
from tkinter import Tk, Frame, Label, Canvas
from math import sin, cos, radians
from time import time

class myUDPServer(UDPServer):

    def __init__(self, server_address, RequestHandlerClass, q, bind_and_activate=True):
        UDPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate=True)
        self.q = q

class MyUdpHandler(BaseRequestHandler):

    def handle(self):
        self.data = self.request[0].strip()
#        socket = self.request[1] # liefert: <socket.socket fd=188, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 51456)>
        self.dataTuple = (self.client_address[0], self.client_address[1], self.data.decode())
        self.server.q.put(self.dataTuple)

class mainWindow(Frame):
    def __init__(self, q, server, master=None):
        super(mainWindow, self).__init__(master)
        self.master.protocol('WM_DELETE_WINDOW', self.beenden)      # beendet, bei Klick auf das Menüzeilenkreuz das Programm sauber
        self.master.title("DNT Scheibenstand")
        self.pack()
        self.cv = Canvas(self, width=250, height=250)
        self.cv.pack()
        self.drehScheibe()
        self.q = q
        self.server = server                                        # notwendig, um 'server' aus der GUI beenden zu können
        self.message = "keine Daten"
        self.timeSinceLastData = time()
        self.dataOld = 1
        self.labelData = Label(self, text="Drehbühne Position:")
        self.labelData.pack()
        self.labelSensor = Label(self, font=("", 24), text=self.message)
        self.labelSensor.pack()
        self.updateLabelData()

    def updateLabelData(self):
        try:
            self.message = self.q.get_nowait()                      # möglicher Fehler 'Empty'
            try:
                self.meterData = (int(self.message[2]))             # workarround um führende Nullen zu eliminieren # möglicher Fehler 'ValueError'
                self.meterData = self.offsetData(self.meterData, 1) # offsetData beruhigt die Anzeige um den zweiten Wert im Funktionsaufruf
                self.meterData = self.meterData - 1416              # Barcode Offset, weil Barcodeleser physisch an anderem Standort als Maschinenstand-Barcode-Leser
                if self.meterData > 4424:                           # größtmöglicher Wert ist '4424', dann folgt auf dem Barcodeband die '0004'
                    self.meterData = self.meterData - 4424
                self.meterData = int(self.meterData * 5010 / 4424)  # Barcodeband ist kürzer als der Drehscheibenumfang, Durchmesser der Drehscheibe ist größer
                self.positionsStrich(self.meterData)
                self.timeSinceLastData = time()                     # nimmt die Zeit, wann die letzten Daten empfangen wurden
                if self.meterData != 0:
                    self.meterData = self.meterData / 100           # Wert wird hier zur Kommazahl (float), z.B. 1423cm zu 14,23m
                self.labelSensor["text"] = (str(self.meterData)).replace(".", ",") + " m" 
            except(ValueError):                                     # tritt auf, wenn empfangene HEX nicht nach int() übersetzt werden können
                self.labelSensor["text"] = "Daten fehlerhaft"
        except(Empty):
            if time() - self.timeSinceLastData > 120:               # wenn mehr als 120 sec ohne Datenempfang vergangen sind -> Fehlermeldung
                self.labelSensor["text"] = "Daten fehlen"
        self.after(1, self.updateLabelData)

    def drehScheibe(self):
        self.x0 = 25
        self.y0 = 25
        self.x1 = 225
        self.y1 = 225

        self.strichLaenge = (self.x1 - self.x0)/2
        self.center_x = ((self.x1 - self.x0)/2) + self.x0
        self.center_y = ((self.y1 - self.y0)/2) + self.y0

        self.cv.create_oval(self.x0, self.y0, self.x1, self.y1)
        self.strich = self.cv.create_line(self.center_x, self.center_y, self.center_x, self.center_y) # beim start nur als Punkt

    def positionsStrich(self, wert):
        mappedValue = self.mapping(wert, 0, 5010, 0, 360)
        x = self.strichLaenge * sin(radians(mappedValue)) + self.center_x
        y = self.strichLaenge * cos(radians(mappedValue)) + self.center_y

        self.cv.coords(self.strich, self.center_x, self.center_y, x, y)

    #   mapping entspricht der Funktion map() aus Arduino
    def mapping(self, value, in_min, in_max, out_min, out_max):
        return ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    
    def offsetData(self, data, offset):
        # offsetData ist keine gute Bezeichnung, offset ist besser für die Scheibenwerte (44,06?m)
        if data != self.dataOld:
            if ((data < self.dataOld - offset) | (data > self.dataOld + offset)):
                self.dataOld = data
                return data
            else:
                return self.dataOld
        else:
            return data

    def beenden(self):
        self.server.shutdown()
        self.master.destroy()

if __name__ == "__main__":

    q = Queue()

# Serverstart als eigener Thread ------------------------------------
    HOST, PORT = "", 51456
    server = myUDPServer((HOST, PORT), MyUdpHandler, q)
    serverThread = Thread(target=server.serve_forever)
    serverThread.start()
# Ende Serverstart
    
# Starte Fenster ----------------------------------------------------
    root = Tk()
    fenster = mainWindow(q, server, master=root)
    fenster.mainloop()
# Ende Start Fenster


