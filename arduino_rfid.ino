#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10  // SDA pin
#define RST_PIN 9  // Reset pin

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("RFID Reader Ready");
}

void loop() {
  // Look for new cards
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Read and send the UID
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    // Pad single digit hex values with a leading zero
    if (mfrc522.uid.uidByte[i] < 0x10) {
      uid += "0";
    }
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  
  // Convert to uppercase
  uid.toUpperCase();
  
  // Send just the UID over serial
  Serial.println(uid);

  // Halt PICC and stop encryption
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  
  // Small delay before next read
  delay(1000);
} 