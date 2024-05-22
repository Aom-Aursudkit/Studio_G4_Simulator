#define pwm1 6  //6
#define dir1 7  //7
#define pwm2 9
#define dir2 8

bool checkk(String a) {
  for (int i = 0; i < a.length(); i++) {
    if (isDigit(a.charAt(i))) {
      return true;
    }
  }
  return false;
}

void setup() {
  Serial.begin(9600);
  pinMode(pwm1, OUTPUT);
  pinMode(dir1, OUTPUT);
  pinMode(pwm2, OUTPUT);
  pinMode(dir2, OUTPUT);
  analogWrite(pwm1, 0);
  digitalWrite(dir1, LOW);
  analogWrite(pwm2, 0);
  digitalWrite(dir2, LOW);
  delay(100);
  //////////////////////////////////
  // analogWrite(pwm1, 255);
  // digitalWrite(dir1, LOW);
  // delay(80);
  // analogWrite(pwm1, 255);
  // digitalWrite(dir1, HIGH);
  // delay(100);
  // //////////////////////////////////
  // analogWrite(pwm1, 0);
  // digitalWrite(dir1, LOW);
  // delay(10);
  Serial.println("Ready");
}

void loop() {
  // Serial.print(analogRead(A0));
  // Serial.print("    ");
  // Serial.println(analogRead(A1));
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil(";");
    if (checkk(data) == true) {
      int datanum = data.toInt();
      if (datanum >= 0) {
        // for (int i = 0; i < 10; i++) {
        float volt = 1.2 * datanum;                //r * a(0-21)
        float power = map(volt, 0, 25.2, 0, 255);  //25.2
        Serial.println("Shoot!");
        Serial.print("A = ");
        Serial.println(datanum);
        Serial.print("V = ");
        Serial.println(volt);
        Serial.print("PWM = ");
        Serial.println(power);
        long d = millis();
        while (millis() - d < 200) {
          if (analogRead(A0) > 550) {
            break;
          }
          analogWrite(pwm1, power);
          digitalWrite(dir1, HIGH);
        }
        analogWrite(pwm1, power);
        digitalWrite(dir1, LOW);
        delay(200);
        /////////////////////////////////////
        // d = millis();
        // while (millis() - d < 100) {
        //   if (analogRead(A1) > 580) {
        //     break;
        //   }
        //   analogWrite(pwm1, power);
        //   digitalWrite(dir1, LOW);
        //   analogWrite(pwm2, power);
        //   digitalWrite(dir2, LOW);
        // }
        // analogWrite(pwm1, 0);
        // digitalWrite(dir1, LOW);
        // analogWrite(pwm2, power);
        // digitalWrite(dir2, HIGH);
        // delay(120);
        //////////////////////////////////
        analogWrite(pwm1, 0);
        digitalWrite(dir1, LOW);
        analogWrite(pwm2, 0);
        digitalWrite(dir2, LOW);
        delay(10);
        Serial.println("Ready");
        //////////////////////////////////
        //   analogWrite(pwm1, 0);
        //   digitalWrite(dir1, LOW);
        //   delay(1000);
        //   analogWrite(pwm1, 150);
        //   digitalWrite(dir1, LOW);
        //   delay(200);
        //   analogWrite(pwm1, 0);
        //   digitalWrite(dir1, LOW);
        //   delay(9000);
        // }
      }
    }
    if (checkk(data) == false) {
      // Serial.println("Reset");
      // analogWrite(pwm1, 0);
      // digitalWrite(dir1, LOW);
      // delay(50);
      // analogWrite(pwm1, 50);
      // digitalWrite(dir1, LOW);
      // delay(100);
      // analogWrite(pwm1, 0);
      // digitalWrite(dir1, LOW);
      // delay(50);
      char temp = data[0];
      if (temp == 'z') {
        while (true) {
          Serial.print(analogRead(A0));
          Serial.print("    ");
          Serial.println(analogRead(A1));
          if (Serial.available() > 0) {
            Serial.println("Ready");
            break;
          }
        }
      }
    }
  }
  analogWrite(pwm1, 0);
  digitalWrite(dir1, LOW);
}