# ELE Kvadar
Projekat "Lansiranje ele kvadra" predstavlja lansiranje malog satelita meteorološkim balonom do visine od 30 km. Cilj je prikupljati podatke, kao što su temperatura, radijacija i atmosferski pritisak. Satelit se zatim na zemlju vraca pomoću padobrana. Dalji procesi ukljucuju nalazenje satelita i analiziranje snimljenih podataka kao i njihovo uporedjivanje sa proslim poznatim rezultatima zvanicnih merenja.

Slika otvorenog satelita pre lansiranja:

![Otvoren satelit pre lansiranja](https://github.com/usern4mehere9/LeninRepo/blob/main/10.jpg)

Slika satelita u vazduhu:

![Satelit u vazduhu](https://github.com/usern4mehere9/LeninRepo/blob/main/8.png)

Slika satelita na mestu gde je pao:

![Satelit na mestu gde je pao](https://github.com/usern4mehere9/LeninRepo/blob/main/9.jpg)

Projekat je rađen na seminaru elektronike u Istraživačkoj stanici Petnica.

## Software

### SYS1

**SYS1** sastoji se od: 
* Raspberry Pi Zero 2W
* Raspberry Pi Camera Module 3

Cilj ovog sistema je prikupljanje slika iz svemira. Ovaj system koristi kod capture_images.py.

Na sys1 nismo zalemili 40-pin GPIO header za Raspberry Pi, jer nam nije bio potreban, pa smo na ovaj način sačuvali na masi celog sistema.

Slike su bile čuvane u jpg formatu pod nazivom img1_XXXX.jpg (XXXX predstavlja redni broj slike, u 4 cifre, počevši od 0000).  Kada se program restartuje, slike se rewrite-ju, tako da imamo sačuvanu poslednju sliku pod tim istim nazivom.

Kamera je postavljena na donju stranu kućišta i programirana da slika na svakih 60 sekundi. Na dan lansiranja, proverena je njena funkcionalnost, a zahvaljujući automatskom fokusu, dodatna podešavanja nisu bila potrebna pre nego što je konačno postavljena u kućište.

Primer slike na dan lansiranja:

![Primer slike na dan lansiranja](https://github.com/usern4mehere9/LeninRepo/blob/main/1.png)

### SYS2

**SYS2** sastoji se od: 
* Raspberry Pi Zero 2W
* Raspberry Pi HQ Camera v1.0
* BMX160
* BMP388
* SIM868 GPS/GSM modul

Cilj ovog sistema je prikupljanje očitavanja senzora, slanje tih podataka kroz poruku i snimanje videa. Koristi kod svepokk.py.

Videe snima u h264 formatu. Čuva ih pod nazivom YY-MM-DD-HH-MM-SS.h264. Format je h264 zato što za to imamo hardverski enkoder pa je najbrže.

Kamera je zalepljena na bočnu stranu kućišta satelita. Napravili smo i da nam radi live stream sa kamere na računaru, što je puno pomoglo pri nameštanju fokusa, jer smo pre toga morali da slikamo i otvaramo slike kako bi proveravali da li je dobar. 

Screenshot snimka dobijenog sa satelita:

![Screenshot snimka dobijenog sa satelita](https://github.com/usern4mehere9/LeninRepo/blob/main/6.jpg)

Korišćen je SIM868 GPS/GSM modul za traženje GPS koordinata, i slanje podataka putem poruke pomoću GSM modula. GPS je testiran više puta. Nakon prvih testiranja po stanici dobijali smo tačnu lokaciju sa greškom od ~6m. Koordinate su stizale na laptop pa je naknadno napisan kod da podaci dolaze na SMS svakih 60 sekundi. Za pravilno funkcionisanje i postizanje potrebne preciznosti bilo je neophodno obavljati testiranja na otvorenom prostoru, s obzirom da uređaj ne radi u zatvorenom. 

Prvi broj u poruci predstavlja datum i vreme, zatim karakterom “;” odvojeno idu gps koordinate odvojene zarezima, nakon toga, razdvojeno “;” idu tri komponente žiroskopa, međusobno odvojene zarezima, nakon toga tri komponente očitavanja akselerometra odvojene zarezima, i zatim dva broja odvojena “;” koji predstavljaju pritisak i temperaturu. Primer poruke: *20240808213841.000;44.246743,19.930845,218.326;0.02, 0.05,-0.03;0.89,0.16,9.35;990.2834;25.96*

Primer izgleda poruke:

![Primer izgleda poruke](https://github.com/usern4mehere9/LeninRepo/blob/main/3.png)

Za sys2 namestili smo čuvanje podataka u json fajl, svako novo merenje bilo je upisivano u novu liniju. To nam je bilo značajno jer prilikom gubitka signala (što bi se desilo u svemiru u nekom trenutku, a nama se desilo čak i pri samom poletanju), ipak bismo mogli da dobijemo te podatke čim pronađemo satelit i preuzmemo fajlove sa SD kartice. U fajl su bila upisivana sva merenja, istim redosledom kao što su bila upisivana u poruku. Fajlovi su nazivani kao data_YYYY-MM-DD-HH-MM-SS.json_file.json, tako da su ti datum i vreme u trenutku pokretanja programa.

Primer izgleda fajla u kom su upisivani podaci:

![Primer izgleda fajla u koji su upisivani podaci](https://github.com/usern4mehere9/LeninRepo/blob/main/2.png)

Namešteno je automatsko pokretanje koda i za sys1 i za sys2. Odnosno, ukoliko se u bilo kom trenutku resetuje rpi, kod će odmah ponovo da se pokrene. 

## SYS6

**SYS6** sastoji se od: 
*	Raspberry Pi Zero 2W sa zalemljenim ipex konektorom za antenu 
*	2 redno vezane litijumske baterije 
*	Eksterna SMA antena 
*	DC na DC konverter za stabilno napajanje od 5V 
*	Ipex na SMA adapter 

Sistem je bio napravljen za praćenje Samsung Galaxy SmartTag2 u toku potrage za satelitom. Bilo je planirano da se postavi na dron u toku potrage.

Slika sistema:

![Slika sistema](https://github.com/usern4mehere9/LeninRepo/blob/main/5.png)

U toku rada isečen je trace za integrisanu antenu i odlemljen kondenzator za napajanje, na čije su mesto zalemljene žice iz DC na DC konvertera. 

Test je odrađen uz pomoć krana, meren je intenzitet signala u odnosu na udaljenost od odašiljača u inkrementima od 3 metra. Korišćen kran je proizveden od strane KONE proizvođača i ima nosivost od 16 tona. Ima radio komandu (daljinski) koji funkcioniše na oko 2.4Ghz. Takođe su u sklopu testa izmerene i maksimalna, minimalna i average (prosečna) potrošnja koristeći unimer.
