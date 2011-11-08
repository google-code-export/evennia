��    d      <  �   \      �  �  �  �  Q  �    �     �   �  �  �  w  �  
    E   $  E   ]$  C   �$  ?   �$  4   '%  ,   \%  6   �%  g   �%  '   (&  `   P&  .   �&      �&  !   '     #'  -   @'     n'  *   �'  =   �'  A   �'  +   0(  )   \(     �(  0   �(     �(  `   �(  7   W)  8   �)  "   �)  +   �)  !   *  5   9*     o*  q   �*  
   �*  G   +     O+     X+     v+     z+     �+     �+  :   �+  &   �+     ,     ;,  %   N,  \   t,  Q   �,     #-  (   )-     R-  -   f-  
   �-  7   �-  	   �-     �-  \   �-     R.  /   n.  7   �.     �.  `   �.     G/  Z   V/     �/     �/     �/     �/  *   �/  S   (0     |0     �0  #   �0     �0  O  �0  .   !3  ^   P3    �3  F   �4     5  9   &5  +   `5  B   �5      �5  ;   �5  .   ,6     [6  N   z6  6   �6  5    7  +   67  �  b7  �  9  �  �;  N  {B  �   �E  �   �F  �  TG  t  NI  
  �J  ?   �T  I   U  H   gU  M   �U  3   �U  ?   2V  ;   rV  x   �V  $   'W  R   LW      �W     �W  A   �W     !X  /   ;X     kX  ,   �X  B   �X  ?   �X  ,   6Y  %   cY     �Y  (   �Y  %   �Y  d   �Y  :   XZ  H   �Z  2   �Z  1   [     A[  @   a[     �[  {   �[     6\  J   <\     �\     �\  
   �\     �\     �\     �\  F   �\  1   =]     o]     �]  .   �]  Q   �]  V   %^     |^  1   �^     �^  "   �^     �^  H   �^  	   F_     P_  e   h_     �_  A   �_  @   +`     l`  k   �`     �`  Z   �`     Za     ua     �a     �a  0   �a  j   �a     Nb     ab     tb     �b  �  �b      �d  E   �d  �   �d  [   �e     f  3   0f  -   df  R   �f  /   �f  4   g  :   Jg  %   �g  \   �g  M   h  4   Vh  /   �h        [   =       J   I   @   #           Y       ]       &   G   \                         c   a      9   6           2   4   `   W          S   )   %   >   L              F   .   
          R   Z      ?   Q          8      	   _   B   d      b      -      N                    0       !   ^   '   3       +      A       7   X   V   O       $          "          K   U              ;                      ,                     <   T            M   /          (   E   H   *               :   5   D   C          1   P    

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
                                                 (version %s) 

This program launches Evennia with various options. You can access all
this functionality directly from the command line; for example option
five (restart server) would be "evennia.py restart server".  Use
"evennia.py -h" for command line options.

Evennia consists of two separate programs that both must be running
for the game to work as it should:

Portal - the connection to the outside world (via telnet, web, ssh
         etc). This is normally running as a daemon and don't need to
         be reloaded unless you are debugging a new connection
         protocol. As long as this is running, players won't loose
         their connection to your game. Only one instance of Portal
         will be started, more will be ignored.
Server - the game server itself. This will often need to be reloaded
         as you develop your game. The Portal will auto-connect to the
         Server whenever the Server activates. We will also make sure
         to automatically restart this whenever it is shut down (from
         here or from inside the game or via task manager etc). Only
         one instance of Server will be started, more will be ignored.

In a production environment you will want to run with the default
option (1), which runs as much as possible as a background
process. When developing your game it is however convenient to
directly see tracebacks on standard output, so starting with options
2-4 may be a good bet. As you make changes to your code, reload the
server (option 5) to make it available to users.

Reload and stop is not well supported in Windows. If you have issues, log
into the game to stop or restart the server instead. 
 
    ... A new settings file was created. Edit this file to configure
    Evennia as desired by copy&pasting options from
    src/settings_default.py.

    You should then also create/configure the database using

        python manage.py syncdb

    Make sure to create a new admin user when prompted -- this will be
    user #1 in-game.  If you use django-south, you'll see mentions of
    migrating things in the above run. You then also have to run

        python manage.py migrate

    If you use default sqlite3 database, you will find a file
    evennia.db appearing. This is the database file. Just delete this
    and repeat the above manage.py steps to start with a fresh
    database.

    When you are set up, run evennia.py again to start the server. 
    ERROR: Unable to import win32api, which Twisted requires to run.
    You may download it from:

    http://sourceforge.net/projects/pywin32
      or
    http://starship.python.net/crew/mhammond/win32/Downloads.html 
    Edit your new settings.py file as needed, then run
    'python manage syncdb' and follow the prompts to
    create the database and your superuser account.
         
    INFO: Since you are running Windows, a file 'twistd.bat' was
    created for you. This is a simple batch file that tries to call
    the twisted executable. Evennia determined this to be:

       %{twistd_path}s

    If you run into errors at startup you might need to edit
    twistd.bat to point to the actual location of the Twisted
    executable (usually called twistd.py) on your machine.

    This procedure is only done once. Run evennia.py again when you
    are ready to start the server.
     
    Your database does not seem to be set up correctly.

    Please run:
      
         python manage.py syncdb

    (make sure to create an admin user when prompted). If you use
    pyhon-south you will get mentions of migrating in the above
    run. You then need to also run

         python manage.py migrate

    When you have a database set up, rerun evennia.py.
     
+---------------------------------------------------------------------------+
|                                                                           |
|                    Welcome to the Evennia launcher!                       |
|                                                                           |
|                Pick an option below. Use 'h' to get help.                 |
|                                                                           |
+--- Starting (will not restart already running processes) -----------------+
|                                                                           |
|  1) (default):      Start Server and Portal. Portal starts in daemon mode.|
|                     All output is to logfiles.                            |
|  2) (game debug):   Start Server and Portal. Portal starts in daemon mode.|
|                     Server outputs to stdout instead of logfile.          |
|  3) (portal debug): Start Server and Portal. Portal starts in non-daemon  |
|                     mode (can be reloaded) and logs to stdout.            |
|  4) (full debug):   Start Server and Portal. Portal starts in non-daemon  |
|                     mode (can be reloaded). Both log to stdout.           |
|                                                                           |
+--- Restarting (must first be started) ------------------------------------+
|                                                                           |
|  5) Reload the Server                                                     |
|  6) Reload the Portal (only works in non-daemon mode. If running          |
|       in daemon mode, Portal needs to be restarted manually (option 1-4)) |
|                                                                           |
+--- Stopping (must first be started) --------------------------------------+
|                                                                           |
|  7) Stopping both Portal and Server. Server will not restart.             |
|  8) Stopping only Server. Server will not restart.                        |
|  9) Stopping only Portal.                                                 |
|                                                                           |
+---------------------------------------------------------------------------+
|  h) Help                                                                  |
|  q) Quit                                                                  |
+---------------------------------------------------------------------------+
 
Evennia Portal is already running as process %(pid)s. Not restarted. 
Evennia Server is already running as process %(pid)s. Not restarted. 
Starting Evennia Portal in Daemon mode (output to portal logfile). 
Starting Evennia Portal in non-Daemon mode (output to stdout). 
Starting Evennia Server (output to server logfile). 
Starting Evennia Server (output to stdout).     No settings.py file found. launching manage.py ...   A private key 'ssl.key' was already created. Please create %(cert)s manually using the commands valid   Creating SSL key and certificate ...    Evennia's SSL context factory could not automatically create an SSL certificate game/%(cert)s.   Example (linux, using the openssl program):    Generating SSH RSA keypair ...   SSL_ENABLED requires PyOpenSSL.   for your operating system.  %(servername)s Portal (%(version)s) started.  ... Server restarted.  ADMIN_MEDIA_ROOT already exists. Ignored.  Admin-media files copied to ADMIN_MEDIA_ROOT (Windows mode).  Admin-media files should be copied manually to ADMIN_MEDIA_ROOT.  Admin-media symlinked to ADMIN_MEDIA_ROOT.  Creating and starting global scripts ...  Creating default channels ...  Creating objects (Player #1 and Limbo room) ...  Error creating system scripts.  If this error persists, create game/%(pub)s and game/%(priv)s yourself using third-party tools.  Importing MUX help database (devel reference only) ...  Moving imported help db to help category '%(default)s'.  Portal lost connection to Server.  Resuming initial setup from step %(last)s.  Running at_initial_setup() hook.  Server started for the first time. Setting defaults.  Starting in-game time ...  getKeyPair error: %(e)s
 WARNING: Evennia could not auto-generate SSH keypair. Using conch default keys instead.  option >  #1 could not be created. Check the Player/Character typeclass for bugs. %(name)s AMP Error for %(info)s: %(e)s Add Change Do not start Portal process Do not start Server process Evennia Portal stopped in interactive mode. Restarting ... Evennia Server stopped. Restarting ... Evennia database administration Evennia site admin Idle timeout exceeded, disconnecting. If Portal was running in default Daemon mode, it cannot be restarted. In that case you have  If this error persists, create game/%(keyfile)s yourself using third-party tools. Limbo Logged in from elsewhere. Disconnecting. Logged in: %(self)s Models available in the %(name)s application. My Actions No settings.py file found. Run evennia.py to create it. None yet. Not a valid option. Note: Portal usually don't need to be reloaded unless you are debugging in interactive mode. Portal process error: %(e)s Portal reloaded (or stopped if in daemon mode). Portal reloaded (or stopped, if it was in daemon mode). Portal stopped. Process %(pid)s could not be signalled. The PID file '%(pidfile)s' seems stale. Try removing it. Recent Actions Restarting from command line is not supported under Windows. Log into the game to restart. Server process error: %(e)s Server reload. Server reloaded. Server stopped. ServerConfig cannot store db objects! (%s) Start given processes in interactive mode (log to stdout, don't start as a daemon). Stopped Portal. Stopped Server. The %s does not seem to be running. This is User #1. This is the main Evennia launcher. It handles the Portal and Server, the two services making up Evennia. Default is to operate on both services. Use --interactive together with start to launch services as 'interactive'. Note that when launching 'all' services with the --interactive flag, both services will be started, but only Server will actually be started in interactive mode. This is simply because this is the most commonly useful state. To activate interactive mode also for Portal, launch the two services explicitly as two separate calls to this program. You can also use the menu. This operation is not supported under Windows. This operation is not supported under Windows. Log into the game to restart/reload the server. This runner should normally *not* be called directly - it is called automatically from the evennia.py main program. It manages the Evennia game server and portal processes an hosts a threaded loop to restart the Server whenever it is stopped (this constitues Evennia's reload mechanism). Twisted binary for Windows is not ready to use. Please run evennia.py. Unknown content Windows requires Python 2.7 or higher for this operation. You don't have permission to edit anything. mode should be none or one of 'menu', 'start', 'reload' or 'stop'. operation %(op)s not recognized. output portal log to stdout. Does not make portal a daemon. output server log to stdout instead of logfile press <return> to continue ... rsaKey error: %(e)s
 WARNING: Evennia could not auto-generate SSL private key. service should be none or 'server', 'portal' or 'all'. to restart it manually with 'evennia.py start portal' writing mode=%(mode)s to %(portal_restart)s Project-Id-Version: 0.1
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2011-11-03 20:21+0100
PO-Revision-Date: 2011-11-03 22:23+0100
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
                                                 (version %s) 

Detta program startar Evennia med olika funktionalitet. Du kan se alla
functioner direkt från kommandoraden; t.ex så motsvarar val nummer 5
(starta om servern) kommandot "evennia.py restart server" Använd 
"evennia.py -h för att lista alla möjliga kommandon. 

Evennia består av tvp separata program som båda måste vara igång
för att servern ska fungera:

Portal - Kopplingen till omvärlden (via telnet, web, ssh etc). Portalen
         körs vanligen som en "demon" och behöver inte startas om
         såtillvida du inte debuggar ett nytt nätverksprotokoll. Så länge
         Portalen kör så kommer inte spelare att förlora kontakten med
         spelet. Bara en instans av Portalen kan starts p¨ en gång, ytterligare
         instanser kommer att ignoreras
Server - Spelservern själv. Denna kan ofta behöva starts om medan
         du utvecklar ditt spel. Portalen kommer att automatiskt ansluta
         till Servern så fort denna startar. Servern startar också automatiskt
         om så fort den stängs ner (innfrån spelet eller via operativsystemet).
         Bara en instans av Server kan vara igång samtidigt. 

När servern är öppen för allmänheten är det lämpligt att använda val (1)
som innebär att så mycket som möjligt jörs i bakgrunden.
 När man utvecklar sitt spel är det dock bekvämt att direkt se felmeddanden
i terminalen. För detta är val 2-4 bra val. Starta om servern när ny kod är
på plats genom att använda val (5).

Omstart och stopp fungerar inte så bra i Windows. Om du har problem, 
loggin in i spelet och starta om innifrån istället.
 
    ... En ny settings-fil har skapats. Modifiera denna fil för att konfigurera
    Evennia som önskas genom att klippa och klistra från originalet i 
    src/settings_default.py.

    Du bör sedan återskapa databasen med

        python manage.py syncdb

    Se till att skapa ett nytt admin-lösenord när så tillfrågas - detta används
    för användare #1 i spelet. Om nu använder django-south kommer du 
    se ett omnämnande om migrationer efter de ovanstående kommandona.
    Du måste då köra: 
        python manage.py migrate

    Om du använder sqlite3-databasen kommer du att hitta en fil
        evennia.db i game/. Detta är databas-filen. Radera denna fil 
    och upprepa de ovannämnda stegen för att starta om med en 
    ny, tom databas. 

    När allt är klart, kör evennia.py igen rör att starta servern. 
    FEL: Kunde inte importera win32api. Twisted behöver detta.   
    Ladda ner från:

    http://sourceforge.net/projects/pywin32
      eller
    http://starship.python.net/crew/mhammond/win32/Downloads.html 
    Modifiera din nya settings.py fil som du önskar, kör
    sedan 'python manage.py syncdb' och följ instruktionerna
    för att skapa databasen och ditt superuser-konto.
     
    INFO: Efersom du kör Windows har en fil 'twistd.bat' skapats
    Detta är en enkel batch-file som försöker anropa twisted:s
    exeutiva fil. Evennia bedömde att detta är:

       %{twistd_path}s

    Om du stöter på fel under starten så kanske du behöver 
    modifiera twistd.dat så att den hittar Twisted:s binärfil (vanligen
    kallad twistd.py) just på din dator.

    Denna procedur behöver bara göras en gång. Kör evennia.py
    igen när du är redo att starta servern.
     
    Din databas verkar inte korrekt konfigurerad.

    Vänligen kör:
      
         python manage.py syncdb

    (Se till att skapa ett administrationskonto när det tillfrågas.
    Om du använder pyhon-south kommer du att se omnämnande om 
    Se till att då också köra

         python manage.py migrate

    När databasen fungeran, kör evennia.py igen.
     
+---------------------------------------------------------------------------+
|                                                                           |
|                    Välkommen till Evennia!                                |
|                                                                           |
|                Välj nedan. Ge '-h' för att få hjälp.                      |
|                                                                           |
+--- Starta (kommer inte att starta om existerande processer)-------------+
|                                                                           |
|  1) (förvalt):      Start Server och Portal. Portalen startar som demon|n|                     Alla meddelanden till loggfiler                       |
|  2) (spelutveckling): Starta Server och Portal. Portalen startar som    .|
|                     demon. Server meddelar till terminal.                 |
|  3) (portal debug): StartaServer and Portal. Portal startar som           |
|                     icke-demon.                                          |
|  4) (full debug):   StartaServer and Portal. Båda  startar som            |
|                     icke-demon. Båda meddear till terminal.               |
|                                                                           |
+--- Starta om (måste först vara startad)-----------------------------------+
|                                                                           |
|  5) Starta om Server                                                      |
|  6) Starta om Portalen (funkar bara som icke-demon). Om man kör           |
|       som demon så måste Portalen startas om manuellt (val 1-4)           |
|                                                                           |
+--- Stopp (måste först vara startad) --------------------------------------+
|                                                                           |
|  7) Stoppa både Portal och Server. Server startar inte om.                |
|  8) Stoppa bara Server. Server kommer inte att starta om.                 |
|  9) Stoppa bara Portalen.                                                 |
|                                                                           |
+---------------------------------------------------------------------------+
|  h) Hjälp                                                                 |
|  q) Avsluta                                                               |
+---------------------------------------------------------------------------+
 
Evennias portal kör redan som %(pid)s. Behöver inte startas. 
 Evennias Server-process kör redan som %(pid)s. Behöver inte startas.  
Startar Evennias Portal-process som en demon (meddelanden till logfil). 
Startar Evennias Portal-process som icke-demon (meddelanden till terminalen) 
Startar Evennias Server (meddelanden till logfil). 
Startar Evennias Server-process (meddelanden till terminalen).    Filen "settings.py" hittades inte. Startar manage.py ... En privat nyckel 'ssl.key' har redan skapats. Skapa %(cert)s manuellt med hjälp av kommandona för ditt operativsystem. Skapar SSL-nyckel och certifikat ... Evennia's SSL-rutiner kunde inte automatiskt skapa SSL-certifikatet game/%(cert)s. Exempel för Linux, med openssl: Genererar SSH RSA-nyckerlpar.  För att använde SSL_ENABLED måste PyOpenSSL vara installerat.  för ditt operativsystem.  %(servername)s Portal (%(version)s) startades. ... Servern startades om.  ADMIN_MEDIA_ROOT existerar redan. Ignorerar. Admin-media-filer kopierades till ADMIN_MEDIA_ROOT (Windows-läge) Admin-media-filer bör kopieras manuellt till ADMIN_MEDIA_ROOT. Admin-media länkades till ADMIN_MEDIA_ROOT. Skapar och startar globala skript ... Skapar standardkanaler ... Skapar objekt (Spelare #1 och Limbo) ... Fel under skapandet av System-skript. Om detta fel består, skapa game/%(pub)s och game/%(priv)s själv med hjälp av tredjepartsverktyg.  Importerar MUX:s hjälpdatabas (enbart för utvecklare)... Flyttar de importerade hjälpfileran till hjälpkategorin '%(default)s'. Portalen förlorade sin koppling till terminalen.  Startar om uppstarten från steg nummer %(last)s. Kör kroken at_initial_setup(). Servern startades för första gången. Sätter standardvärden. Startar spelets tid ... getKeyPair-fel: %(e)s
VARNING: Evennia kunde inte auomatiskt generera SSH-nyckelparet. Använder standardnycklar istället. val > #1 kunde inte skapas. Kolla efter fel i typklassen för Player/Character.  %(name)s AMP-fel: %(info)s: %(e)s Lägg till Ändra Starta inte Portal-processen Starta inte Server-processen. Evennia:s Portal-process stoppades i interaktivt läge. Startar om ... Evennia:s Serverprocess stoppades. Startar om ... Evennia databas-administration Evennia webside-admin Passivitetstimer överskriden. Kopplas ifrån. Om Portalen kördes som en demon så kan den inte startas om. I såfall måste du Om detta fel består, skapa game/%(keyfile)s själv med hjälp av tredjepartsverktyg.  Limbo Inloggad från någon annanstans. Kopplas ifrån. %(self)s loggade in.  Modeller tillgängliga i %(name)s. Mina Handlingar Ingen settings.py-fil kunde hittas. Kör evennia.py för att skapa den.  Inga än. Inte ett lämpligt val. Obs: Portalen behöver oftast inte startas om såtillvida man inte håller på att debugga portalen.  Portal: Process-fel: %(e)s Portalen startades om (eller stoppades, om den körde some demon) Portalen startades om (eller stoppades om den kördes som demon) Portalen stoppades. Processen %(pid)s kunde inte signaleras. PID-filen '%(pidfile)s' verkar vara ur synk. Ta bort den manuellt. Senaste Handlingar Att starta om från kommandoraden stöds inte under Windows. Logga in för att starta om.  Server: Process-fel: %(e)s Serven laddades om. Servern startades om. Servern stoppades. ServerConfig kan inte lagra databas-objekt! (%s) Starta den angivna processen i interaktivt läge (alla meddelanden till terminalen, starta inte som demon) Stoppade Portalen. Stoppade Portalen. %s verkar inte köra.  Detta är användare #1. Detta är Evennias huvudprogram. Det hanterar Portalen och Servern, de två program so utgör Evennia. Normal verkar alla kommandon på båda programmen. Använd --interactive tillsammans med start för att starta interaktiva lägen. Notera att normalt startar bara Servern i interaktivt läge eftersom detta är det oftast använda läget. För att aktivera interaktivt läge även för Portalen så måste man starta programmen var för sig. Man kan också använde menyn.  Detta stöds inte under Windows. Detta stöds inte under Windows. Logga in för att starta om servern. Detta program bör normalt *inte* anropas direkt - det startas automatiskt från evennia.py. Programmet styr Evennia:s Server- och Portal-processer med hj'lp av en trådbaserad loop som gör att Servern kan startas om.  Twisted:s Windows-binärfil är inte klar att användas. Vänligen kör evennia.py först.  Okänt innehåll Windows kräver Python 2.7 för att utföra detta.  Du har inte tillstånd att ändra någonting. 'mode' (om den anges) måste antingen vara 'menu', 'start', 'reload' eller 'stop'. kommando av typ %(op)s kunde inte kännas igen. Avge Portal-data till stdout. Starta inte som demon. Avge Server-data till stdout istället för till en logfil tryck <retur> för att fortsätta ... rsaKey fel: %(e)s
VARNING: Evennia kunde inte automatiskt generera den privata SSL-nyckeln.  'service' (om den anges) måste antingen vara 'server', 'portal' eller 'all'. starta om den manuellt med 'evennia.py start portal' writing mode = %(mode)s till %(portal_restart)s 