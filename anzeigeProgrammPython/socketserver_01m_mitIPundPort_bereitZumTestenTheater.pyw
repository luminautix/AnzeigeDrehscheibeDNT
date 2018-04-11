#socketserverUDP von docs.python.org
from socketserver import BaseRequestHandler, UDPServer
from threading import Thread
from queue import Queue, Empty
from tkinter import Tk, Frame, Label, Canvas
from math import sin, cos, radians

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
        self.master.protocol('WM_DELETE_WINDOW', self.beenden) # beendet, bei Klick auf das Menüzeilenkreuz das Programm sauber
        self.master.title("DNT Scheibenstand")
        self.pack()
        self.cv = Canvas(self, width=250, height=250)
        self.cv.pack()
        self.drehScheibe()
        self.q = q
        self.server = server # notwendig, um 'server' aus dem GUI beenden zu können
        self.message = "keine Daten"
        self.labelData = Label(self, text="Drehbühne Position:")
        self.labelData.pack()
        self.labelSensor = Label(self, font=("", 24), text=self.message)
        self.labelSensor.pack()
        self.updateLabelData()

    def updateLabelData(self):
        try:
            self.message = self.q.get_nowait()
           try:    
                self.meterData = int(self.message[2]) # workarround um führende Nullen zu eliminieren
                if self.meterData != 0:
                    self.meterData = self.meterData / 100
                self.labelSensor["text"] = (str(self.meterData)).replace(".", ",") + " m" 
                self.positionsStrich()
            except(ValueError):             # tritt auf, wenn empfangene HEX nicht nach int() übersetzt werden können
                self.labelSensor["text"] = "Daten fehlerhaft"
        except(Empty):
            pass ## muss noch bearbeitet werden
 
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

    def positionsStrich(self):
        mappedValue = self.mapping(int(self.message[2]), 0, 4450, 0, 360)
        x = self.strichLaenge * sin(radians(mappedValue)) + self.center_x
        y = self.strichLaenge * cos(radians(180 + mappedValue)) + self.center_y

        self.cv.coords(self.strich, self.center_x, self.center_y, x, y)

    #   mapping entspricht der Funktion map() aus Arduino
    def mapping(self, value, in_min, in_max, out_min, out_max):
        return ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

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


