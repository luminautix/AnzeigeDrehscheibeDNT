
boolean stringComplete = false;  // whether the string is complete
boolean newDataReceived = false;
const int barcodeLength = 6;
const int triggerChannel = 4;

int counter = 0;
byte inputByteString[barcodeLength];


void setup() {
  // initialize serial:
  Serial.begin(9600);
  
  pinMode(triggerChannel, OUTPUT);
  digitalWrite(triggerChannel, LOW);
}

void loop() {
  if (stringComplete) {
    for (int z = 0; z < barcodeLength; z++){

      }
    stringComplete = false;

  } // END if(stringComplete)

  digitalWrite(triggerChannel, LOW); // setze Barcodetrigger auf 0V -> Lesebetrieb
  delay(10); // ACHTUNG: ohne dieses Delay funktioniert die 'serialEvent' nicht
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
