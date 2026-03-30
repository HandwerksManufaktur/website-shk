# HandwerksManufaktur – Website

## Dateistruktur

```
WEBSITE/
├── index.html      ← Haupt-HTML-Datei
├── styles.css      ← Alle Styles
├── script.js       ← Animation & JS-Logik
├── images.js       ← Bildpfade (verweist auf images/)
└── images/         ← Alle Bilder (18 Dateien)
    ├── img_noah_full.png
    ├── img_hm_logo_white.png
    └── ...
```

---

## In VS Code einbinden

1. **Alle Dateien herunterladen** (index.html, styles.css, script.js, images.js + images/ Ordner)
2. Dateien in deinen `WEBSITE/` Ordner ziehen
3. In VS Code öffnen → du siehst die Struktur im Explorer links
4. Mit **Live Server** (Erweiterung) lokal testen: Rechtsklick auf `index.html` → *Open with Live Server*

---

## Auf GitHub hochladen

### Option A – GitHub Desktop (einfacher)
1. GitHub Desktop öffnen
2. Dein Repo auswählen
3. Alle neuen Dateien sind als "Changes" sichtbar
4. Commit-Nachricht eingeben z.B. `"Add HandwerksManufaktur website"`
5. **Commit to main** → **Push origin**

### Option B – Terminal
```bash
cd /pfad/zu/deinem/WEBSITE-Ordner
git add .
git commit -m "Add HandwerksManufaktur website"
git push
```

---

## GitHub Pages aktivieren (Website live schalten)

1. Gehe zu deinem Repo auf **github.com**
2. **Settings** → **Pages** (linke Sidebar)
3. Source: **Deploy from a branch**
4. Branch: **main** → Ordner: **/ (root)**
5. **Save** klicken
6. Nach 1-2 Minuten ist die Seite live unter:
   `https://DEIN-USERNAME.github.io/WEBSITE/`

---

## Wichtig

Die Bilder liegen im `images/` Ordner – stelle sicher dass dieser Ordner mit hochgeladen wird, sonst werden Logos und Fotos nicht angezeigt.
