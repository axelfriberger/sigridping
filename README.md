# Sigrid köbevakning för macOS

Dubbelklicka på Starta.command i Finder. Kräver Python 3. Låt terminalfönstret vara öppet. Stoppa med Ctrl+C.

Programmet läser https://sigrid.cs.lth.se/monitor var tionde sekund, hittar rum där axel-1 är handledare och visar en macOS-notis vid nya poster i hjälp- eller redovisningskön. Personnamn visas inte i notiser och ingen köhistorik sparas till disk. Redan väntande personer notifieras vid start.

Testa notiser från den här mappen med `python3 watch.py --test`. Om notisen inte syns: kontrollera macOS notisinställningar för Script Editor/osascript och Fokus. Terminalen visar alltid händelsen också. Notisleverans är inte verifierad på din dator.

Annat handledarnamn: `python3 watch.py --supervisor axel-2`.

Datorn måste vara vaken, ha internet och programmet måste köras. Ingen automatisk start installeras. Poster som både kommer och försvinner mellan kontroller kan missas. Programmet använder monitorns nuvarande felsökningsformat; om sidan ändras kan läsaren behöva uppdateras. Fel visas i terminalen och kontrollerna fortsätter.
