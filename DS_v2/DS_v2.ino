#include <SPI.h>        
#include <Ethernet2.h>
#include <EthernetUdp2.h>

IPAddress ip(192, 9, 200, 42);            // Adresse des Ethernet2-Arduino-Controller
byte mac[] = {0x90, 0xA2, 0xDA, 0x10, 0xC0, 0x87}; // MAC des Ethernet2-Arduino-Controller

unsigned int localPort = 50456;             // Port zum auf Leitung hören (Empfangen)
unsigned int destinationPort = 51456;       // Port zum senden der Pakete (Senden)

boolean stringComplete = false;  // whether the string is complete
boolean newDataReceived = false;
const int barcodeLength = 6;
const int triggerChannel = 4;

int counter = 0;
byte inputByteString[barcodeLength];  // Länge des Barcodespeicherplatz = Anzahl der Barcodezeichen

long previousMillis;     // in millis()
long intervalMillis = 30000;    // in millis()

EthernetUDP Udp;          // Eine EthernetUDP Instanz zum Senden und Empfangen von Paketen über UDP

void setup() {
  delay(5000);
  Ethernet.begin(mac, ip); // startet Ethernet mit angegebener MAC und IP
  Udp.begin(localPort); // startet UDP auf angegebenen Port
  // initialize serial:
  Serial.begin(9600);
  pinMode(triggerChannel, OUTPUT);
  digitalWrite(triggerChannel, LOW);

  previousMillis = millis();  
}
// ------------------------------------------------------------------------------------------------------


void loop() {
  if (stringComplete) {

    Udp.beginPacket("192.9.200.255", destinationPort);  // öffne einen Port Broadcast -> ...255
    for (int z = 0; z < barcodeLength; z++){
      Udp.write(inputByteString[z]); 
      }
    Udp.endPacket(); 
    
    stringComplete = false;

  } // END if(stringComplete)

  digitalWrite(triggerChannel, LOW); // setze Barcodetrigger auf 0V -> Lesebetrieb
  delay(250); // ACHTUNG: ohne dieses Delay funktioniert die 'serialEvent' Funktion nicht
}

/* Funktionen Bereich --------------------------------------------------------------------------------------------- */

void serialEvent(){
  while (Serial.available()){
    digitalWrite(triggerChannel, HIGH); // setze Barcodetrigger auf 5V
    byte readBarcode = Serial.read();
    if (readBarcode == 13){
      // ASCII 13 entspricht dem '\n'
      // die Endsequenz ist 13 10, also '\n' '\t', also Line Feed und Carriage Return
      // die Sequenz beginnt mit ASCII 2, also 'Start of Text'

      // TODO - zyklisches Senden wenn sich Daten nicht ändern, nach gewisser Zeitspanne (vielleicht 30s ?) 
      if ((newDataReceived != true) && ((millis() - previousMillis) > intervalMillis)){
        previousMillis = millis();
        stringComplete = true;
        }
        
      // SENDEN freigeben - Daten haben sich geändert      
      if (newDataReceived == true){
        stringComplete = true;
        newDataReceived = false;
        }

      counter = 0;      
      }
    else {
      if ((readBarcode > 47) && (readBarcode < 58) && (counter > 2)){
        // die ASCII-Zahlen beginnen bei 48 (= 0) bis 57 (= 9)
        if (inputByteString[counter - 3] != readBarcode){
          inputByteString[counter - 3] = readBarcode;
          newDataReceived = true;
        }
      }
    }
    counter++;
  }
}
