---
name: slide-builder-ver2
description: Slide builder ver 2 — Kimi-style full design system: layout intelligence (A–M), Content Zone Budget, per-section color rotation, glassmorphism card, icon-grid, timeline, quote layouts. VTI mode với extended palette 7 màu + tinted cards + multi-stop gradient. Footer embedded (logo do user tự thêm), badge OOXML, spell-check. Output: PPTX. HTML deck → dùng skill slide-html-deck.
---

## When to use
Dùng khi user yêu cầu tạo slide mới hoặc build deck từ dàn ý. Kích hoạt bằng `/slide-builder-ver2` hoặc đề cập "slide-builder ver2".

---

## Model Routing (TỰ ĐỘNG — không hỏi user)

| Task | Độ nặng | Model |
|---|---|---|
| A — Elicitation + plan + layout selection | Nhẹ | **Haiku 4.5** |
| B — Layout calc (EMU positions, Content Zone Budget) | Trung bình | **Sonnet 4.6** |
| C — edit_slide_xml (OOXML build từ layout spec) | Nặng | **Sonnet 4.6** |
| E — Spell check | Trung bình | **Sonnet 4.6** |
| F — verify_slides (chỉ khi có lỗi) | Nhẹ | **Haiku 4.5** |

**Nguyên tắc:**
- Haiku 4.5 → hỏi user, xác nhận, verify (chỉ khi báo lỗi).
- Sonnet 4.6 → tính EMU, build OOXML, spell check.
- AI tự chọn model, KHÔNG thông báo lên user trừ khi có lỗi.
- **Claude Design sub-agent đã bỏ** — Sonnet tự xử lý composition dựa trên Content Zone Budget.
- `verify_slide_visual` **bỏ khỏi happy path** — chỉ dùng khi verify_slides báo lỗi.
- Logo do user tự thêm thủ công — skill không tự inject logo.
- **HTML deck không thuộc skill này** → dùng skill `slide-html-deck`.

---

## Step 1 — Elicitation (BẮT BUỘC trước khi build) — [Haiku 4.5]

Hỏi bằng `ask_user_question` trong **một lần**:

- Q1: Theme → 🌙 Tối (Dark) | ☀️ Sáng (Light) | 🔵 VTI
- Q2: Ngôn ngữ → 🇻🇳 Tiếng Việt | 🇯🇵 Tiếng Nhật
- Q3: Nội dung → 📝 Có (paste ngay) | 💡 Chưa (mô tả chủ đề)

**Sau khi nhận đủ Q1+Q2+Q3:**
- ✅ Xác nhận ngắn gọn: `"Đã nhận: [Dark/Light/VTI], [VI/JP], nội dung [có/chưa]. Bắt đầu build."`
- **KHÔNG** hiển thị lại bảng Color System cho user.
- Nếu Q3 = "Chưa", yêu cầu user paste nội dung hoặc mô tả chủ đề, sau đó tiếp tục build ngay.
- Muốn output HTML thay vì PPTX → dùng skill `slide-html-deck`.

---

## Step 2 — Color System (NỘI BỘ — AI tự dùng, không hiển thị cho user)

### 🌙 Dark Theme

| Role | Hex | Gradient to |
|---|---|---|
| Slide bg | `#1C1C2E` | `#12121F` |
| Card bg | `#252538` | `#2E2E4A` |
| Glass card border | `#4A4A6A` opacity 40% | — |
| Title | `#E0E2E5` | — |
| Accent | `#D4A26A` | `#C08040` |
| Alt accent | `#8DAAC2` | — |
| Accent 3 (teal) | `#5EC4B0` | — |
| Body | `#D8DAE0` | — |
| Badge primary (60%) | `#D4A26A` | — |
| Badge alt (30%) | `#8DAAC2` | — |
| Separator | `#3A3A5A` | — |
| Stat highlight | `#D4A26A` | — |
| Muted text | `#8A8CA0` | — |
| Decor shape | `#2E2E50` | — |

**Dark section color rotation** (xoay theo section index, reset mỗi deck):
```
Section 0: accent=#D4A26A, alt=#8DAAC2  (gold/blue)
Section 1: accent=#8DAAC2, alt=#5EC4B0  (blue/teal)
Section 2: accent=#5EC4B0, alt=#D4A26A  (teal/gold)
Section 3: repeat từ Section 0
```

### ☀️ Light Theme

| Role | Hex | Gradient to |
|---|---|---|
| Slide bg | `#F5F4F0` | `#ECEAE4` |
| Card bg | `#FFFFFF` | `#F0EEE8` |
| Glass card border | `#C0B8A8` opacity 35% | — |
| Title | `#1A1A2E` | — |
| Accent | `#3B6FA0` | `#2A5080` |
| Alt accent | `#C06030` | — |
| Accent 3 (teal) | `#2A9080` | — |
| Body | `#2E2E3A` | — |
| Badge primary (60%) | `#3B6FA0` | — |
| Badge alt (30%) | `#C06030` | — |
| Separator | `#A3B5B8` | — |
| Stat highlight | `#3B6FA0` | — |
| Muted text | `#8A9BAD` | — |
| Decor shape | `#E8E4DC` | — |

**Light section color rotation:**
```
Section 0: accent=#3B6FA0, alt=#C06030  (blue/orange)
Section 1: accent=#C06030, alt=#2A9080  (orange/teal)
Section 2: accent=#2A9080, alt=#3B6FA0  (teal/blue)
Section 3: repeat từ Section 0
```

### 🔵 VTI Theme — EXTENDED DESIGN (Art-level, 7-color palette)

> **VTI ver2 philosophy:** Không chỉ dùng brand colors đơn thuần. Mỗi card được tinted riêng, accent bar dùng multi-stop gradient, decor shapes tạo visual depth. Kết quả: professional nhưng sống động.

**7-color extended palette VTI:**
| Slot | Tên | Hex | Dùng cho |
|---|---|---|---|
| P1 | Navy | `#172759` | Title, heading chính |
| P2 | Royal Blue | `#2362B0` | Badge primary, accent bar |
| P3 | Sky Blue | `#4A9EE0` | Card tint A, icon fill |
| P4 | Green | `#7FC236` | Badge alt, CTA accent |
| P5 | Teal | `#1E9E8A` | Card tint B, stat highlight |
| P6 | Amber | `#E8A020` | Card tint C, data callout |
| P7 | Coral | `#E05060` | Card tint D, warning/alert |

**VTI Tinted Card System** (dùng pastel version của P2–P7):
```
Card tint A (Sky):   bg=EBF4FC→D6EAF8, border-top=4A9EE0
Card tint B (Teal):  bg=E8F7F4→D0EEE9, border-top=1E9E8A
Card tint C (Amber): bg=FEF6E7→FDE9C0, border-top=E8A020
Card tint D (Coral): bg=FDEEF0→FAD4D8, border-top=E05060
Card tint E (Navy):  bg=EAF0FA→D5E2F5, border-top=2362B0
Card tint F (Green): bg=F0F9E5→DDF0C0, border-top=7FC236
```
**Rotation rule:** Card 1→A, 2→B, 3→C, 4→D, 5→E, 6→F (cycle, per-slide reset).

**VTI Core color roles:**
| Role | Hex | Gradient to |
|---|---|---|
| Slide bg | `#FFFFFF` | `#EEF4FB` |
| Title | `#172759` | — |
| Body | `#1C2D4F` | — |
| Separator | `#B8D0EE` | — |
| Muted text | `#6A7FA0` | — |
| Decor shape A | `#EBF4FC` | `#D6EAF8` |
| Decor shape B | `#E8F7F4` | `#D0EEE9` |

**VTI Multi-stop Gradient presets:**
```
Accent bar (cover/section): P2(2362B0) → P3(4A9EE0) → P4(7FC236), ang=5400000
Accent bar (content slide): P2(2362B0) → P4(7FC236), ang=5400000
Cover left bar: P1(172759) → P2(2362B0), ang=0
Section divider bg: P1(172759) → 1A3070, ang=9000000
CTA bg: P2(2362B0) → P1(172759), ang=16200000
Card bg default: FFFFFF → EEF4FB, ang=16200000
Stat block bg: P2(2362B0) opacity 10% tint → EBF4FC
```

**VTI Section color rotation** (theo section index):
```
Section 0: badge=P2(2362B0), alt=P4(7FC236), stat=P5(1E9E8A)
Section 1: badge=P5(1E9E8A), alt=P3(4A9EE0), stat=P6(E8A020)
Section 2: badge=P4(7FC236), alt=P6(E8A020), stat=P2(2362B0)
Section 3: repeat từ Section 0
```

---

## Step 3 — Font System (CRITICAL) — [Sonnet 4.6]

### 🇻🇳 Tiếng Việt → Arial (KHÔNG Liter/Quattrocento)

```xml
<a:rPr lang="vi-VN" sz="1600" b="0" dirty="0">
  <a:solidFill><a:srgbClr val="2E2E3A"/></a:solidFill>
  <a:latin typeface="Arial" pitchFamily="34" charset="0"/>
  <a:ea typeface="Arial" pitchFamily="34" charset="-122"/>
  <a:cs typeface="Arial" pitchFamily="34" charset="-120"/>
</a:rPr>
```
Body line spacing: `spcPct val="140000"`. Tránh ALL CAPS.

### 🇯🇵 Tiếng Nhật → Arial + Yu Gothic

```xml
<a:rPr lang="ja-JP" sz="1600" dirty="0">
  <a:solidFill><a:srgbClr val="D8DAE0"/></a:solidFill>
  <a:latin typeface="Arial" pitchFamily="34" charset="0"/>
  <a:ea typeface="Yu Gothic" pitchFamily="34" charset="-122"/>
  <a:cs typeface="Yu Gothic" pitchFamily="34" charset="-120"/>
</a:rPr>
```
Body line spacing: `spcPct val="160000"`.

---

## Step 3b — bodyPr chuẩn (BẮT BUỘC mọi txBody) — [Sonnet 4.6]

> **Root cause của text tràn viền:** Skill cũ dùng `<a:bodyPr anchor="ctr"/>` trần — không có wrap rule, không có inset, không có autofit. Text vượt boundary khi dài.

**Kimi bodyPr template — dùng cho MỌI text shape:**

```xml
<!-- ── CARD / BULLET TEXT (body content) ── -->
<a:bodyPr wrap="square"
          lIns="152400" rIns="152400"
          tIns="114300" bIns="114300"
          anchor="t" anchorCtr="0">
  <a:normAutofit/>
</a:bodyPr>

<!-- ── TITLE / HEADING (1 dòng, không wrap) ── -->
<a:bodyPr wrap="none"
          lIns="0" rIns="0"
          tIns="0" bIns="0"
          anchor="ctr" anchorCtr="1">
  <a:noAutofit/>
</a:bodyPr>

<!-- ── BADGE NUMBER / STAT NUMBER (centered, no overflow) ── -->
<a:bodyPr wrap="square"
          lIns="0" rIns="0"
          tIns="0" bIns="0"
          anchor="ctr" anchorCtr="1">
  <a:normAutofit/>
</a:bodyPr>
```

**Giải thích tham số:**
```
wrap="square"    → text bọc trong bounds của shape (KHÔNG tràn ra ngoài)
lIns/rIns        → left/right inset = 152400 EMU (12pt) — breathing room
tIns/bIns        → top/bottom inset = 114300 EMU (9pt)
anchor="t"       → text bắt đầu từ trên xuống (không bị lệch khi ít text)
anchorCtr="0"    → không center vertically (dùng "1" + anchor="ctr" chỉ cho badge/stat)
normAutofit      → tự giảm font size nếu text dài hơn card — KHÔNG cắt, KHÔNG overflow
noAutofit        → giữ nguyên size (dùng cho title — nếu dài thì rút gọn text thủ công)
```

**Quick reference — inset theo use case:**
| Shape | lIns | rIns | tIns | bIns | anchor |
|---|---|---|---|---|---|
| Card content | 152400 | 152400 | 114300 | 114300 | t |
| Card header text | 152400 | 152400 | 76200 | 76200 | ctr |
| Badge/stat number | 0 | 0 | 0 | 0 | ctr |
| Slide title | 0 | 0 | 0 | 0 | ctr |
| Footer text | 76200 | 76200 | 0 | 0 | ctr |

| Role | sz | pt |
|---|---|---|
| Cover title | `6400–7200` | 64–72 |
| Section title | `5000–5400` | 50–54 |
| Slide title | `3200–3600` | 32–36 |
| Card header | `2000–2400` | 20–24 |
| Sub-header | `1600–1800` | 16–18 |
| Body/bullet | `1400–1600` | **14–16 (floor)** |
| Breadcrumb | `1200–1400` | 12–14 |
| Badge number | `1600–1800` | 16–18 |
| Stat big number | `5600–6400` | 56–64 |
| Stat label | `1400–1600` | 14–16 |
| CTA heading | `2800–3200` | 28–32 |

---

## Step 4b — Layout Calc & Color Selection (Sonnet 4.6 tự xử lý)

> **Claude Design sub-agent đã bỏ** — gọi show_widget không ổn định trong thực tế và tốn thêm 1 tool call/slide. Sonnet 4.6 tự tính toán đủ dựa trên Content Zone Budget (Step 5.0) và Color System (Step 2).

Sau khi biết layout type + content, Sonnet tự xác định:
1. **Zones** → dùng trực tiếp từ Step 5.0 CONTENT ZONE BUDGET + layout spec
2. **Icons** → dùng `buildIcon()` (Pattern 5) — OOXML shapes stroke-only, màu = card.border_color
3. **Colors** → dùng rotation table Step 2 theo section index + card index

Không cần Design Brief, không cần DESIGN_SPEC JSON. Tiến thẳng sang Step 6 (OOXML build).

---

## Step 5 — Layout Intelligence (KIMI-STYLE — QUAN TRỌNG)

### 5.1 — Content Analysis (BẮT BUỘC trước khi chọn layout)

Trước khi build mỗi slide, AI phân tích loại nội dung:

| Loại nội dung | Dấu hiệu | Layout phù hợp |
|---|---|---|
| Danh sách/liệt kê (3–4 items, mỗi item có mô tả) | Bullet list, features | **Layout A — Card Grid** |
| Danh sách (5–6 items ngắn) | Nhiều mục, mỗi mục ngắn | **Layout B — 2-Column List** |
| Quy trình / luồng tuyến tính | "Bước 1..2..3", arrows | **Layout C — Flow Steps** |
| So sánh / đối lập 2 phía | "vs", "before/after" | **Layout D — Two-Column Contrast** |
| Số liệu / thống kê / KPI | Số lớn, %, dashboard | **Layout E — Data Highlight** |
| Narrative / giới thiệu dài | Đoạn văn, context | **Layout F — Left-Text Right-Visual** |
| Chuyển chương | Section break | **Layout G — Section Divider** |
| Kết thúc / hành động | "Next steps", CTA | **Layout H — CTA Slide** |
| Cover | Slide đầu tiên | **Layout I — Cover** |
| Mục lục | TOC, agenda | **Layout J — TOC** |
| Sự kiện / mốc thời gian | "Q1..Q2..", milestones | **Layout K — Timeline** |
| Features / icon list (6–8 items ngắn) | Icon + label, service list | **Layout L — Icon Grid** |
| Trích dẫn / insight mạnh | Quote, key message, "big idea" | **Layout M — Quote Highlight** |

**Quy tắc:** AI KHÔNG được dùng Card Grid cho mọi slide — PHẢI chọn layout phù hợp. Ưu tiên variety: 1 deck không nên có >3 slides dùng cùng layout.

---

### 5.0 — CONTENT ZONE BUDGET (BẮT BUỘC tính trước khi đặt shapes)

**Tọa độ cố định (EMU) cho mọi content slide (Layout A–M trừ Cover/Section/CTA):**

```
SLIDE_H        = 6858000 EMU  (540pt)   ← 540 × 12700
SLIDE_W        = 12192000 EMU (960pt)   ← 960 × 12700  ⚠️ KHÔNG phải 9144000

MARGIN_X       = 254000  EMU  ( 20pt)   ← left/right margin
CONTENT_X      = 254000  EMU  ( 20pt)   ← x_start content
CONTENT_W      = 11684000 EMU (920pt)   ← SLIDE_W - 2×MARGIN_X
ACCENT_BAR_Y   = 1079550 EMU  ( 85pt)   ← dưới title
CONTENT_TOP    = 1333500 EMU  (105pt)   ← y_start zone nội dung
CONTENT_BOTTOM = 6096000 EMU  (480pt)   ← y_end an toàn
CONTENT_H      = 4762500 EMU  (375pt)   ← CONTENT_BOTTOM − CONTENT_TOP
FOOTER_Y       = 6375400 EMU  (502pt)   ← footer, KHÔNG chặn content
```

> ⚠️ **1pt = 12700 EMU** — áp dụng nhất quán. Khi layout spec viết "x=500pt" → EMU = 500 × 12700 = 6350000.

**Rule tính card height — Stretch-to-fill (Kimi style):**
```
CARD_GAP    = 127000 EMU (10pt) — khoảng cách giữa cards
n_cards     = số cards trong slide

card_h = (CONTENT_H - CARD_GAP × (n_cards − 1)) / n_cards  ← LUÔN fill đầy zone

Ví dụ:
  2 cards → card_h = (4762500 - 127000)   / 2 = 2317750 EMU (~182pt) ✓
  3 cards → card_h = (4762500 - 254000)   / 3 = 1502833 EMU (~118pt) ✓
  4 cards → card_h = (4762500 - 381000)   / 4 = 1095375 EMU ( ~86pt) ← tối thiểu
  card_y[i] = CONTENT_TOP + i × (card_h + CARD_GAP)
```

**Rule tính card width — horizontal layout:**
```
n_cols      = số cột cards ngang (1, 2, 3, 4)
COL_GAP     = 127000 EMU (10pt)

card_w = (CONTENT_W - COL_GAP × (n_cols − 1)) / n_cols
card_x[j] = CONTENT_X + j × (card_w + COL_GAP)

Ví dụ (Layout A — 3 cards ngang):
  card_w = (11684000 - 254000) / 3 = 3810000 EMU (300pt) ✓
  card_x: 254000 | 4318000 | 8382000
```

> **Kimi stretch rule:** Cards LUÔN fill từ CONTENT_TOP đến CONTENT_BOTTOM. Không có khoảng trống cuối slide. Nếu ít content → card to hơn, padding nhiều hơn — vẫn đẹp hơn slide có vùng trắng.

**Decor shapes (Pattern 8) — giới hạn overflow:**
```
x/y PHẢI nằm trong [0 .. SLIDE_W] × [0 .. SLIDE_H]
Nếu shape lớn → center trong slide, KHÔNG đặt tại tọa độ âm
Chỉ dùng decor cho layout Full-BG (G, H, I) — KHÔNG thêm mặc định vào A–F, J–M
```

---

### Layout A — Card Grid (3–4 items có mô tả)
```
Breadcrumb y=20pt + Title y=40pt + Accent bar y=85pt + Logo top-right
Cards y=105pt→480pt (Stretch-to-fill, card_h = CONTENT_H/n_cards):
  CONTENT_X=20pt, CONTENT_W=920pt
  3 cards ngang: card_w=(920-20)/3=300pt, gap=10pt
    card_x: 20pt | 330pt | 640pt   (EMU: 254000 | 4191000 | 8128000)
  2 cards ngang: card_w=(920-10)/2=455pt, gap=10pt
    card_x: 20pt | 485pt            (EMU: 254000 | 6159500)
  Card: roundRect adj=16667 + tinted bg (VTI) hoặc gradient (Dark/Light)
        top border 5pt accent + Card Badge Pattern 3 + header + dot bullets
        bodyPr: wrap="square" lIns=152400 rIns=152400 tIns=114300 bIns=114300 normAutofit
  VTI: mỗi card dùng tint khác nhau (A→B→C)
Content density: max 3 bullets/card × 2 dòng
```

### Layout B — 2-Column List (5–6 items)
```
Breadcrumb y=20pt + Title y=40pt + Accent bar y=85pt + Logo top-right
Left col:  x=20pt,  w=440pt  (EMU x=254000,  cx=5588000)
Right col: x=480pt, w=440pt  (EMU x=6096000, cx=5588000)
Vertical separator x=460pt (EMU=5842000), h=375pt (Stretch — Pattern 4)
Mỗi item: Badge Pattern 1 (số, xen kẽ primary/alt) + text bên phải
Row gap: 72pt (6 items/col tối đa); bodyPr wrap="square" normAutofit
VTI: badge màu xoay P2→P5→P4→P2...
```

### Layout C — Flow / Steps (quy trình)
```
Breadcrumb y=20 + Title y=40 + Accent bar y=85 + Logo top-right
Steps y=120→450:
  Horizontal flow (≤4 steps): step w=(960-gaps)/n
    Step box: roundRect + Badge Pattern 1 top-center + header + mô tả ngắn
    Arrow connector: Pattern 6 (rightArrow, muted color)
    VTI: step box tint A/B/C/D xen kẽ
  Vertical flow (5+ steps): badge left + text right, step h=70pt
  Decor: faint arc shape Pattern 8 phía sau step boxes
```

### Layout D — Two-Column Contrast (so sánh)
```
Breadcrumb y=20pt + Title y=40pt + Accent bar y=85pt + Logo top-right
Left card:  x=20pt,  w=445pt (EMU cx=5651500) — roundRect + top border P2/Accent
Right card: x=475pt, w=445pt (EMU x=6032500, cx=5651500) — roundRect + top border P4/AltAccent
Gap=10pt (EMU=127000) giữa 2 cards
Center "VS": x=460pt, y=mid, sz=2400, muted
Cards Stretch: y=105pt→480pt (card_h=CONTENT_H=375pt, fill full zone)
bodyPr: wrap="square" lIns=152400 rIns=152400 tIns=114300 bIns=114300 normAutofit
VTI: left=tint E (navy), right=tint F (green)
```

### Layout E — Data Highlight (số liệu / KPI)
```
Breadcrumb y=20 + Title y=40 + Accent bar y=85 + Logo top-right
Stat blocks y=130→350 (2–4 stats horizontal):
  Per stat: Big number sz=5600–6400, stat highlight color, bold
            Unit label sz=2000 bên phải (%, K, M, +)
            Stat label sz=1400 muted bên dưới
            Stat card bg: roundRect, VTI dùng tint theo index (A/B/C/D)
  Separator vertical Pattern 4 giữa stats
Context box y=370→490: roundRect + summary text 14pt
VTI: stat 1=P2 số, stat 2=P5 số, stat 3=P4 số, stat 4=P6 số
```

### Layout F — Left-Text Right-Visual (narrative)
```
Breadcrumb y=20 + Title y=40 + Accent bar y=85 + Logo top-right
Left panel x=20, w=480: body text 16pt, line spacing 160%
  Dot bullets Pattern 2 nếu có list
Right panel x=520, w=420: roundRect card (VTI: tint A)
  Hero icon Pattern 5 (≥48pt, centered) hoặc stat callout
Decor shape Pattern 8 (arc/ellipse mờ) góc dưới phải
```

### Layout G — Section Divider (chuyển chương)
```
Full-slide BG gradient (theo theme):
  Dark: 1C1C2E→12121F
  Light: F5F4F0→ECEAE4
  VTI: 172759→1A3070 (navy gradient đậm, đảo ngược từ slide thường)
Left bar: x=0, w=101600(8pt), h=540, accent gradient (multi-stop VTI)
Section number: sz=12000–14400, muted/light, y=160
Section title: sz=5000–5400, title color, y=280
Subtitle: sz=1800–2000, body, y=370
Right panel x=600→960: roundRect card bg (VTI: tint theo section index) + hero icon Pattern 5 ≥64pt
Decor shape Pattern 8 (large faint ellipse) góc bottom-right
Logo top-right, KHÔNG breadcrumb/accent bar ngang
```

### Layout H — CTA / Next Steps (kết thúc)
```
Full-slide BG: VTI=2362B0→172759 (gradient mạnh), Dark=12121F→1C1C2E, Light=ECEAE4→F5F4F0
Center zone y=160→380:
  Heading: sz=2800–3200, white (VTI/Dark) hoặc accent (Light), centered
  Action items: 2–3 items horizontal, Badge Pattern 1 + text 2 dòng
    VTI: badge 1=P4(green), badge 2=P3(sky), badge 3=P5(teal)
  Divider y=420: Pattern 4 horizontal, w=200pt, muted/white-30%
Footer: sz=1400, muted/white-50%, y=450, centered
Decor: 2 faint circle shapes Pattern 8 (large, bg+10% opacity) corners
Logo top-right
```

### Layout I — Cover (slide 1 bắt buộc)
```
BG: full gradient theo theme
VTI cover BG đặc biệt:
  Main: FFFFFF→EEF4FB (light)
  Left bar x=0, w=8pt, h=540: gradient P1→P2 (navy→blue, ang=0, vertical)
  Right decorative strip x=820, w=140, h=540: gradient P2→P3 (mờ, opacity 30%)

Nội dung: Tag y=48 12pt bold P2 | Title y=80 64–72pt P1
  Divider bar y=285 w=120 h=5 gradient P2→P4 (accent multi-color)
  Subtitle y=305 24–28pt P1-70% | Caption y=415 12pt muted

Right panel x=660→960:
  roundRect card (VTI: tint A) + hero icon Pattern 5 ≥80pt (color P2)
  Decor: small ellipse Pattern 8 trong card corner (P4 mờ)
Logo top-right
```

### Layout J — TOC (mục lục)
```
Breadcrumb y=22 + Title y=44, 36–40pt + Accent bar y=90
Vertical separator x=480, w=2, h=380 (Pattern 4)
2-column badge list (left x=20, right x=500), row gap=90pt:
  Badge Pattern 1 (số) + Title 22pt bold + Slide range 14pt muted
  VTI: badge xoay P2→P5→P4→P2...
Logo top-right
```

### Layout K — Timeline (sự kiện / mốc)
```
Breadcrumb y=20 + Title y=40 + Accent bar y=85 + Logo top-right
Timeline spine: rect horizontal y=270, x=40→920, h=4pt, gradient P2→P4 (VTI) hoặc accent→alt (D/L)
Events (3–5 milestones):
  Dot: ellipse 20pt (Pattern 2 size up: 254000 EMU) trên spine, accent color
  Event card: roundRect w=140pt, h=120pt
    Alternating: odd→y=110 (above spine), even→y=310 (below spine)
    Connector line: rect w=2pt, h=40pt, muted, từ dot lên/xuống card
    Card nội dung: date/label 12pt muted + event name 14pt bold + mô tả 12pt
  VTI: card odd=tint A, even=tint B, dot xoay P2/P5
```

### Layout L — Icon Grid (features 6–8 items)
```
Breadcrumb y=20 + Title y=40 + Accent bar y=85 + Logo top-right
Grid 2 hàng × 3–4 cột, cells y=105→490:
  Cell w≈280pt, h≈170pt (3-col) hoặc w≈210pt (4-col), gap=10pt
  Cell: roundRect bg (VTI: tint cycle A→F) + hero icon Pattern 5 top-center 36pt
        Label sz=1800 bold center + sub-label sz=1400 muted center (optional)
  VTI: icon color = card tint border color (P3/P5/P6...)
  Dark/Light: icon color = accent, alt xen kẽ
Density: 6 cells = 2×3, 8 cells = 2×4; text max 2 dòng/cell
```

### Layout M — Quote / Highlight (trích dẫn, key message)
```
Breadcrumb y=20 + Title y=40 + Accent bar y=85 + Logo top-right
Accent block left: x=0, w=16pt=203200 EMU, y=105, h=340, gradient accent multi-stop
  VTI: P2→P4 gradient | Dark: D4A26A→8DAAC2 | Light: 3B6FA0→C06030
Quote text zone x=40, y=130, w=720:
  Opening mark: sz=9600 (96pt), accent color, y=110 — dùng ký tự "❝" hoặc rect shape
  Quote body: sz=2800–3200, title color, bold=0, line spacing 160%, italic
  Attribution: sz=1600, muted, y=quote_bottom+20
Accent block right (optional, small): x=900, w=60pt, h=60pt, roundRect accent mờ
Decor: large faint quote mark Pattern 8 (rect approx) bg-right góc, opacity 5%
Context card y=420→490: roundRect card bg + summary/source text 14pt
```

---

## Step 6b — Footer (BẮT BUỘC mọi slide, mọi mode) — [Sonnet 4.6]

Footer gồm **2 thành phần cố định** ở góc dưới bên trái, áp dụng cho **tất cả layout (A–M), tất cả theme (Dark/Light/VTI)**.

### Vị trí cố định (EMU — đã fix bug footer y)

> ⚠️ **Bug đã sửa:** Bản cũ dùng `y=4704919` (~370pt) cho footer — sai lệch 130pt so với vị trí đúng. Toàn bộ content bị nhồi vào 370/540pt. Bản mới dùng `y=6375400` (~502pt).

| Thành phần | x | y | cx | cy |
|---|---|---|---|---|
| Số trang (hình vuông xanh) | `453839` | `6375400` | `533400` | `438551` |
| Copyright text | `1066800` | `6413000` | `3175000` | `342900` |

> **Fix cx copyright:** Cũ=1944600 (153pt) → text "Copyright © 2026 VTI All rights reserved" tràn xuống hàng. Mới=3175000 (250pt) → đủ rộng cho 1 dòng ở sz=1000.

### Màu sắc

- **Hình vuông số trang:** `#408DD6` (xanh dương VTI — dùng cho **mọi theme**, kể cả Dark/Light)
- **Số trang text:** White `#FFFFFF`, bold, sz=1800, centered
- **Copyright text:** `#808080` (xám trung tính — không đổi theo theme)

### Helper function

```javascript
// ── FOOTER HELPER (paste once per edit_slide_xml call) ──────────────
function insertFooter(doc, spTree, slideNumber) {
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  function parse(s) { return new DOMParser().parseFromString(s, "text/xml").documentElement; }

  // Shape 1: Blue square with slide number
  const numBox = parse(`<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="901" name="FooterNum"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="453839" y="6375400"/><a:ext cx="533400" cy="438551"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      <a:solidFill><a:srgbClr val="408DD6"/></a:solidFill>
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody>
      <a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0" anchor="ctr" anchorCtr="1"><a:noAutofit/></a:bodyPr><a:lstStyle/>
      <a:p><a:pPr algn="ctr"/>
        <a:r><a:rPr lang="vi-VN" sz="1800" b="1" dirty="0">
          <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
          <a:latin typeface="Arial" pitchFamily="34" charset="0"/>
          <a:ea typeface="Arial" pitchFamily="34" charset="-122"/>
        </a:rPr><a:t>${slideNumber}</a:t></a:r>
      </a:p>
    </p:txBody>
  </p:sp>`);

  // Shape 2: Copyright text
  const copyright = parse(`<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="902" name="FooterCopyright"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="1066800" y="6413000"/><a:ext cx="3175000" cy="342900"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      <a:noFill/><a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody>
      <a:bodyPr wrap="none" lIns="76200" rIns="76200" tIns="0" bIns="0" anchor="ctr" anchorCtr="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>
      <a:p><a:pPr algn="l"/>
        <a:r><a:rPr lang="vi-VN" sz="1000" b="0" dirty="0">
          <a:solidFill><a:srgbClr val="808080"/></a:solidFill>
          <a:latin typeface="Arial" pitchFamily="34" charset="0"/>
          <a:ea typeface="Arial" pitchFamily="34" charset="-122"/>
        </a:rPr><a:t>Copyright © 2026 VTI All rights reserved</a:t></a:r>
      </a:p>
    </p:txBody>
  </p:sp>`);

  // Re-ID to avoid collisions
  const existing = doc.getElementsByTagName("p:cNvPr");
  let maxId = 900;
  for (let i = 0; i < existing.length; i++) maxId = Math.max(maxId, parseInt(existing[i].getAttribute("id") || "0"));
  numBox.getElementsByTagName("p:cNvPr")[0].setAttribute("id", String(++maxId));
  copyright.getElementsByTagName("p:cNvPr")[0].setAttribute("id", String(++maxId));

  spTree.appendChild(doc.importNode(numBox, true));
  spTree.appendChild(doc.importNode(copyright, true));
}

// ── USAGE (cuối mỗi edit_slide_xml) ────────────────────────────────
// insertFooter(doc, spTree, slideIndex); // slideIndex = 1, 2, 3...
// ────────────────────────────────────────────────────────────────────
```

**Quy tắc:**
- Gọi `insertFooter(doc, spTree, slideIndex)` trong mọi `edit_slide_xml`.
- `slideIndex` bắt đầu từ `1` (slide 1 = cover).
- Màu hình vuông `408DD6` **không đổi** theo theme — đây là brand color cố định.
- Vị trí EMU **không được thay đổi** — cố định theo file gốc.
- Copyright text **không được chỉnh sửa** nội dung.

---

## Step 7 — Badge & Visual Marker System (KIMI-STYLE) — [Sonnet 4.6]

### Nguyên tắc cốt lõi

**KHÔNG dùng `search_icons` / `insert_icon` — kể cả cho hero icon.**

Kimi AI style dùng **geometric OOXML shapes** cho markers/bullets, và **Pattern 5 buildIcon()** cho tất cả icon ngữ nghĩa:
- Nhất quán, professional, không AI-noise từ external library
- Cùng stroke-width, cùng style (stroke-only) trên toàn slide
- Màu derive từ card.border_color → tự đồng nhất không cần can thiệp thủ công

Pattern 5 (`buildIcon()`) thay thế hoàn toàn `search_icons` cho mọi use case (cover hero, section hero, narrative panel, icon grid).

---

### Pattern 1 — Numbered Badge (TOC, ordered list, Flow steps)

**2 shapes chồng tại cùng (x,y):**

```javascript
function buildBadge(doc, id, x_emu, y_emu, number, accentHex) {
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  function parse(s) { return new DOMParser().parseFromString(s, "text/xml").documentElement; }

  const ellipse = parse(`<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="Bg${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x_emu}" y="${y_emu}"/><a:ext cx="508000" cy="508000"/></a:xfrm>
      <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
      <a:solidFill><a:srgbClr val="${accentHex}"/></a:solidFill>
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
  </p:sp>`);

  const num = parse(`<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id+1}" name="Num${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x_emu}" y="${y_emu}"/><a:ext cx="508000" cy="508000"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      <a:noFill/><a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody>
      <a:bodyPr anchor="ctr"/><a:lstStyle/>
      <a:p><a:pPr algn="ctr"/>
        <a:r><a:rPr lang="vi-VN" sz="1800" b="1" dirty="0">
          <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
          <a:latin typeface="Arial" pitchFamily="34" charset="0"/>
        </a:rPr><a:t>${number}</a:t></a:r>
      </a:p>
    </p:txBody>
  </p:sp>`);

  return [doc.importNode(ellipse, true), doc.importNode(num, true)];
}
// Sizing: 508000 EMU = 40pt (TOC/flow), 36×36 cho section
// Text theo sau: x = badge_x + 635000 EMU (50pt gap)
```

---

### Pattern 2 — Solid Accent Dot (bullet replacement)

Ellipse 10×10pt (127000 EMU):

```javascript
function buildDot(doc, id, x_emu, y_emu, colorHex) {
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  const xml = `<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="Dot${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x_emu}" y="${y_emu}"/><a:ext cx="127000" cy="127000"/></a:xfrm>
      <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
      <a:solidFill><a:srgbClr val="${colorHex}"/></a:solidFill>
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
  </p:sp>`;
  return doc.importNode(new DOMParser().parseFromString(xml, "text/xml").documentElement, true);
}
// dot x = text_x_emu - 177800 (14pt gap)
// dot y = text_line_y_emu + (fontSize_pt * 6350) - 63500
```

---

### Pattern 3 — Card Header Badge

Ellipse 36×36pt (457200 EMU):

```javascript
function buildCardBadge(doc, id, card_x_emu, card_y_emu, number, colorHex) {
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  const bx = card_x_emu + 127000;
  const by = card_y_emu + 127000;
  const xml = `<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="CBadge${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${bx}" y="${by}"/><a:ext cx="457200" cy="457200"/></a:xfrm>
      <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
      <a:solidFill><a:srgbClr val="${colorHex}"/></a:solidFill>
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody>
      <a:bodyPr anchor="ctr"/><a:lstStyle/>
      <a:p><a:pPr algn="ctr"/>
        <a:r><a:rPr lang="vi-VN" sz="1600" b="1" dirty="0">
          <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
          <a:latin typeface="Arial" pitchFamily="34" charset="0"/>
        </a:rPr><a:t>${number}</a:t></a:r>
      </a:p>
    </p:txBody>
  </p:sp>`;
  return doc.importNode(new DOMParser().parseFromString(xml, "text/xml").documentElement, true);
}
// Card header text x = card_x_emu + 711200 (56pt)
```

---

### Pattern 4 — Separator Line

Rect 2pt wide, muted color:

```javascript
function buildSeparator(doc, id, x_emu, y_emu, height_emu, colorHex) {
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  const xml = `<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="Sep${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x_emu}" y="${y_emu}"/><a:ext cx="25400" cy="${height_emu}"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      <a:solidFill><a:srgbClr val="${colorHex}"/></a:solidFill>
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
  </p:sp>`;
  return doc.importNode(new DOMParser().parseFromString(xml, "text/xml").documentElement, true);
}
// Light: "A3B5B8" | Dark: "3A3A5A" | VTI: "B8D0EE"
// Horizontal separator: cx=width_emu, cy=38100 (3pt)
```

---

### Pattern 5 — OOXML Semantic Icon (Kimi-style — KHÔNG dùng search_icons)

> **Kimi AI technique:** Tất cả icon = OOXML shapes thuần vector — ellipse/rect/path combination. Màu derive từ `card.border_color` → tự đồng nhất toàn file. Stroke-only style (fill=none) → premium. 3 cấp kích thước cố định → visual rhythm.

#### 5.1 — 3 Size Tiers (cố định toàn deck)

| Tier | EMU (cx=cy) | pt | Use case |
|---|---|---|---|
| Hero | `1016000` | 80pt | Cover right panel, Section divider right panel |
| Mid | `609600` | 48pt | Narrative Layout F right panel |
| Small | `457200` | 36pt | Icon Grid Layout L, mỗi cell top-center |

#### 5.2 — Color Binding Rule (đồng nhất tự động)

```
icon_stroke_color = card.border_color (cùng hex — KHÔNG hardcode riêng)

VTI binding:
  Card tint A (Sky)   → icon stroke = 4A9EE0
  Card tint B (Teal)  → icon stroke = 1E9E8A
  Card tint C (Amber) → icon stroke = E8A020
  Card tint D (Coral) → icon stroke = E05060
  Card tint E (Navy)  → icon stroke = 2362B0
  Card tint F (Green) → icon stroke = 7FC236

Dark theme: icon stroke = accent của section (D4A26A / 8DAAC2 / 5EC4B0 xen kẽ)
Light theme: icon stroke = 3B6FA0 hoặc C06030 xen kẽ theo card index
```

#### 5.3 — Stroke-Only Style (fill=none — bắt buộc cho hero/mid)

```javascript
// stroke-only → premium, nhẹ, không đè lên bg gradient
// stroke-width: hero=2pt(25400), mid/small=1.5pt(19050)
// fill: "none" (KHÔNG solidFill)
// Duy nhất exception: fill opacity 10% cho "depth variant" khi card bg trắng đơn thuần
```

#### 5.4 — buildIcon() — Template Function (1 hàm dùng toàn slide)

```javascript
// Nguyên tắc: tất cả icon trong 1 slide build từ buildIcon() với cùng strokeHex
// → đảm bảo visual consistency tuyệt đối

function buildIcon(doc, id, x_emu, y_emu, size_emu, strokeHex, iconType, themeDepth) {
  // themeDepth: true = thêm fill opacity 10% (depth variant cho white bg)
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  const sw = size_emu >= 1016000 ? "25400" : "19050"; // hero=2pt, others=1.5pt
  const half = Math.round(size_emu / 2);
  const cx = x_emu + half;
  const cy = y_emu + half;

  // Icon type mapping → OOXML shape/path combo
  // Kimi dùng combination 2-3 shapes để gợi ngữ nghĩa — KHÔNG cần detail cao
  const icons = {
    // Tổng quát / AI
    "ai":       [ellipse(id,   x_emu, y_emu, size_emu, strokeHex, sw, themeDepth),
                 hLine(id+1,  cx-half*0.4, cy, half*0.8, strokeHex)],
    "settings": [ellipse(id,   x_emu, y_emu, size_emu, strokeHex, sw, themeDepth),
                 cross(id+1,   cx, cy, half*0.35, strokeHex, sw)],
    "data":     [roundRect(id, x_emu, y_emu, size_emu, size_emu, strokeHex, sw, themeDepth),
                 hLines3(id+1, x_emu, y_emu, size_emu, strokeHex)],
    "flow":     [ellipse(id,   x_emu, y_emu, size_emu, strokeHex, sw, themeDepth),
                 arrow(id+1,   cx-half*0.3, cy, half*0.6, strokeHex, sw)],
    "doc":      [roundRect(id, x_emu, y_emu, size_emu*0.8, size_emu, strokeHex, sw, themeDepth),
                 hLines3(id+1, x_emu+size_emu*0.1, y_emu, size_emu*0.8, strokeHex)],
    "team":     [ellipse(id,   x_emu, y_emu, size_emu*0.55, strokeHex, sw, themeDepth),
                 ellipse(id+1, x_emu+size_emu*0.45, y_emu, size_emu*0.55, strokeHex, sw, themeDepth)],
    "check":    [ellipse(id,   x_emu, y_emu, size_emu, strokeHex, sw, themeDepth),
                 checkmark(id+1, cx, cy, half*0.45, strokeHex, sw)],
    "chart":    [roundRect(id, x_emu, y_emu, size_emu, size_emu, strokeHex, sw, themeDepth),
                 bars(id+1,    x_emu, y_emu, size_emu, strokeHex, sw)],
    "lock":     [roundRect(id, x_emu, y_emu+size_emu*0.35, size_emu, size_emu*0.65, strokeHex, sw, themeDepth),
                 arc(id+1,     cx, y_emu, half*0.5, strokeHex, sw)],
    "star":     [ellipse(id,   x_emu, y_emu, size_emu, strokeHex, sw, themeDepth),
                 star4(id+1,   cx, cy, half*0.4, strokeHex, sw)],
    // fallback: plain ellipse (generic, selalu works)
    "default":  [ellipse(id,   x_emu, y_emu, size_emu, strokeHex, sw, themeDepth)],
  };

  return (icons[iconType] || icons["default"]).flat();
}

// ── Primitive helpers ──────────────────────────────────────────────────
function ellipse(id, x, y, size, stroke, sw, depth) {
  const fill = depth ? `<a:solidFill><a:srgbClr val="${stroke}"><a:alpha val="10000"/></a:srgbClr></a:solidFill>` : `<a:noFill/>`;
  const P="http://schemas.openxmlformats.org/presentationml/2006/main",A="http://schemas.openxmlformats.org/drawingml/2006/main";
  const xml=`<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="Icon${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x}" y="${y}"/><a:ext cx="${size}" cy="${size}"/></a:xfrm>
      <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
      ${fill}
      <a:ln w="${sw}"><a:solidFill><a:srgbClr val="${stroke}"/></a:solidFill></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
  </p:sp>`;
  const doc2=new DOMParser().parseFromString(xml,"text/xml");
  return doc2.documentElement;
}

function roundRect(id, x, y, cx, cy, stroke, sw, depth) {
  const fill = depth ? `<a:solidFill><a:srgbClr val="${stroke}"><a:alpha val="10000"/></a:srgbClr></a:solidFill>` : `<a:noFill/>`;
  const P="http://schemas.openxmlformats.org/presentationml/2006/main",A="http://schemas.openxmlformats.org/drawingml/2006/main";
  const xml=`<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="IconRR${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x}" y="${y}"/><a:ext cx="${cx}" cy="${cy}"/></a:xfrm>
      <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 16667"/></a:avLst></a:prstGeom>
      ${fill}
      <a:ln w="${sw}"><a:solidFill><a:srgbClr val="${stroke}"/></a:solidFill></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
  </p:sp>`;
  return new DOMParser().parseFromString(xml,"text/xml").documentElement;
}
// (hLine, cross, hLines3, arrow, checkmark, bars, arc, star4 → dùng cùng pattern,
//  build bằng rect/line shapes với a:prstGeom prst="line" hoặc path thủ công)
// RULE: Khi không chắc iconType → dùng "default" (ellipse) — vẫn đẹp hơn bitmap icon
```

#### 5.5 — Icon Type Selection Guide

```
Chọn iconType theo ngữ nghĩa nội dung — KHÔNG chọn theo màu:

"ai" / "robot" / "machine learning"  → "ai"
"cài đặt" / "cấu hình" / "quản lý"  → "settings"
"data" / "database" / "dữ liệu"      → "data"
"quy trình" / "workflow" / "flow"    → "flow"
"tài liệu" / "báo cáo" / "spec"      → "doc"
"nhóm" / "team" / "users"            → "team"
"hoàn thành" / "kết quả" / "success" → "check"
"số liệu" / "KPI" / "analytics"      → "chart"
"bảo mật" / "quyền truy cập"         → "lock"
"nổi bật" / "premium" / "ưu điểm"   → "star"
Khác / không rõ                       → "default" (ellipse)
```

#### 5.6 — Icon Grid (Layout L) — cách build đồng loạt

```javascript
// Build tất cả icon trong 1 slide TRƯỚC khi insert vào spTree:
// 1. Lấy mảng iconTypes từ content (["ai","flow","data","check","team","chart"])
// 2. Lấy mảng strokeColors từ card tint rotation (["4A9EE0","1E9E8A","E8A020",...])
// 3. Loop: buildIcon(doc, baseId+i*10, x_emu, y_emu, 457200, strokeColors[i], iconTypes[i], false)
// 4. Append tất cả vào spTree → visual consistency đảm bảo vì cùng template
// strokeWidth = 19050 (1.5pt) cho tất cả — KHÔNG thay đổi per-icon
```

---

### Pattern 6 — Flow Arrow Connector (Layout C only)

rightArrow preset, 24pt × 16pt:

```javascript
function buildArrow(doc, id, x_emu, y_emu, colorHex) {
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  const xml = `<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="Arrow${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x_emu}" y="${y_emu}"/><a:ext cx="304800" cy="203200"/></a:xfrm>
      <a:prstGeom prst="rightArrow"><a:avLst/></a:prstGeom>
      <a:solidFill><a:srgbClr val="${colorHex}"/></a:solidFill>
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
  </p:sp>`;
  return doc.importNode(new DOMParser().parseFromString(xml, "text/xml").documentElement, true);
}
// x = right edge step box + 50400 EMU (4pt gap)
// y = step box center_y - 101600 (half arrow height)
// colorHex = separator muted color của theme
```

---

### Pattern 7 — Rounded Card Background (BẮT BUỘC thay rect)

```javascript
// LUÔN dùng roundRect cho card bg — adj=16667 (~8pt radius)
// VTI tinted card: dùng gradFrom/gradTo từ Tinted Card System (Step 2)
// Dark/Light: dùng gradient chuẩn từ Step 8
const cardBgXml = `<p:sp xmlns:p="${P}" xmlns:a="${A}">
  <p:nvSpPr><p:cNvPr id="${id}" name="Card${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="${cx_emu}" y="${cy_emu}"/><a:ext cx="${cw_emu}" cy="${ch_emu}"/></a:xfrm>
    <a:prstGeom prst="roundRect">
      <a:avLst><a:gd name="adj" fmla="val 16667"/></a:avLst>
    </a:prstGeom>
    <a:gradFill rot="1">
      <a:gsLst>
        <a:gs pos="0"><a:srgbClr val="${gradFrom}"/></a:gs>
        <a:gs pos="100000"><a:srgbClr val="${gradTo}"/></a:gs>
      </a:gsLst>
      <a:lin ang="${gradAng}" scaled="0"/>
    </a:gradFill>
    <a:ln><a:noFill/></a:ln>
  </p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
</p:sp>`;
// Top border: rect w=cw_emu, h=63500(5pt), tint border color, y=cy_emu
// Card padding nội dung ≥152400 EMU (12pt) mọi cạnh
```

---

### Pattern 8 — Decorative Background Shape (visual depth, texture)

Faint ellipse/circle tạo chiều sâu — append TRƯỚC content shapes (z-order dưới cùng):

```javascript
function buildDecorShape(doc, id, x_emu, y_emu, cx_emu, cy_emu, colorHex, alphaPercent) {
  // alphaPercent: 5–15 (rất mờ — chỉ là texture, KHÔNG cản text)
  const P = "http://schemas.openxmlformats.org/presentationml/2006/main";
  const A = "http://schemas.openxmlformats.org/drawingml/2006/main";
  const alphaVal = alphaPercent * 1000;
  const xml = `<p:sp xmlns:p="${P}" xmlns:a="${A}">
    <p:nvSpPr><p:cNvPr id="${id}" name="Decor${id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr>
      <a:xfrm><a:off x="${x_emu}" y="${y_emu}"/><a:ext cx="${cx_emu}" cy="${cy_emu}"/></a:xfrm>
      <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
      <a:solidFill>
        <a:srgbClr val="${colorHex}"><a:alpha val="${alphaVal}"/></a:srgbClr>
      </a:solidFill>
      <a:ln><a:noFill/></a:ln>
    </p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr dirty="0"/></a:p></p:txBody>
  </p:sp>`;
  return doc.importNode(new DOMParser().parseFromString(xml, "text/xml").documentElement, true);
}
// Presets hay dùng (VTI):
// Cover/Section bottom-right: x=7620000, y=3810000, cx=3810000, cy=3810000, color="4A9EE0", alpha=8
// CTA corner circles: (−500000, 3000000, 4000000, 4000000, "7FC236", 7) và (8000000, −500000, 3000000, 3000000, "2362B0", 6)
// Layout M quote decor: x=8000000, y=500000, cx=2000000, cy=2000000, color="2362B0", alpha=5
// Dark theme: color="D4A26A", alpha=6 | Light: color="3B6FA0", alpha=7
```

---

### Bảng quyết định Pattern nhanh

| Vị trí | Pattern | EMU size | Màu |
|---|---|---|---|
| TOC numbered item | 1 (badge) | 508000×508000 | Section color rotation |
| Flow step number | 1 (badge) | 508000×508000 | Primary accent |
| Card header marker | 3 (card badge) | 457200×457200 | Tint border (VTI) / 60-30 (D/L) |
| Bullet indicator | 2 (dot) | 127000×127000 | Primary accent |
| Timeline event dot | 2 (dot, large) | 254000×254000 | Xen kẽ primary/alt |
| Layout separator (V) | 4 (sep rect) | 25400×N | Muted |
| Layout separator (H) | 4 (sep rect) | N×38100 | Muted |
| Hero/section icon | 5 (library icon) | ≥609600 (48pt+) | Accent / tint border |
| Icon grid cell icon | 5 (library icon) | 457200 (36pt) | Tint border color |
| Flow connector | 6 (rightArrow) | 304800×203200 | Muted |
| Card background | 7 (roundRect) | varies | Gradient / VTI tint |
| Bg texture / depth | 8 (decor ellipse) | ≥1905000 (150pt+) | Theme color, 5–15% opacity |

**VTI color rotation (per card index trong slide):**
- Index 0 → tint A (Sky P3), badge P2
- Index 1 → tint B (Teal P5), badge P5
- Index 2 → tint C (Amber P6), badge P4
- Index 3 → tint D (Coral P7), badge P3
- Index 4 → tint E (Navy P2), badge P6
- Index 5 → tint F (Green P4), badge P7

**Dark/Light rotation:** Card odd → primary (60%), even → alt (30%)

---

## Step 8 — Gradient OOXML — [Sonnet 4.6]

**Dark/Light standard gradients:**
```
Accent bar light: 3B6FA0 → C06030, ang=5400000
Accent bar dark:  D4A26A → 8DAAC2, ang=5400000
Card bg light:    FFFFFF → F0EEE8, ang=16200000
Card bg dark:     252538 → 2E2E4A, ang=16200000
Slide bg light:   F5F4F0 → ECEAE4, ang=9000000
Slide bg dark:    1C1C2E → 12121F, ang=9000000
```

**VTI gradient presets (multi-stop dùng 3 gs nodes):**
```xml
<!-- Accent bar cover/section (P2→P3→P4, 3-stop) -->
<a:gradFill rot="1"><a:gsLst>
  <a:gs pos="0"><a:srgbClr val="2362B0"/></a:gs>
  <a:gs pos="50000"><a:srgbClr val="4A9EE0"/></a:gs>
  <a:gs pos="100000"><a:srgbClr val="7FC236"/></a:gs>
</a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>

<!-- Accent bar content (P2→P4, 2-stop) -->
<a:gradFill rot="1"><a:gsLst>
  <a:gs pos="0"><a:srgbClr val="2362B0"/></a:gs>
  <a:gs pos="100000"><a:srgbClr val="7FC236"/></a:gs>
</a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>

<!-- Cover left bar (P1→P2, vertical) -->
<a:gradFill rot="1"><a:gsLst>
  <a:gs pos="0"><a:srgbClr val="172759"/></a:gs>
  <a:gs pos="100000"><a:srgbClr val="2362B0"/></a:gs>
</a:gsLst><a:lin ang="0" scaled="0"/></a:gradFill>

<!-- Section divider bg (P1→1A3070) -->
<a:gradFill rot="1"><a:gsLst>
  <a:gs pos="0"><a:srgbClr val="172759"/></a:gs>
  <a:gs pos="100000"><a:srgbClr val="1A3070"/></a:gs>
</a:gsLst><a:lin ang="9000000" scaled="0"/></a:gradFill>

<!-- CTA bg (P2→P1) -->
<a:gradFill rot="1"><a:gsLst>
  <a:gs pos="0"><a:srgbClr val="2362B0"/></a:gs>
  <a:gs pos="100000"><a:srgbClr val="172759"/></a:gs>
</a:gsLst><a:lin ang="16200000" scaled="0"/></a:gradFill>

<!-- Title divider bar cover (P2→P4) -->
<a:gradFill rot="1"><a:gsLst>
  <a:gs pos="0"><a:srgbClr val="2362B0"/></a:gs>
  <a:gs pos="100000"><a:srgbClr val="7FC236"/></a:gs>
</a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>
```

**VTI Tinted Card gradients (từ Tinted Card System Step 2):**
```
Tint A (Sky):   EBF4FC → D6EAF8, ang=16200000
Tint B (Teal):  E8F7F4 → D0EEE9, ang=16200000
Tint C (Amber): FEF6E7 → FDE9C0, ang=16200000
Tint D (Coral): FDEEF0 → FAD4D8, ang=16200000
Tint E (Navy):  EAF0FA → D5E2F5, ang=16200000
Tint F (Green): F0F9E5 → DDF0C0, ang=16200000
VTI slide bg:   FFFFFF → EEF4FB, ang=9000000
```

---

## Step 9 — Content Density Rules (KIMI-STYLE)

Kimi AI enforce chặt content density để tránh slide bị chật hoặc có khoảng trắng:

| Layout | Max items | Max text/item | Hành động nếu vượt |
|---|---|---|---|
| Card Grid (A) | 4 cards | 3 bullets × 2 dòng | Tách thành 2 slides |
| 2-Column List (B) | 6 items/col | 1 dòng/item | Rút gọn text |
| Flow Steps (C) | 5 steps | 2 dòng/step | Dùng vertical flow |
| Two-Column (D) | 4 bullets/cột | 2 dòng/bullet | Chọn 4 key points |
| Data Highlight (E) | 4 stats | 1 label 1 dòng | Ưu tiên stats chính |
| CTA (H) | 3 action items | 2 dòng/item | Merge nếu nhiều hơn |

**Nguyên tắc:**
- **Stretch-to-fill** — card_h = CONTENT_H / n_cards (dynamic). KHÔNG hardcode height. Cards luôn fill từ CONTENT_TOP → CONTENT_BOTTOM
- **bodyPr bắt buộc** — mọi text shape dùng `wrap="square"` + `normAutofit` (xem Step 3b). KHÔNG dùng `<a:bodyPr anchor="ctr"/>` trần
- **Inset = breathing room** — lIns/rIns=152400, tIns/bIns=114300 cho card content. Text KHÔNG bắt đầu tại edge
- **normAutofit fallback** — khi text dài hơn dự kiến, font tự giảm thay vì overflow. Không cần rút gọn thủ công nếu chênh lệch nhỏ
- Title tối đa 10 từ; subtitle tối đa 15 từ
- AI tự paraphrase nếu nội dung vượt quá density limit (KHÔNG hỏi user)

---

## Step 10 — Spell Check (BẮT BUỘC trước verify) — [Sonnet 4.6]

**🇻🇳 VI:**
- Dấu thanh: sắc huyền hỏi ngã nặng
- Nguyên âm: ă â ê ô ơ ư đ
- Font Arial, lang="vi-VN" tất cả text
- Từ hay sai: hướng dẫn, quy trình, hệ thống, dự án, kết quả, thực chiến

**🇯🇵 JP:** Kanji đúng, lang="ja-JP", Yu Gothic fallback.

**Cách:** `list_slide_shapes` → `read_slide_text` từng text shape → so sánh → `edit_slide_text` fix.

---

## Step 11 — Task Phân Chia & Model Routing

| Task | Độ nặng | Model | Công việc |
|---|---|---|---|
| A | Nhẹ | **Haiku 4.5** | Elicitation + xác nhận + phân tích content type → chọn Layout A–M |
| B | Trung bình | **Sonnet 4.6** | Layout calc: x/y/w/h từ Content Zone Budget + density check |
| C | Nặng | **Sonnet 4.6** | `edit_slide_xml`: OOXML build + badges + footer + icons |
| E | Trung bình | **Sonnet 4.6** | Spell check: `read_slide_text` → fix |
| F | Nhẹ | **Haiku 4.5** | `verify_slides` — chỉ khi có lỗi, KHÔNG chạy mặc định mọi slide |

**Quy trình:** A → B → C → E → F(nếu lỗi)

**Quy tắc chuyển model:**
- Kết thúc task A (Haiku): chuyển Sonnet 4.6 cho B.
- Kết thúc task B (Sonnet): Sonnet tiếp tục build OOXML (task C) ngay — không gọi sub-agent.
- Kết thúc task C (Sonnet): Sonnet tiếp tục task E (spell check).
- Kết thúc task E (Sonnet): chuyển Haiku 4.5 cho F chỉ khi có lỗi cần verify.
- **Không dùng verify_slide_visual** trong happy path — tiết kiệm 1–2 tool calls/slide.

---

## 15 Key Rules (ver2 — Kimi AI full design system)

1. **Gradient 2-tone** mọi bg và card; VTI dùng multi-stop gradient cho accent bar
2. **Arial** cho VI, **Yu Gothic** cho JP kanji
3. **Floor 14pt** (sz=1400) tất cả body text
4. **Cards tới y≈490** — không để bottom trống
5. **1 slide = 1 `edit_slide_xml`** — batch content + badges + logo
6. **Footer góc dưới trái** — `insertFooter(doc, spTree, slideIndex)` BẮT BUỘC mọi slide. Logo do user tự thêm thủ công.
7. **Badge OOXML (Pattern 1–4,6)** cho markers, bullets, TOC, flow; **icon = Pattern 5 buildIcon()** (OOXML shapes thuần, stroke-only, màu derive từ card.border_color) — KHÔNG dùng search_icons/insert_icon
8. **VTI tinted cards** — mỗi card dùng tint khác nhau (A→B→C→D→E→F, cycle); KHÔNG dùng card trắng đơn thuần
9. **Pattern 8 decor shape** — thêm ≥1 faint ellipse decor vào mọi slide có Full-BG (Cover/Section/CTA), optional cho content slides; append TRƯỚC content shapes
10. **KHÔNG hiển thị Color System cho user** — AI tự dùng nội bộ; sau elicitation xác nhận ngắn rồi build
11. **Layout intelligence BẮT BUỘC** — phân tích content type → chọn Layout A–M; variety rule: không >3 slides cùng layout trong 1 deck
12. **roundRect (Pattern 7) cho mọi card** — adj=16667, padding ≥12pt, density rules theo Step 9
13. **Section color rotation** — mỗi section đổi màu accent/badge/stat theo rotation table (Step 2); tạo visual rhythm xuyên suốt deck
14. **Icon Grid (Layout L)** — build tất cả icon trước bằng `buildIcon()` loop; cùng `strokeWidth=19050`, strokeHex = tint border color per cell; append vào spTree — consistency đảm bảo vì cùng 1 template function
15. **Spell check trước verify** — `read_slide_text` → `edit_slide_text`

Done when: theme đúng, Arial VI, ≥14pt, **SLIDE_W=12192000 (960pt)**, **footer y=6375400 + cx copyright=3175000**, badge OOXML nhất quán (Pattern 1–8), **Content Zone Budget applied** (content y_start=1333500, y_end=6096000), **Stretch-to-fill: card_h=CONTENT_H/n_cards**, **bodyPr: wrap+inset+normAutofit mọi text shape** (Step 3b), icon = Pattern 5 buildIcon() stroke-only, VTI tinted cards, layout variety đủ (A–M), section color rotation applied, decor shapes chỉ ở Full-BG layouts, spell check passed, gradient hiển thị.
