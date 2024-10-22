import serial
import os
import subprocess
import time
import board
import sys
import adafruit_bmp3xx
import adafruit_tmp117
import json
import RPi.GPIO as GPIO
sys.path.append('/home/sys2/DFRobot_BMX160/python/raspberrypi')
from DFRobot_BMX160 import BMX160
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from datetime import datetime

#lokacije fajlova
sys.path.append('/home/sys2/DFRobot_BMX160/python/raspberrypi') 
filename1 = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json" #naziv fajla u koji ce se pakovati merenja senzora
f = filename1 

#inicializacija senzora pritiska/temperature bmp388
i2c = board.I2C()
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address = 0x76)
bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2

#inicijalizacija ziroskopa/akcelerometra/magnetnog kompasa[magnetni kompas se ne koristi]
bmx = BMX160(1)
while not bmx.begin():
    time.sleep(2)

#inicializacija kamere
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}) #Podesavanje rezolucije
picam2.configure(video_config)
output_folder = "/home/sys2/Videos"
filename = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.h264" #ime u formatu YY-MM-DD-HH-MM-SS.h264 (.h264 je zato sto za to imamo hardverski enkoder pa je najbrze)
encoder = H264Encoder()


uart = serial.Serial("/dev/serial0", baudrate=115200, timeout=1) # inicializacija UART za GPS/GSM/BT[ne koristi se]

broj_telefona ="0000000000" #Broj telefona za prijemnu stanicu na zemlji

def init_gsm(pin="1111"):	 #funkcija za inicalizaciju gsm koja ukljucuje modul -> proverava da li se ukljucio -> otkljucava sim katricu
    
    GPIO.setmode(GPIO.BCM) #Ovo sluzi da podesi adresiranje pinova
    '''GPIO.setup(11, GPIO.OUT) #Postavljamo pin 11 kao out
    GPIO.output(11, 1) #postavljamo inicijalno stanje na 0
    time.sleep(0.5)  #cekamo stabilizaciju
    GPIO.output(11, 0)	#postavljamo na 1 [pritiskam taster]
    time.sleep(5) #cekamo sekund [drzim taster]
    GPIO.output(11, 1) #postavljamo na 0 [pustam taster]'''
    time.sleep(0.5) 

    #Proveri da li je gsm ziv
    uart.write("AT\r\n".encode())
    time.sleep(1)
    response = uart.read(uart.in_waiting).decode()
    if "OK" not in response:
        return False
    print(uart.readlines())	#Ovo treba da vrati prazan buffer []

    #Otkljucaj SIM karticu
    uart.write(f"AT+CPIN={pin}\r\n".encode())
    time.sleep(1)
    response = uart.read(uart.in_waiting).decode()
    if "OK" not in response:
        return False
    print(uart.readlines()) #Ovo treba da vrati prazan buffer []

    return True

def send_sms(phone_number, message):	#funkcija za slanje poruke koja inicializuje rezim slanja -> kreira poruku za slanje od komande + br.tel. + sadrzaj -> salje na modul 

    #poroveri da li je gsm spreman
    uart.write("AT+CPIN?\r\n".encode())
    time.sleep(1)
    response = uart.read(uart.in_waiting).decode()
    if "+CPIN: READY" not in response:
        return False
    print(uart.readlines())	#Ovo treba da vrati prazan buffer []

    # Sastavi komandu za slanje sms
    uart.write(f'AT+CMGF=1\r\n'.encode())
    time.sleep(1)
    uart.write(f'AT+CMGS="{phone_number}"\r\n'.encode())
    time.sleep(1)
    uart.write(f'{message}\r\n'.encode())
    time.sleep(1)
    uart.write(chr(26).encode())
    time.sleep(1)

    return True

def send_command(command):	#funkcija za slanje komandi GPS/GSM modulu 
    dummy = uart.readlines() 
    uart.write(command.encode() + b'\r\n')
    time.sleep(1)
    response = uart.readlines()
    return response

def make_message(datetime1, res, gyro, accel, bmpp, bmpt):	#funkcija (vise makro) za formatiranje sms poruka
    return datetime1 + ";" + str(res) + ";" + gyro + ";" + accel + ";" + bmpp + ";" + bmpt

init_gsm("1111")

delay = 10


def main():
    try:
        res = send_command('AT+CGNSPWR=1') #Komanda za ukljucenje GPS
        send_sms(broj_telefona, res) #Ovo je tu primazno za debug
        picam2.start_recording(encoder, filename) #zapocinjemo snimanje
        print(f"Kamera je zapocela snimanje") #Ovu poruku za vreme leta necemo ni videti ali je korisna za debug 
        
        while True:
            #Ocitavanje senzora 
            data= bmx.get_all_data() #INU
            res = send_command("AT+CGNSINF") #GPS

            segments = str(res).split(',') #odvajamo rezultat poruke po zarezima da bi mogli da odvojimo datum i vreme i gps koordinate od ostatka teksta koji je potpuno nepotreban
            print(segments)
            if (len(segments) > 4):
            
                datetime1 = (segments[3]) #odvajamo datum i vreme da bi mogli da koristimo posle

                latitude = segments[4] #odvajamo latitudu od ostatka nepotrebnog teksta
                longitude = segments[5] #odvajamo longitudu od ostatka nepotrebnog teksta
                altitude = segments[6] #odvajamo altitudu od ostatka nepotrebnog teksta
                gps = latitude + "," + longitude + "," + altitude #formiramo za ceo gps, da se sve tri koordinate ispisuju zajedno odvojene samo zarezima
                #napomenica: posto gps, ziroskop i akcelerometar imaju tri komponente, svako merenje odvojeno je ; (gps od ziroskopa, ziro od akcelerometra itd.) a unutar jednog od njih brojevi se odvajaju zarezima

                gyro = f"{data[3]:.2f}" +  ", " +  f"{data[4]:.2f}" + "," + f"{data[5]:.2f}" #odvajanje i formatiranje ziroskopa izvucenog iz rezultata senzora (data)
                accel = f"{data[6]:.2f}" + "," +  f"{data[7]:.2f}" + "," +  f"{data[8]:.2f}" #odvajanje i formatiranje akcelerometra izvucenog iz rezultata senzora (data)
                bmpp = f"{bmp.pressure:6.4f}" #formatiranje izmerenog pritiska
                bmpt = f"{bmp.temperature:5.2f}" #formatiranje izmerene temperature
                mes = make_message(datetime1, gps, gyro, accel, bmpp, bmpt) #saljemo funkciji make message da ona pojedinacne segmente odvoji koristeci ;
                print(mes) #printujemo da bi proverili samo da l je sve lepo formatirano

                #struktura za upis u fajl
                data_to_save = {
                    "date&time": datetime1,
                    "gps": gps,
                    "gyro": f"{data[3]:.2f}" +  ", " +  f"{data[4]:.2f}" + "," + f"{data[5]:.2f}",
                    "accel": f"{data[6]:.2f}" + "," +  f"{data[7]:.2f}" + "," +  f"{data[8]:.2f}",
                    "bmpp": f"{bmp.pressure:6.4f}",
                    "bmpt": f"{bmp.temperature:5.2f}"
                }
            else:
                gyro = f"{data[3]:.2f}" +  ", " +  f"{data[4]:.2f}" + "," + f"{data[5]:.2f}" #odvajanje i formatiranje >               
                accel = f"{data[6]:.2f}" + "," +  f"{data[7]:.2f}" + "," +  f"{data[8]:.2f}" #odvajanje i formatiranje >                
                bmpp = f"{bmp.pressure:6.4f}" #formatiranje izmerenog pritiska
                bmpt = f"{bmp.temperature:5.2f}" #formatiranje izmerene temperature
                mes = str(res) + ';' + gyro + ';' + accel + ';' + bmpp + ';' + bmpt
                #struktura za upis u fajl
                data_to_save = {
                    "date&time": "/",
                    "gps": "/",
                    "gyro": f"{data[3]:.2f}" +  ", " +  f"{data[4]:.2f}" + "," + f"{data[5]:.2f}",
                    "accel": f"{data[6]:.2f}" + "," +  f"{data[7]:.2f}" + "," +  f"{data[8]:.2f}",
                    "bmpp": f"{bmp.pressure:6.4f}",
                    "bmpt": f"{bmp.temperature:5.2f}"
                }

            send_sms(broj_telefona, mes) #forma\irana poruka se salje na drugu sim karticu

            #Procedura za upis u fajl
            with open('/home/sys2/data_' + f + '_file.json', 'a') as file: #'a' je da se ne prepisuje fajl nego da se samo dopise kad bude novi poziv
                file.write(json.dumps(data_to_save) + '\n') #dopisujemo nova merenja u novi red
                print("Podaci su uspešno sačuvani u JSON fajlu.") #ovo je za debug

            time.sleep(delay)

    except KeyboardInterrupt:
	#AKO uspemo da ga nadjemo i povezemo se na wifi mozemo da zaustavimo snimanje na normalan nacin
        print("Keyboard interrupt! Zaustavljanje snimanja ")
        picam2.stop_recording()
        picam2.close()
        print("Snimanje zaustavljeno, program ce se zatvoriti [end of output, no further imput is needed].")


if __name__ == "__main__":
    main() 