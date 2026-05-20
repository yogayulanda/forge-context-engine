---
id: meta.context-content-contract
title: Kontrak Konten Konteks — forge-context-engine
type: meta
status: decision
confidence: high
source: hybrid
evidence:
  - { type: doc, ref: FORGE-CONTEXT-ARCHITECTURE.md }
  - { type: doc, ref: CLAUDE.md }
owner: forge-context-engine
updated: 2026-05-20
---

# Kontrak Konten Konteks — forge-context-engine

> Versi 0.1 (Draft) · Pendamping `FORGE-CONTEXT-ARCHITECTURE.md` v0.5 · Bahasa Indonesia

## 0. Tentang Dokumen Ini

Dokumen arsitektur (`FORGE-CONTEXT-ARCHITECTURE.md`) menjawab **di mana** konteks hidup — struktur folder, zona, tier. Dokumen ini menjawab **apa** yang boleh hidup di setiap tempat dan **bagaimana** AI memperlakukannya: kontrak semantik per komponen.

Ini **bukan** template dokumen, **bukan** skema markdown wajib, **bukan** birokrasi format. Kontrak ini mengikat **makna dan batas**, bukan tata letak. Penulis file bebas memakai struktur adaptif (heading, tabel, daftar) selama batas semantik dipatuhi — tidak ada section markdown yang diwajibkan.

Fungsi dokumen: aturan konteks engineering yang dapat dibaca AI, panduan anti-tumpang-tindih, panduan anti-halusinasi, dan panduan rawatan jangka panjang.

`CLAUDE.md` (adapter root) tidak menyimpan konteks sehingga berada di luar cakupan kontrak ini.

**Pemuatan dokumen ini sendiri:** ini file `type: meta` di `00-meta/`, namun bersifat referensi tata kelola yang verbose. Direkomendasikan dimuat **selektif** (saat Context Initialization & pemeliharaan konteks), bukan pada setiap bootstrap — `conventions.md` tetap satu-satunya file normatif yang selalu dimuat. Konsekuensi terhadap invarian arsitektur §8 dicatat di §6.

## 1. Cara Membaca Kontrak

Setiap komponen di §3 didefinisikan lewat tujuh field tetap:

1. **Tujuan** — alasan keberadaan komponen, dalam satu kalimat.
2. **Pengetahuan yang dimuat** — jenis pengetahuan yang menjadi miliknya.
3. **Yang TIDAK boleh dimuat** — batas eksklusi; mencegah tumpang-tindih.
4. **Perilaku AI** — bagaimana AI membaca/menulis/mempercayai komponen.
5. **Verbositas** — kepadatan yang diharapkan (lihat skala di bawah).
6. **Loading** — kapan komponen masuk window konteks (lihat §2.1).
7. **Relasi** — keterkaitan & garis pemisah dengan komponen lain.

**Skala verbositas:** `Minimal` (key/value) · `Sangat ringkas` (satu baris per entri) · `Ringkas` (pernyataan tegas) · `Sedang` (prosa padat terstruktur) · `Adaptif` (variabel sesuai isi).

## 2. Aturan Global

### 2.1 Tiga Tier Pemuatan

| Tier | Komponen | Implikasi kontrak |
|---|---|---|
| **Selalu dimuat** | `forge.config.yaml`, `00-meta/*`, `01-core/*` | Biayanya dibayar setiap tugas → **wajib hemat token** (size budget ketat). |
| **Selektif** | `layers/*`, `systems/*`, `knowledge/*`, `modes/<aktif>` | Dimuat hanya bila mode/intent merujuknya → **inilah sumber penghematan token**. |
| **Dihasilkan kemudian** | `generated/*`, `temp/*` | Tidak ada saat bootstrap; dibuat saat dipakai, dimuat on-demand. |

### 2.2 Hierarki Otoritas (resolusi konflik konteks)

Bila dua sumber konteks bertentangan, AI mengikuti urutan kepercayaan ini (tertinggi → terendah):

1. **Kode nyata repo** — sumber kebenaran untuk fakta implementasi; konteks hanyalah cache turunan.
2. **`knowledge/decisions/` (ADR)** — sumber kebenaran untuk intent & keputusan.
3. **`01-core/constraints.md`** — batas keras; mengungguli kenyamanan desain.
4. **Fakta `status: confirmed` tulisan manusia** di `01-core/`, `layers/`, `systems/`.
5. **`01-core/principles.md`** — panduan lunak/heuristik.
6. **`status: inferred`** — `knowledge/inferred.md` serta entri layer/system ber-inferensi.
7. **`status: assumption`** — `knowledge/assumptions.md`.
8. **`generated/*`** — tidak pernah otoritatif.
9. **`temp/*`** — tidak pernah otoritatif; disposable.

### 2.3 Uji Penempatan — Satu Fakta, Satu Rumah

Sebelum menulis sebuah fakta, tanyakan: *"Selingkup apa fakta ini benar?"* — Berlaku untuk seluruh produk → `01-core/`. Berlaku untuk satu disiplin engineering → `layers/`. Benar **hanya** untuk satu unit implementasi → `systems/`. Konteks bersama dideklarasikan sekali dan dirujuk via `id`, **tidak pernah disalin**. Duplikasi hanya sah bila berupa ringkasan yang disengaja dan ditandai sebagai turunan.

### 2.4 Hemat Token

Utamakan konteks padat-sinyal di atas dokumentasi verbose. Hormati size budget (`01-core/*` ≤ ~200 baris; `layers/*` ≤ ~150; `systems/*` ≤ ~200; `modes/*` ≤ ~40). File yang melewati budget dipecah jadi sub-file, bukan dipadatkan dengan mengorbankan kejelasan. Komponen tier "Selalu dimuat" memikul disiplin paling ketat.

### 2.5 Anti-Halusinasi

AI tidak pernah mengarang arsitektur, API, service, database, integrasi, kepemilikan, atau aturan bisnis. Tanpa `evidence`, status maksimal `assumption`. Inferensi baru masuk `inferred.md`/`generated/`, tidak pernah ke file `source: human`. `unknown` adalah tujuan wajib — dilarang ditebak. Kontrak operasi AI yang normatif berada di `00-meta/conventions.md` (lihat arsitektur §9).

## 3. Kontrak per Komponen

### 3.1 `00-meta/context-manifest.md`

*Lokasi: `.forge/context/00-meta/` · type: `meta`*

- **Tujuan** — Indeks dan peta-routing seluruh sistem konteks; titik masuk tunggal yang memberi tahu AI file apa yang ada, di mana, dan aturan pemuatannya.
- **Pengetahuan yang dimuat** — Registry file/folder beserta tier pemuatannya; urutan & aturan bootstrap; daftar layer, system, dan mode aktif; aturan validasi manifest. Pointer, bukan isi.
- **Yang TIDAK boleh dimuat** — Pengetahuan domain apa pun (produk, arsitektur, konvensi, aturan bisnis); salinan isi file lain; keputusan engineering.
- **Perilaku AI** — Dibaca pertama (setelah config) sebagai tabel routing untuk menentukan file lain yang dimuat per mode/intent. Bukan sumber fakta; bila manifest dan file nyata berbeda, file nyata menang dan manifest diperbarui.
- **Verbositas** — Sangat ringkas; gaya tabel/daftar.
- **Loading** — Selalu dimuat (bootstrap, file pertama `00-meta`).
- **Relasi** — Akar graf dependensi; merujuk semua komponen. Berpasangan dengan `forge.config.yaml` (config = pengaturan; manifest = isi & routing). Dikonsumsi `modes/` saat resolusi delta.

### 3.2 `00-meta/conventions.md`

*Lokasi: `.forge/context/00-meta/` · type: `meta`*

- **Tujuan** — Aturan main sistem konteks itu sendiri: konvensi penamaan & ID, skema front-matter, kosakata status, kontrak operasi AI (normatif), jalur promosi status, siklus hidup & staleness.
- **Pengetahuan yang dimuat** — Konvensi stabil repo-wide tentang **cara mengelola konteks**; definisi "inti yang selalu termuat"; kontrak baca/tulis AI.
- **Yang TIDAK boleh dimuat** — Konvensi koding spesifik disiplin (→ `layers/`); prinsip engineering produk (→ `principles.md`); pengetahuan domain; pengaturan mesin (→ `forge.config.yaml`).
- **Perilaku AI** — Selalu hadir; kontrak operasi AI di sini bersifat **normatif** dan wajib dipatuhi (tidak menaikkan status sendiri, tidak menulis ke file `source: human`, tidak menebak `unknown`). Acuan setiap kali membuat/memperbarui file konteks.
- **Verbositas** — Ringkas; pernyataan aturan yang tegas dan dapat dicek.
- **Loading** — Selalu dimuat (bootstrap, `00-meta`).
- **Relasi** — Menormakan setiap file konteks. Aturannya ditegakkan oleh blok `governance` di `forge.config.yaml`. Berbeda dari `principles.md`: ini aturan sistem konteks, bukan prinsip engineering produk.

### 3.3 `00-meta/glossary.md`

*Lokasi: `.forge/context/00-meta/` · type: `meta` · opsional pada tier Minimal*

- **Tujuan** — Kosakata kanonik: definisi tunggal dan otoritatif untuk istilah domain/teknis yang ambigu atau spesifik proyek.
- **Pengetahuan yang dimuat** — Entri `istilah — definisi kanonik — status`; hanya istilah spesifik domain/proyek, akronim, atau istilah bermakna khusus di repo ini; alias bila perlu.
- **Yang TIDAK boleh dimuat** — Istilah engineering umum; tutorial/penjelasan panjang; deskripsi arsitektur atau produk (→ `01-core/`).
- **Perilaku AI** — Tabel lookup untuk meresolusi istilah ambigu dan menyelaraskan penamaan; mencegah makna karangan. Bila pemakaian menyimpang dari glossary, glossary menang atau gap dicatat.
- **Verbositas** — Sangat ringkas; satu baris per istilah. Justru karena selalu dimuat, ketat-padat adalah syarat.
- **Loading** — Selalu dimuat saat ada (`00-meta`); opsional pada tier Minimal.
- **Relasi** — Mendukung `product.md`, `architecture.md`, `systems/*` dengan kosakata bersama; dirujuk via istilah, tidak disalin.

### 3.4 `01-core/product.md`

*Lokasi: `.forge/context/01-core/` · type: `core`*

- **Tujuan** — Konteks produk & domain tingkat global: apa produk ini, masalah yang dipecahkan, untuk siapa, dan batas sistem — menjawab "produk apa & mengapa".
- **Pengetahuan yang dimuat** — Ringkasan produk; domain & ruang masalah; pengguna & pemangku kepentingan; batas sistem (IN/OUT scope); istilah inti produk. Fakta & keputusan eksplisit.
- **Yang TIDAK boleh dimuat** — Arsitektur teknis & solusi (→ `architecture.md`); detail satu unit (→ `systems/`); konvensi koding; roadmap spekulatif; materi marketing.
- **Perilaku AI** — Selalu tersedia sebagai latar. AI menambatkan setiap keputusan generasi/spec pada intent produk & batas scope; menolak menambah fitur di luar scope tanpa keputusan; scope tak jelas → `unknowns.md`.
- **Verbositas** — Sedang; prosa padat, ≤ ~200 baris.
- **Loading** — Selalu dimuat (inti `01-core`).
- **Relasi** — Membatasi `architecture.md` (masalah → solusi). Sumber intent untuk `modes/planning` & SDD masa depan. Berbeda dari `architecture.md`: product = ruang masalah, architecture = ruang solusi.

### 3.5 `01-core/architecture.md`

*Lokasi: `.forge/context/01-core/` · type: `core`*

- **Tujuan** — Arsitektur sistem tingkat tinggi & global: gaya arsitektur, komponen utama, alur data menyeluruh, integrasi eksternal, batasan arsitektural.
- **Pengetahuan yang dimuat** — Struktur level-sistem; tanggung jawab & batas komponen besar; alur data tingkat tinggi; titik integrasi eksternal; keputusan arsitektural mayor (dengan `status` & `evidence`).
- **Yang TIDAK boleh dimuat** — Detail internal satu disiplin (→ `layers/`); detail satu unit (→ `systems/`); alasan bisnis (→ `product.md`); konvensi koding; arsitektur yang ditebak tanpa evidence.
- **Perilaku AI** — Model mental sistem yang selalu hadir. AI menghormati batas komponen, **tidak mengarang** komponen/service/database/integrasi di luar yang terdaftar; komponen tak terverifikasi → `inferred`; gap → `unknowns.md`.
- **Verbositas** — Sedang; terstruktur, ≤ ~200 baris.
- **Loading** — Selalu dimuat (inti `01-core`).
- **Relasi** — Induk konseptual `layers/` & `systems/` (keduanya menspesialisasikan, tidak menyalin). Dibatasi oleh `product.md` & `constraints.md`. Keputusan besar dicatat sebagai ADR di `knowledge/decisions/`.

### 3.6 `01-core/principles.md`

*Lokasi: `.forge/context/01-core/` · type: `core` · opsional pada tier Minimal*

- **Tujuan** — Nilai & standar engineering yang tahan lama: heuristik pengambilan keputusan yang memandu penilaian saat aturan konkret tidak mencakup suatu kasus.
- **Pengetahuan yang dimuat** — Prinsip engineering berprioritas; heuristik trade-off; filosofi keputusan & standar mutu. Stabil, jarang berubah.
- **Yang TIDAK boleh dimuat** — Konvensi pengelolaan konteks (→ `conventions.md`); batasan keras (→ `constraints.md`); tujuan produk (→ `product.md`); detail implementasi atau aturan spesifik layer.
- **Perilaku AI** — Penengah trade-off saat aturan konkret tak mencukupi; dipakai untuk menjustifikasi rekomendasi. Bukan batas keras — kalah terhadap `constraints.md` bila berbenturan.
- **Verbositas** — Sangat ringkas; pernyataan prinsip.
- **Loading** — Selalu dimuat saat ada (inti `01-core`); opsional pada tier Minimal.
- **Relasi** — Mendasari konvensi koding per layer (konvensi = prinsip yang dikonkretkan). Dipakai `modes/review`. Berbeda dari `constraints.md`: principles = "sebaiknya", constraints = "wajib".

### 3.7 `01-core/constraints.md`

*Lokasi: `.forge/context/01-core/` · type: `core` · opsional pada tier Minimal*

- **Tujuan** — Batas keras dan hal yang tidak bisa dinegosiasi: batasan compliance, performa, biaya, keamanan, dan legacy/platform yang wajib dipatuhi.
- **Pengetahuan yang dimuat** — Batasan eksplisit & faktual: mandat regulasi, anggaran performa, batas platform, mandat keamanan, teknologi yang dilarang/diwajibkan — dengan `evidence`/sumber.
- **Yang TIDAK boleh dimuat** — Preferensi atau prinsip lunak (→ `principles.md`); konvensi; tujuan aspiratif; asumsi yang disajikan seolah batasan (→ `knowledge/assumptions.md`).
- **Perilaku AI** — Batas keras absolut. AI tidak pernah mengusulkan solusi yang melanggarnya; konflik tugas-vs-constraint → **berhenti dan tandai**. Otoritas tertinggi setelah kode nyata & ADR.
- **Verbositas** — Sangat ringkas; terenumerasi, tegas, dapat diaudit.
- **Loading** — Selalu dimuat saat ada (inti `01-core`); opsional pada tier Minimal.
- **Relasi** — Membatasi `architecture.md`, `layers/`, `systems/`, dan `modes/implementation`. Mengungguli `principles.md` saat berkonflik.

### 3.8 `forge.config.yaml`

*Lokasi: `.forge/` (root namespace, satu-satunya komponen di luar `context/`) · tanpa front-matter — file konfigurasi, bukan file konteks naratif*

- **Tujuan** — Manifest engine yang dapat dibaca mesin: mendeklarasikan **konfigurasi** sistem konteks — tier, layer aktif, daftar systems, mode default, parameter governance & size budget.
- **Pengetahuan yang dimuat** — Nilai konfigurasi saja: `forge_version`, `tier`, `layers_enabled`, `systems[]`, `loading.default_mode`, `size_budget`, `governance.*`.
- **Yang TIDAK boleh dimuat** — Pengetahuan domain; prosa; fakta arsitektur; konvensi; narasi manusia. Komentar minimal saja.
- **Perilaku AI** — Dibaca paling awal saat bootstrap untuk mengetahui **bagaimana** engine dikonfigurasi. Bukan sumber pengetahuan; tidak pernah dikutip sebagai fakta domain. AI boleh mengusulkan perubahan, tidak mengubah diam-diam.
- **Verbositas** — Minimal; hanya key/value.
- **Loading** — Selalu dimuat (bootstrap langkah ke-2, sebelum `context/`).
- **Relasi** — Berpasangan dengan `context-manifest.md` (config = pengaturan & toggle; manifest = indeks isi). Mengaktifkan `layers/`, `systems/`, dan mode default. Parameter `governance`/`size_budget` menegakkan aturan `conventions.md`.

### 3.9 `layers/`

*Lokasi: `.forge/context/layers/` · type: `layer` (per file `<layer>.md`)*

- **Tujuan** — Konteks **horizontal** per peran/disiplin engineering — backend, frontend, mobile, infrastructure, testing (+ observability & security pada tier Advanced); menjawab "bagaimana kita mengerjakan satu disiplin", membentang ke semua sistem.
- **Pengetahuan yang dimuat** — Per layer: konvensi & pola spesifik disiplin, standar, struktur, batasan layer. Mulai sebagai `README.md` placeholder; konten `<layer>.md` dihasilkan saat init.
- **Yang TIDAK boleh dimuat** — Konteks global lintas-disiplin (→ `01-core/`); konteks spesifik satu unit (→ `systems/`); pengetahuan produk; apa pun yang disalin dari core. Satu file layer tidak mencampur dua disiplin.
- **Perilaku AI** — Memuat **hanya** layer yang relevan dengan tugas; tidak mencampur konteks antar-layer. Fakta brownfield → `inferred`+evidence; greenfield → `assumption`+ADR.
- **Verbositas** — Sedang per layer; fokus, ≤ ~150 baris; dipecah jadi sub-file bila melewati budget.
- **Loading** — Selektif; per layer, didorong mode/intent. Placeholder README ringan; konten dimuat hanya saat layer aktif.
- **Relasi** — Menspesialisasikan `architecture.md` dan menerapkan `principles.md`. Ortogonal terhadap `systems/` (layer = irisan horizontal, system = irisan vertikal); uji penempatan §2.3 mencegah duplikasi.

### 3.10 `systems/`

*Lokasi: `.forge/context/systems/` · type: `system` (per `<nama>/system.md`)*

- **Tujuan** — Konteks **vertikal** per unit implementasi nyata — service, app, worker, library, infra-module, platform-component; menjawab "apa yang spesifik tentang satu unit ini", menembus semua layer yang disentuhnya.
- **Pengetahuan yang dimuat** — Per unit: tanggung jawab, antarmuka publik/API, dependensi (unit lain via `id` + eksternal), layer yang disentuh (referensi), konteks runtime spesifik, unknown/asumsi unit. Hanya yang benar **hanya** untuk unit ini.
- **Yang TIDAK boleh dimuat** — Konteks global (→ `01-core/`); standar disiplin yang berlaku untuk semua unit sejenis (→ `layers/`); dokumentasi domain bisnis; unit yang tidak ada/dikarang.
- **Perilaku AI** — Memuat hanya system yang disentuh tugas; dipakai untuk memahami dampak lintas-layer & dependensi antar-unit. Dependensi dinyatakan sebagai referensi `id`, bukan salinan.
- **Verbositas** — Sedang; fokus per unit, ≤ ~200 baris; dipecah saat besar.
- **Loading** — Selektif; per unit, didorong mode/intent. Pada monorepo, hanya unit terkait yang dimuat (biaya token per-tugas O(1)).
- **Relasi** — Menyusun `layers/` secara vertikal; didetailkan di bawah `architecture.md`. Uji penempatan tegas mencegah duplikasi dengan core & layers.

### 3.11 `knowledge/`

*Lokasi: `.forge/context/knowledge/` · berisi `decisions/`, `assumptions.md`, `unknowns.md`, `inferred.md`, `confirmations.md`*

- **Tujuan** — Ledger kebenaran tunggal: memisahkan secara fisik keenam keadaan pengetahuan dan menjadi mesin resistensi halusinasi sistem.
- **Pengetahuan yang dimuat** — Lihat batas per sub-komponen:

  | Sub-komponen | Keadaan | Otoritatif? | Catatan |
  |---|---|---|---|
  | `decisions/` (ADR) | Keputusan / intent | Ya (untuk intent) | Append-only; `ADR-NNNN`; immutable saat `accepted` |
  | `assumptions.md` | Asumsi sementara | Tidak | Bukan dasar keputusan final |
  | `unknowns.md` | Gap yang diakui | — | Tujuan wajib; dilarang ditebak |
  | `inferred.md` | Inferensi AI | Tidak | `source: ai`; wajib dilabeli; dikarantina |
  | `confirmations.md` | Log konfirmasi | Ya (audit) | Mencatat promosi status ke `confirmed` |

- **Yang TIDAK boleh dimuat** — Fakta manusia otoritatif (→ `01-core/`/`layers/`/`systems/`); artefak generate mentah (→ `generated/`); scratch (→ `temp/`). `inferred` tidak pernah bercampur fisik dengan fakta manusia.
- **Perilaku AI** — AI menulis inferensi/asumsi/unknown **di sini**, tidak pernah ke file `source: human`. AI tidak menaikkan status sendiri — hanya mengusulkan; promosi ke `confirmed` butuh entri `confirmations.md`. `unknown` = tujuan wajib, dilarang ditebak.
- **Verbositas** — Ringkas, append-only; tabel ledger; ADR terstruktur. Tumbuh dengan menambah entri, bukan memperbesar file.
- **Loading** — Selektif per mode: `decisions/` → implementation/review; `assumptions`/`unknowns` → planning/testing; `inferred` → implementation.
- **Relasi** — `decisions/` = sumber kebenaran intent (mengikat `architecture.md` & `systems/`). Memberi makan `modes/`. `inferred.md` berpasangan dengan `generated/` (keduanya non-otoritatif).

### 3.12 `modes/`

*Lokasi: `.forge/context/modes/` · type: `mode` (per `<mode>.md`)*

- **Tujuan** — Deklarasi pemuatan konteks per jenis pekerjaan — planning, implementation, review, testing (+ security & documentation pada Advanced); menentukan konteks **apa** yang masuk window AI.
- **Pengetahuan yang dimuat** — Per mode: `include` (delta di atas inti yang selalu termuat), `on_demand`, `exclude`, `token_budget`. Hanya deklarasi referensi.
- **Yang TIDAK boleh dimuat** — Pengetahuan domain apa pun; kode runtime/otomasi; langkah prosedural/perilaku; `00-meta/*` atau `01-core/*` (inti tidak pernah didaftar ulang — hanya delta).
- **Perilaku AI** — AI mengidentifikasi mode aktif lalu mengikuti resep pemuatannya (resolusi `include`/`on_demand`/`exclude`, hormati `token_budget`). Mode = kebijakan pemilihan konteks, bukan kebijakan perilaku.
- **Verbositas** — Sangat ringkas; deklarasi murni, ≤ ~40 baris per mode.
- **Loading** — Selektif; hanya mode aktif diresolusi (`default_mode` dari `forge.config.yaml`). Mode itu sendiri yang mendorong pemuatan komponen lain.
- **Relasi** — Mengonsumsi `context-manifest.md`; mendorong selective loading atas `layers/`, `systems/`, `knowledge/`. Titik ekstensi untuk SDD & agent workflow masa depan.

### 3.13 `generated/`

*Lokasi: `.forge/context/generated/` · type: `generated` · dibuat saat dipakai*

- **Tujuan** — Konteks turunan hasil generate AI: ringkasan, indeks, peta kode, snapshot yang diekstrak AI dari repo/konteks nyata — terpisah tegas dari ground truth tulisan manusia.
- **Pengetahuan yang dimuat** — Artefak turunan mesin: peta kode, ringkasan dependensi, snapshot arsitektur terekstrak. Selalu ditandai `source: ai`, status non-otoritatif, dengan timestamp & sumber.
- **Yang TIDAK boleh dimuat** — Ground truth tulisan manusia; keputusan; batasan; apa pun yang otoritatif. Tidak diedit tangan — diregenerasi, bukan dipelihara.
- **Perilaku AI** — Diperlakukan sebagai kepercayaan rendah & dapat diregenerasi. AI memverifikasi terhadap sumber nyata sebelum mengandalkannya; tidak pernah dikutip mengungguli `01-core/`. Bisa usang.
- **Verbositas** — Adaptif; tetap ringkas — ringkasan hemat token, bukan dump.
- **Loading** — Dihasilkan kemudian; dibuat saat dipakai, dimuat selektif on-demand; tidak pernah selalu-muat.
- **Relasi** — Diturunkan dari repo nyata + konteks core; dikonsumsi `modes/`. Berpasangan dengan `knowledge/inferred.md` (keduanya non-otoritatif).

### 3.14 `temp/`

*Lokasi: `.forge/context/temp/` · gitignored · dibuat saat dipakai*

- **Tujuan** — Scratch ephemeral: konteks kerja berumur pendek untuk satu sesi/tugas. Sepenuhnya disposable.
- **Pengetahuan yang dimuat** — Catatan transien, state tugas antara, draf konteks — apa pun yang aman dihapus saat sesi berakhir.
- **Yang TIDAK boleh dimuat** — Apa pun yang tahan lama; keputusan; ground truth; apa pun yang komponen lain bergantung padanya. Tidak di-commit (gitignored).
- **Perilaku AI** — Boleh dipakai bebas sebagai scratchpad dalam satu tugas; tidak pernah diandalkan lintas sesi; tidak pernah dijadikan otoritas tanpa dipromosikan keluar lebih dulu.
- **Verbositas** — Tidak dibatasi; tidak relevan karena konten disposable.
- **Loading** — Tidak pernah dimuat otomatis; hanya dalam tugas aktif yang membuatnya. Dikecualikan dari routing manifest.
- **Relasi** — Terisolasi — tidak ada komponen yang boleh bergantung padanya. Jalur promosi: `temp/` → (diverifikasi) → `knowledge/` atau `01-core/`.

## 4. Matriks Ringkas

| Komponen | Tier pemuatan | Verbositas | Inti batas semantik |
|---|---|---|---|
| `context-manifest.md` | Selalu | Sangat ringkas | Indeks & routing — bukan pengetahuan |
| `conventions.md` | Selalu | Ringkas | Aturan sistem konteks & kontrak AI |
| `glossary.md` | Selalu * | Sangat ringkas | Kosakata kanonik |
| `product.md` | Selalu | Sedang | Ruang masalah & domain |
| `architecture.md` | Selalu | Sedang | Ruang solusi tingkat sistem |
| `principles.md` | Selalu * | Sangat ringkas | Heuristik "sebaiknya" |
| `constraints.md` | Selalu * | Sangat ringkas | Batas keras "wajib" |
| `forge.config.yaml` | Selalu | Minimal | Pengaturan engine |
| `layers/` | Selektif | Sedang / layer | Disiplin engineering horizontal |
| `systems/` | Selektif | Sedang / unit | Unit implementasi vertikal nyata |
| `knowledge/` | Selektif | Ringkas, append-only | Ledger enam keadaan pengetahuan |
| `modes/` | Selektif | Sangat ringkas | Deklarasi delta pemuatan |
| `generated/` | Dihasilkan kemudian | Adaptif ringkas | Turunan AI non-otoritatif |
| `temp/` | Tidak otomatis | Bebas / disposable | Scratch satu sesi |

\* Selalu dimuat saat ada; opsional pada tier Minimal.

## 5. Peta Anti-Overlap

Garis pemisah untuk pasangan komponen yang paling sering tertukar:

| Pasangan | Garis pemisah |
|---|---|
| `product.md` ↔ `architecture.md` | Masalah & "mengapa" vs solusi & "bagaimana sistem" |
| `architecture.md` ↔ `layers/` ↔ `systems/` | Global vs disiplin horizontal vs unit vertikal |
| `principles.md` ↔ `constraints.md` | Panduan "sebaiknya" vs batas "wajib" |
| `conventions.md` ↔ `principles.md` | Aturan mengelola sistem konteks vs prinsip engineering produk |
| `conventions.md` ↔ `layers/` | Konvensi meta-konteks vs konvensi koding per disiplin |
| `glossary.md` ↔ `product.md` | Definisi istilah satu baris vs deskripsi domain |
| `context-manifest.md` ↔ `forge.config.yaml` | Indeks isi & routing vs pengaturan & toggle engine |
| `knowledge/inferred.md` ↔ `generated/` | Entri ledger inferensi terkurasi vs artefak generate mentah |
| `generated/` ↔ `temp/` | Turunan persisten sampai diregenerasi vs scratch satu sesi |
| `layers/` ↔ `modes/` | Pengetahuan disiplin yang bertahan vs lensa pemuatan per pekerjaan |

## 6. Titik Terbuka

Hal-hal yang memerlukan keputusan pemilik sebelum kontrak ini naik dari `status: decision` ke `confirmed`:

1. **Pemuatan dokumen ini** — Menempatkan file ber-isi verbose di `00-meta/` menabrak invarian arsitektur §8 ("`00-meta/*` selalu dimuat"). Rekomendasi: dokumen ini dimuat **selektif** (mode `init` & pemeliharaan konteks), dan aturan §8 disempurnakan menjadi "`00-meta/*` selalu dimuat **kecuali** file ber-`loading: selective` eksplisit". Alternatif: pindah ke sub-folder `00-meta/governance/` yang dikecualikan dari always-load.
2. **Registrasi & validasi** — Saat skeleton dibuat (fase Context Initialization), `context-content-contract.md` harus didaftarkan di `context-manifest.md` dan lulus invarian validasi arsitektur §16 (front-matter valid, `id` unik, terdaftar di manifest).
3. **Promosi status** — Dokumen ini `status: decision`; konfirmasi pemilik menaikkannya ke `confirmed` dengan mencatat entri di `confirmations.md` saat ledger `knowledge/` aktif.
