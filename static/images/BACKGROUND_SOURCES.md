# Free Background Images for Magazine Covers

## ⚠️ DÔLEŽITÉ - Formát A4 PORTRAIT (na výšku)

**Požadované rozlíšenie:**
- **Ideálne (pre tlač):** 2480 x 3508 px (300 DPI, A4 portrait)
- **Minimálne (pre web):** 1240 x 1754 px (150 DPI, A4 portrait)  
- **Odporúčané (optimalizované):** 1200 x 1697 px
- **Aspect ratio:** 0.707 (šírka:výška = 21:29.7 cm)

**⚠️ PORTRAIT, nie landscape!** Obrázky musia byť **vyššie ako široké** (výška > šírka)

---

## Odporúčané zdroje (Creative Commons / Free to use):

### 1. Unsplash (https://unsplash.com/)
- Úplne zadarmo pre komerčné aj nekomerčné použitie
- Vysoká kvalita fotografií
- Hľadaj s filtrom: **Portrait orientation**
- Keywords: "magazine cover", "vertical background", "portrait wallpaper"

### 2. Pexels (https://www.pexels.com/)
- Zadarmo bez nutnosti pripísania autora
- Filter: **Portrait orientation**
- Široký výber tém

### 3. Pixabay (https://pixabay.com/)
- Zadarmo, široký výber
- Filter: **Vertical**

---

## Odporúčané témy pre pozadia (všetky PORTRAIT format):

1. **pozadie_1.jpg** - Abstraktné farebné vlny (modrá/fialová gradient)
2. **pozadie_2.jpg** - Minimalistický gradient (ružová/oranžová sunset)
3. **pozadie_3.jpg** - Geometrické vzory (žltá/zelená polygons)
4. **pozadie_4.jpg** - Textúra mramoru (sivá/biela marble)
5. **pozadie_5.jpg** - Mestská panoráma vertikálne (night cityscape)
6. **pozadie_6.jpg** - Príroda - lesná hmla (misty forest vertical)
7. **pozadie_7.jpg** - Abstraktný watercolor (pastelové farby)
8. **pozadie_8.jpg** - Tech/futuristické pozadie (tmavomodrá matrix)
9. **pozadie_9.jpg** - Textúra papiera/vintage (old paper texture)
10. **pozadie_10.jpg** - Dynamický splash effect (colorful paint splash)

---

## Tipy:
✅ **Rozlíšenie:** 1200 x 1697 px minimum (portrait!)
✅ **Formát:** JPG (optimalizovaný pre web, 300-800 KB)
✅ **Orientácia:** PORTRAIT - výška musí byť väčšia ako šírka!
✅ **Čitateľnosť:** Vyhni sa príliš rušivým obrázkom (text musí byť čitateľný)
✅ **Farby:** Tmavšie alebo stredné tóny (pridávame dark overlay 50%)
❌ **Nepoužívaj:** Landscape (na šírku), príliš jasné pozadia, veľmi detailné fotky

---

## Príklad vyhľadávacích výrazov (s "portrait" filtrom):

**Unsplash/Pexels:**
- "vertical abstract background portrait"
- "portrait gradient wallpaper"
- "magazine cover background vertical"
- "dark vertical texture"
- "modern geometric background portrait"
- "minimalist vertical background"
- "elegant portrait background"

**Konkrétne návrhy:**
1. Unsplash: `https://unsplash.com/s/photos/vertical-gradient`
2. Pexels: `https://www.pexels.com/search/portrait%20background/`
3. Pixabay: Vyhľadaj "vertical" + "texture"

---

## Ako upraviť obrázok na správne rozmery:

### Online nástroje (zadarmo):
1. **Photopea** (https://www.photopea.com/) - online Photoshop
   - Open image → Image → Canvas Size → 1200 x 1697 px
   
2. **Canva** (https://www.canva.com/)
   - Custom size: 1200 x 1697 px
   - Nahraj obrázok a crop

3. **iloveimg.com/crop-image**
   - Nastav aspect ratio 21:29.7 alebo priamo 1200 x 1697 px

### Príkazový riadok (ImageMagick):
```bash
# Crop na A4 portrait aspect ratio (center crop)
magick input.jpg -gravity center -crop 1200x1697+0+0 +repage pozadie_1.jpg
```

---

## Kontrolný checklist pred použitím:
- [ ] Obrázok je na **výšku** (portrait)
- [ ] Rozlíšenie minimálne 1200 x 1697 px
- [ ] Formát JPG, veľkosť 300-800 KB
- [ ] Text by bol čitateľný cez dark overlay
- [ ] Obrázok nie je príliš rušivý
- [ ] Uložený ako `pozadie_X.jpg` v `static/images/`
