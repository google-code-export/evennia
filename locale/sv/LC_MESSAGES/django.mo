��    >        S   �      H  �  I  �     g   �  '   +	  `   S	  .   �	      �	  !   
     &
  -   C
     q
  *   �
  =   �
  A   �
  +   3  )   _     �  0   �     �  `   �  7   Z  8   �  "   �  +   �  !     5   <     r  q   �  G   �     G     P     n     r          �     �     �     �     �  V   �     S     [  %   `  Q   �     �  (   �       -     
   I  	   T  @   ^     �     �  *   �     �     �       +         :  N   [  +   �  �  �  �  �  �   ^  x     $   �  R   �           &  A   E     �  /   �     �  ,   �  B     ?   \  ,   �  %   �     �  (   
  %   3  d   Y  :   �  H   �  2   B  1   u     �  @   �       {      J   �     �     �  
   	       %   (     N  (   U     ~     �     �  k   �     (     1  .   5  V   d     �  1   �     �  "   	     ,  	   <  A   F     �     �  0   �     �     �     �  -      /   ;   \   k   /   �                 0                        6       8      )   =                      :      3              -   &      2                            4         $      <      (           	          "       1   /   5             %   9   +   #   '         !   7   ;      *      >          
               .   ,    

    Error: Couldn't import the file 'settings.py' in the directory 
    containing %(file)r. There are usually two reasons for this: 
    1) You moved your settings.py elsewhere. In that case move it back or 
       create a link to it from this folder. 
    2) The settings module is where it's supposed to be, but contains errors.
       Review the traceback above to resolve the problem, then try again. 
    3) If you get errors on finding DJANGO_SETTINGS_MODULE you might have 
       set up django wrong in some way. If you run a virtual machine, it might be worth
       to restart it to see if this resolves the issue. Evennia should not require you 
       to define any environment variables manually. 
     
    Edit your new settings.py file as needed, then run
    'python manage syncdb' and follow the prompts to
    create the database and your superuser account.
           A private key 'ssl.key' was already created. Please create %(cert)s manually using the commands valid   Creating SSL key and certificate ...    Evennia's SSL context factory could not automatically create an SSL certificate game/%(cert)s.   Example (linux, using the openssl program):    Generating SSH RSA keypair ...   SSL_ENABLED requires PyOpenSSL.   for your operating system.  %(servername)s Portal (%(version)s) started.  ... Server restarted.  ADMIN_MEDIA_ROOT already exists. Ignored.  Admin-media files copied to ADMIN_MEDIA_ROOT (Windows mode).  Admin-media files should be copied manually to ADMIN_MEDIA_ROOT.  Admin-media symlinked to ADMIN_MEDIA_ROOT.  Creating and starting global scripts ...  Creating default channels ...  Creating objects (Player #1 and Limbo room) ...  Error creating system scripts.  If this error persists, create game/%(pub)s and game/%(priv)s yourself using third-party tools.  Importing MUX help database (devel reference only) ...  Moving imported help db to help category '%(default)s'.  Portal lost connection to Server.  Resuming initial setup from step %(last)s.  Running at_initial_setup() hook.  Server started for the first time. Setting defaults.  Starting in-game time ...  getKeyPair error: %(e)s
 WARNING: Evennia could not auto-generate SSH keypair. Using conch default keys instead. #1 could not be created. Check the Player/Character typeclass for bugs. %(name)s AMP Error for %(info)s: %(e)s Add Add %(name)s Add another %(verbose_name)s Change Enter a username and password. Evennia database administration Evennia site admin Filter First, enter a username and password. Then you'll be able to edit more Player options. History Home Idle timeout exceeded, disconnecting. If this error persists, create game/%(keyfile)s yourself using third-party tools. Limbo Logged in from elsewhere. Disconnecting. Logged in: %(self)s Models available in the %(name)s application. My Actions None yet. Please correct the error below. Please correct the errors below. Recent Actions Remove ServerConfig cannot store db objects! (%s) This is User #1. Unknown content View on site You don't have permission to edit anything. operation %(op)s not recognized. rsaKey error: %(e)s
 WARNING: Evennia could not auto-generate SSL private key. writing mode=%(mode)s to %(portal_restart)s Project-Id-Version: 0.1
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2012-02-19 10:36+0100
PO-Revision-Date: 2012-02-19 10:45+0100
Last-Translator: Griatch <griatch@gmail.com>
Language-Team: Griatch <griatch@gmail.com>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1)
X-Poedit-Language: Swedish
X-Poedit-Country: Sweden
X-Poedit-SourceCharset: utf-8
 

    Fel: Kunde inte importera filen 'settings.py' från den hårddiskplats som
    innehåller %(file)r. Detta beror vanligtvis på en av två anledningar: 
    1) Du har flyttat settings.py någon annanstans. Flytta tillbaka filen eller länka 
        den hit.
    2) settings.py är där den ska vara men innehåller fel. Läs felmeddelandet ovan
       och fixa till problemet. 
    3) Om du ser ett felmeddelande som nämner DJANGO_SETTINGS_MODULE så 
       är django felkonfigurerat på något vis. Om du kör i en virtuell maskin så kan det
       vara värt att starta om för att se om detta löser problemet. Evennia kräver normalt
       inte att du definierar några miljövariabler manuellt. 
     
    Modifiera din nya settings.py fil som du önskar, kör
    sedan 'python manage.py syncdb' och följ instruktionerna
    för att skapa databasen och ditt superuser-konto.
     En privat nyckel 'ssl.key' har redan skapats. Skapa %(cert)s manuellt med hjälp av kommandona för ditt operativsystem. Skapar SSL-nyckel och certifikat ... Evennia's SSL-rutiner kunde inte automatiskt skapa SSL-certifikatet game/%(cert)s. Exempel för Linux, med openssl: Genererar SSH RSA-nyckerlpar.  För att använde SSL_ENABLED måste PyOpenSSL vara installerat.  för ditt operativsystem.  %(servername)s Portal (%(version)s) startades. ... Servern startades om.  ADMIN_MEDIA_ROOT existerar redan. Ignorerar. Admin-media-filer kopierades till ADMIN_MEDIA_ROOT (Windows-läge) Admin-media-filer bör kopieras manuellt till ADMIN_MEDIA_ROOT. Admin-media länkades till ADMIN_MEDIA_ROOT. Skapar och startar globala skript ... Skapar standardkanaler ... Skapar objekt (Spelare #1 och Limbo) ... Fel under skapandet av System-skript. Om detta fel består, skapa game/%(pub)s och game/%(priv)s själv med hjälp av tredjepartsverktyg.  Importerar MUX:s hjälpdatabas (enbart för utvecklare)... Flyttar de importerade hjälpfileran till hjälpkategorin '%(default)s'. Portalen förlorade sin koppling till terminalen.  Startar om uppstarten från steg nummer %(last)s. Kör kroken at_initial_setup(). Servern startades för första gången. Sätter standardvärden. Startar spelets tid ... getKeyPair-fel: %(e)s
VARNING: Evennia kunde inte auomatiskt generera SSH-nyckelparet. Använder standardnycklar istället. #1 kunde inte skapas. Kolla efter fel i typklassen för Player/Character.  %(name)s AMP-fel: %(info)s: %(e)s Lägg till Lägg till %(name)s Lägg till ett annat %(verbose_name)s Ändra Mata in ett användarnamn och lösenord. Evennia databas-administration Evennia webside-admin Filtrera Mata först in ett användarnamn och lösenord. Sedan kommer du att kunna ändra fler Spelarinställningar. Historia Hem Passivitetstimer överskriden. Kopplas ifrån. Om detta fel består, skapa game/%(keyfile)s själv med hjälp av tredjepartsverktyg.  Limbo Inloggad från någon annanstans. Kopplas ifrån. %(self)s loggade in.  Modeller tillgängliga i %(name)s. Mina Handlingar Inga än. Vänligen korrigera felet nedan. Vänligen korrigera felen nedan. Senaste Handlingar Ta bort ServerConfig kan inte lagra databas-objekt! (%s) Detta är användare #1. Okänt innehåll Se på Websida Du har inte tillstånd att ändra någonting. kommando av typ %(op)s kunde inte kännas igen. rsaKey fel: %(e)s
VARNING: Evennia kunde inte automatiskt generera den privata SSL-nyckeln.  writing mode = %(mode)s till %(portal_restart)s 