import time
import os
from picamera2 import Picamera2 #uvodjenje potrebnih biblioteka

picam2 = Picamera2() #inicijalizacija kamere

save_dir = "/home/sys1/Pictures" #path ka folderu gde se cuvaju slike

def capture_images(interval = 60, total_images = 9999): #definisemo da se slika svakih 60 sekundi a maksimalan broj slika da bude 9999
	picam2.start() #pokrece se kamera
	for i in range(total_images):
		image_name = f"img1_{i:04d}.jpg" #ime slike (fajla)
		image_path = os.path.join(save_dir,image_name) #path do slike
		picam2.capture_file(image_path) #slikanje
		print(f"Captured {image_path}")
		time.sleep(interval) #cekamo 60 sekundi
	picam2.stop() #kamera se zaustavlja

if __name__ == "__main__":
	try:
		capture_images()
	except KeyboardInterrupt: 
		print("Keyboard Interrupt")
	finally:
		picam2.close()