/* Servo test

Servo to push power button connects to Digital pin 11
Servo to push vibrate button connects to Digital pin 10

Servos run on 6 volt power

*/

#include <Servo.h>

Servo power; 
Servo vibrate;

void setup() {
  power.attach(11);  
  vibrate.attach(10);

  // Position servos 'up'
  power.write(90);
  vibrate.write(90);
  delay(1000);
}

void loop() {

  // Position servos 'down' 
  //this is the to verify that they are moving in the correct direction and that the fingers can reach the button properly
  power.write(180);
  delay(1000);
  vibrate.write(0);
  delay(1000);
}
