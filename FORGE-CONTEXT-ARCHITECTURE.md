# forge-context-engine — Arsitektur Fondasi Context Engineering

| Field | Nilai |
|---|---|
| Dokumen | Desain Fondasi Context Engineering |
| Fase | Fase 1 — Desain Struktur (BUKAN implementasi) |
| Versi | 0.5 (Draft Desain) |
| Tanggal | 2026-05-20 |
| Status | `decision` — menunggu konfirmasi pemilik |
| Bahasa | Bahasa Indonesia |
| Cakupan tooling | Agnostik tooling, kompatibel Claude |

> **Perubahan v0.4 → v0.5:** `profiles/` diganti menjadi **`modes/`** (penamaan lebih natural — AI bekerja dalam "mode planning", "mode review", dst). **`base.md` dihapus** beserta mekanisme `extends` — inti yang selalu termuat (`00-meta/*` + `01-core/*`) sudah dijamin oleh konvensi numbering & urutan bootstrap, sehingga tidak perlu didaftar ulang dalam file mode. Mode kini hanya mendeklarasikan *delta*-nya. Rincian di Lampiran B.

---

## 0. Ringkasan Eksekutif

Dokumen ini mendefinisikan **struktur fondasi Context Engineering** untuk `forge-context-engine`: kerangka konteks AI yang universal, modular, hemat token, dan tahan-halusinasi yang dipakai ulang oleh seluruh workflow AI-native engineering di masa depan.

Keputusan struktural inti:

1. **Satu namespace tunggal** — seluruh konteks hidup di `.forge/context/`, terpisah total dari kode aplikasi.
2. **Numbering ringan & selektif** — hanya `00-meta` & `01-core` (zona dengan urutan-muat wajib) yang diberi nomor.
3. **Tiga zona konteks ortogonal** — `01-core/` (global), `layers/` (horizontal, per peran engineering), `systems/` (vertikal, per unit implementasi nyata).
4. **`systems/` = unit implementasi nyata** — backend service, frontend app, worker, library, infra module, dll. Mendukung repo single-service maupun monorepo dengan struktur yang sama.
5. **Lapisan dimulai sebagai placeholder** — tiap lapisan hanya berisi `README.md` sampai Context Initialization.
6. **Enam keadaan pengetahuan dipisah tegas** — fakta-manusia, inferensi-AI, asumsi, unknown, keputusan, konfirmasi.
7. **Context loading modes** — `modes/` mendeklarasikan *delta* konteks yang dimuat per jenis pekerjaan, di atas inti yang selalu termuat.
8. **Token-efficient by design** — selective loading; tanpa duplikasi lintas zona; konten unit dihasilkan saat init.

Dokumen ini **tidak** membuat file/folder apa pun. Ia cetak biru. Pembuatan struktur nyata adalah fase berikutnya (Context Initialization).

---

## 1. Prinsip Desain

| Prinsip | Keputusan struktural |
|---|---|
| Universal First | Nama folder berbasis peran/unit, bukan teknologi. |
| Context Before Automation | Tidak ada runtime/pipeline. `modes/` hanya deklarasi pemuatan. |
| Clarification Over Assumption | `knowledge/unknowns.md` adalah tujuan wajib tiap gap. |
| Hallucination Resistance | `status` + `evidence` wajib; promosi status butuh jejak (§9). |
| Modular Context Design | Satu fakta, satu rumah. Referensi via `id`, bukan salinan. |
| Layer-Based Thinking | `layers/` memisahkan peran engineering; mulai sebagai placeholder. |
| Existing Project Safety | Struktur sama untuk brownfield & greenfield (§12). |
| Production-Grade Thinking | `owner`, `updated`, `review_by`; manifest dapat divalidasi. |
| Token Efficiency | Selective loading; tanpa duplikasi lintas `core`/`layers`/`systems`. |
| Output Style | Minim file, tanpa duplikasi, tanpa folder spekulatif. |

---

## 2. Struktur Root

### 2.1 Namespace tunggal `.forge/`

Seluruh sistem konteks berada di bawah satu direktori namespace di root repo: **`.forge/`** — isolasi penuh dari kode aplikasi (aman untuk existing project), satu titik masuk, portabel sebagai satu unit. Alternatif non-tersembunyi `forge/` juga sah.

### 2.2 Adapter (agnostik tooling, kompatibel Claude)

Satu file adapter tipis di root repo: **`CLAUDE.md`**. `AGENTS.md` opsional, ditambahkan hanya bila ada asisten AI kedua. Adapter tidak pernah menyimpan konteks — hanya menunjuk ke `.forge/`.

### 2.3 Kebijakan numbering (ringan & selektif)

Hanya `00-meta/` dan `01-core/` yang diberi nomor — keduanya punya **urutan-muat wajib & tidak berubah**: meta dipahami lebih dulu, lalu core sebagai basis universal. Folder lain (`layers/`, `systems/`, `knowledge/`, `modes/`, `generated/`, `temp/`) dimuat berdasarkan mode, bukan urutan tetap — sehingga tidak diberi nomor. Nomor `00`/`01` adalah mnemonic visual; konfigurasi pemuatan penuh tetap di `meta/context-manifest.md` + `modes/`.

### 2.4 Pohon root (tier Standard — rekomendasi default)

```
repo-root/
├── CLAUDE.md                        # adapter tipis → .forge/  (AGENTS.md opsional)
├── .gitignore                       # mengecualikan .forge/context/temp/
└── .forge/
    ├── forge.config.yaml            # manifest engine: tier, layer aktif, systems, mode default
    └── context/
        ├── 00-meta/                 # [muat ke-1] cara membaca sistem konteks ini sendiri
        │   ├── context-manifest.md      # indeks semua file + urutan & aturan pemuatan
        │   ├── conventions.md           # konvensi, front-matter, kontrak operasi AI, siklus hidup
        │   └── glossary.md              # istilah kanonik (domain & teknis)
        ├── 01-core/                 # [muat ke-2] universal core context — global, lintas semua
        │   ├── product.md               # apa produk ini, domain, pengguna
        │   ├── architecture.md          # arsitektur sistem tingkat tinggi
        │   ├── principles.md            # prinsip & standar engineering
        │   └── constraints.md           # batasan keras: compliance, performa, biaya
        ├── layers/                  # konteks HORIZONTAL per peran engineering — placeholder
        │   ├── backend/README.md
        │   ├── frontend/README.md
        │   ├── mobile/README.md
        │   ├── infrastructure/README.md
        │   └── testing/README.md
        ├── systems/                 # konteks VERTIKAL per unit implementasi nyata
        │   └── README.md                # placeholder: bagaimana unit ditambah saat init
        ├── knowledge/               # ledger enam keadaan pengetahuan (§6)
        │   ├── decisions/
        │   │   └── ADR-0000-template.md
        │   ├── assumptions.md
        │   ├── unknowns.md
        │   ├── inferred.md
        │   └── confirmations.md
        ├── modes/                   # context loading modes — deklarasi delta pemuatan
        │   ├── planning.md
        │   ├── implementation.md
        │   ├── review.md
        │   └── testing.md
        ├── generated/               # konteks hasil generate AI — dibuat saat dipakai (opsional)
        └── temp/                    # scratch ephemeral — dibuat saat dipakai (gitignored, opsional)
```

---

## 3. Pemisahan Konteks (Taksonomi)

Konteks dipisah di sepanjang **dua sumbu ortogonal** — inilah yang mencegah duplikasi.

### 3.1 Sumbu A — Taksonomi (apa sifat konteks)

| Zona | Folder | Isi |
|---|---|---|
| Meta | `00-meta/` | Cara membaca sistem konteks itu sendiri |
| Universal Core | `01-core/` | Konteks global lintas seluruh repo (§4) |
| Layer | `layers/` | Konteks horizontal per peran engineering (§4) |
| System | `systems/` | Konteks vertikal per unit implementasi nyata (§4) |
| Knowledge / Ledger | `knowledge/` | Enam keadaan pengetahuan (§6) |
| Generated | `generated/` | Konteks hasil AI, dapat diregenerasi |
| Temporary | `temp/` | Scratch satu sesi |

### 3.2 Sumbu B — Loading Mode (kapan konteks dimuat)

`modes/` bukan zona taksonomi. Tiap file mendeklarasikan *delta* konteks dari Sumbu A yang dimuat untuk satu jenis pekerjaan. Detail di §7.

### 3.3 Resolusi tumpang-tindih: Layer vs Mode

`testing`, `security`, `observability` adalah **lapisan** (pengetahuan yang bertahan) → `layers/`. `planning`, `implementation`, `review`, `documentation` adalah **mode pemuatan** (lensa kerja) → `modes/`.

---

## 4. Tiga Zona Konteks: core/, layers/, systems/

Tiga zona ini mudah tertukar — pemisahan yang tegas di antaranya adalah yang menjaga sistem tetap hemat token dan bebas duplikasi.

### 4.1 Perbedaan tiga zona

| Zona | Pertanyaan yang dijawab | Orientasi | Lingkup | Contoh isi |
|---|---|---|---|---|
| **`01-core/`** | "Apa produk ini & aturan apa yang berlaku universal?" | Global | Seluruh repo/produk | Visi produk, arsitektur menyeluruh, prinsip engineering, batasan keras |
| **`layers/`** | "Bagaimana cara kita mengerjakan satu disiplin engineering?" | Horizontal — lintas semua sistem | Satu peran engineering | Standar & pola backend, frontend, testing, infrastruktur |
| **`systems/`** | "Apa yang spesifik tentang satu unit implementasi ini?" | Vertikal — satu unit, lintas semua lapisannya | Satu unit buildable nyata | Tanggung jawab `payment-service`, antarmuka publiknya, dependensinya |

Model mentalnya: `01-core/` berada di atas; `layers/` adalah irisan **horizontal** (satu disiplin yang membentang ke semua sistem); `systems/` adalah irisan **vertikal** (satu unit yang menembus semua lapisannya). Sebuah sistem *menyentuh* banyak lapisan; sebuah lapisan *membentang* ke banyak sistem. Keduanya ortogonal.

```
                  01-core/  ── konteks global (berlaku untuk semua)
   ┌─────────────────────────────────────────────────────┐
   │            systems/payment-service  systems/admin-portal  ...
   │ layers/backend   ──────┼───────────────────┼──────────  (horizontal)
   │ layers/frontend  ──────┼───────────────────┼──────────
   │ layers/testing   ──────┼───────────────────┼──────────
   │                   (vertikal)         (vertikal)
   └─────────────────────────────────────────────────────┘
```

### 4.2 Apa itu `systems/`

`systems/` menyimpan konteks untuk **unit implementasi nyata** — sesuatu yang benar-benar dibangun, dijalankan, atau dipublikasikan, dan memiliki batas kodebasis sendiri. Contoh: backend service, frontend app, mobile app, worker, shared library, infrastructure module, platform component.

Tiap unit ditandai `system_type`: `service` · `app` · `worker` · `library` · `infra-module` · `platform-component`.

Tiap unit memiliki satu folder: `systems/<nama-sistem>/system.md` (dapat dipecah jadi sub-file saat besar). Isinya **hanya konteks spesifik-implementasi**: tanggung jawab unit ini, antarmuka publik/API yang diekspos, dependensi ke unit lain & eksternal, lapisan apa yang disentuh (referensi ke `layers/`), konteks runtime spesifik, serta unknown/asumsi unit ini.

### 4.3 Aturan anti-duplikasi (wajib)

`systems/` **bukan** dokumentasi domain bisnis dan **bukan** tempat menyalin konteks lain:

1. **Jangan menyalin konteks global dari `01-core/`.** Visi produk, arsitektur menyeluruh → hanya di `01-core/`; `system.md` mereferensikan via `id`.
2. **Jangan menyalin standar lapisan dari `layers/`.** Bila sebuah fakta berlaku untuk *semua* backend service, ia milik `layers/backend/`, bukan disalin ke tiap `system.md`.
3. **`systems/` hanya berisi yang spesifik unit itu.** Uji penempatan: *"Apakah fakta ini benar HANYA untuk unit ini?"* Jika ya → `systems/<unit>/`. Jika berlaku untuk satu disiplin → `layers/`. Jika berlaku untuk seluruh produk → `01-core/`.

Setiap fakta punya tepat satu rumah — inilah mekanisme hemat-token: konteks bersama dideklarasikan sekali, dirujuk berkali-kali.

### 4.4 Model repo 1 — Single-service repository

Repo yang berisi satu unit implementasi saja. `systems/` berisi tepat satu folder.

```
payment-service-repo/
└── .forge/context/
    ├── 01-core/         → konteks produk & arsitektur untuk service ini
    ├── layers/          → hanya lapisan yang dipakai (mis. backend, testing)
    └── systems/
        ├── README.md
        └── payment-service/system.md
```

`01-core/` menjawab "produk apa & mengapa", `systems/payment-service/` menjawab "spesifik service ini" — keduanya tidak saling menyalin.

### 4.5 Model repo 2 — Monorepo / multi-application repository

`systems/` berisi banyak folder bersebelahan, satu per unit. `01-core/` dan `layers/` **dibagikan satu kali** untuk semua unit.

```
monorepo/
└── .forge/context/
    ├── 01-core/         → konteks produk & arsitektur — DIBAGI semua unit
    ├── layers/          → standar backend/frontend/mobile/... — DIBAGI semua unit
    └── systems/
        ├── README.md
        ├── payment-service/system.md
        ├── auth-service/system.md
        ├── admin-portal/system.md
        └── mobile-app/system.md
```

4 unit tidak mengulang visi produk atau standar backend — semuanya mereferensikan `01-core/` & `layers/` yang tunggal. Dependensi antar-unit dinyatakan sebagai referensi `id`. Memuat konteks untuk tugas pada `payment-service` hanya menarik `01-core/` + `layers/` relevan + `systems/payment-service/` — bukan unit lain (§11).

---

## 5. Skema Front-Matter & Konvensi

Setiap file konteks (kecuali adapter) diawali front-matter YAML — kontrak yang dapat dibaca mesin.

```yaml
---
id: system.payment-service       # ID unik global, format: <zona>.<nama>
title: Sistem — Payment Service
type: system                     # meta|core|layer|system|knowledge|mode|generated
system_type: service             # hanya untuk type=system: service|app|worker|library|infra-module|platform-component
status: confirmed                # confirmed|inferred|assumption|unknown|deprecated
confidence: high                 # high|medium|low
source: human                    # human|ai|hybrid — SIAPA yang menulis (kunci pemisahan §6)
evidence:                        # WAJIB bila status confirmed/inferred
  - { type: code, ref: services/payment/ }   # type: code|doc|adr|human|external
owner: payments-team
updated: 2026-05-20
review_by: 2026-08-20            # opsional — pemicu staleness (§10)
---
```

`status` — keadaan epistemik: `confirmed` (terverifikasi/dikonfirmasi, boleh jadi dasar keputusan); `inferred` (disimpulkan AI, ber-evidence, wajib dilabeli); `assumption` (sementara, bukan dasar keputusan final); `unknown` (gap diakui, dilarang ditebak); `deprecated` (tidak berlaku, tidak dimuat).

Konvensi: file `kebab-case.md`; `id` berformat `<zona>.<nama>`; ADR `ADR-NNNN-judul.md` append-only; satu fakta satu rumah — referensi `id`, jangan salin.

---

## 6. Pemisahan Enam Keadaan Pengetahuan

Enam keadaan pengetahuan **tidak boleh tercampur**. Tiap keadaan punya lokasi, `source`, dan `status` berbeda.

| # | Keadaan | Lokasi | `source` | `status` | Otoritatif? |
|---|---|---|---|---|---|
| 1 | **Fakta tulisan manusia** | `01-core/`, `layers/*`, `systems/*` | `human` | `confirmed` | Ya |
| 2 | **Pengetahuan inferensi AI** | `knowledge/inferred.md`, `generated/` | `ai` | `inferred` | **Tidak** |
| 3 | **Asumsi** | `knowledge/assumptions.md` | `human`/`ai` | `assumption` | Tidak |
| 4 | **Unknown** | `knowledge/unknowns.md` | `human`/`ai` | `unknown` | — (gap) |
| 5 | **Keputusan** | `knowledge/decisions/` | `human` | `decision` | Ya (untuk intent) |
| 6 | **Konfirmasi** | `knowledge/confirmations.md` | `human` | — (log) | Ya (audit) |

Aturan pemisahan: keadaan 1 & 2 tidak pernah berbagi file (fakta manusia terpisah fisik dari inferensi AI yang dikarantina); `source` menandai penulis, `status` menandai keandalan; AI tidak menulis ke file `source: human`; promosi melintasi keadaan harus tercatat; unknown adalah tujuan wajib, bukan tebakan.

**Batas source-of-truth:** kode adalah sumber kebenaran untuk fakta implementasi (`layers/`/`systems/` ber-`inferred` adalah tampilan ter-cache); `knowledge/decisions/` adalah sumber kebenaran untuk intent; `generated/` tidak pernah otoritatif. Konteks adalah lapisan turunan; AI mengonsumsinya, tidak pernah diam-diam menimpa sumbernya.

---

## 7. Context Loading Modes

Sebuah **mode** adalah deklarasi pemuatan konteks: ia menentukan konteks *apa* yang masuk ke window AI untuk satu jenis pekerjaan. Mode **tidak** mengatur perilaku, langkah, atau eksekusi — hanya pemilihan konteks. Nama "mode" lebih natural daripada "profile": AI bekerja dalam "mode planning", "mode review", dst.

### 7.1 Inti yang selalu termuat — bukan bagian dari mode

`00-meta/*` dan `01-core/*` **selalu dimuat**, terlepas dari mode apa pun. Ini sudah dijamin oleh dua hal: (a) konvensi numbering — `00`/`01` menandai zona urutan-muat wajib (§2.3); (b) urutan bootstrap (§8). Karena itu inti ini didefinisikan **satu kali** di `00-meta/conventions.md` dan **tidak pernah** didaftar ulang dalam file mode.

> **Catatan v0.5:** v0.4 punya `profiles/base.md` yang mendaftar `00-meta/*` + `01-core/*` agar profil lain mewarisinya lewat `extends`. Itu redundan — inti yang selalu termuat sudah dijamin oleh numbering + bootstrap. `base.md` dan `extends` dihapus; mode kini hanya mendeklarasikan *delta*-nya di atas inti.

### 7.2 Skema mode

```yaml
---
id: mode.review
type: mode
title: Mode — Review
---
# Mode: Review
## Tujuan          → satu kalimat
## include         → konteks DELTA yang dimuat, DI ATAS inti yang selalu termuat
## on_demand       → dimuat hanya bila direferensikan
## exclude         → pengecualian eksplisit (menang atas include)
## token_budget    → batas estimasi token
```

Mode tidak pernah mendaftar `00-meta/*` atau `01-core/*` — hanya delta-nya. Hanya deklarasi, ≤ ~40 baris.

### 7.3 Mode baku

| Mode | include (delta di atas inti) |
|---|---|
| `planning` | `knowledge/*`, ringkasan `layers/*` |
| `implementation` | `layers/<aktif>`, `systems/<terkait>`, `knowledge/decisions/*`, `inferred` |
| `review` | `layers/security` + `layers/<terkait>`, `knowledge/decisions/*` |
| `testing` | `layers/testing` + `systems/<terkait>`, `knowledge/assumptions` |

`loading.default_mode` di `forge.config.yaml` menetapkan mode default.

---

## 8. Selective Loading & Token Efficiency

Alur pemuatan:

```
1. AI membaca CLAUDE.md
2. → forge.config.yaml                (tier, layer aktif, systems, mode default)
3. → 00-meta/*                        (SELALU — cara membaca sistem & bootstrap)
4. → 01-core/*                        (SELALU — inti universal)
5. Pilih mode → modes/<mode>.md       (resolusi include/on_demand/exclude — DELTA saja)
6. Skip status=deprecated; hormati token_budget
```

Langkah 3–4 tidak bergantung mode — selalu dijalankan. Langkah 5 adalah bagian variabel.

Mekanisme hemat token: (1) selective loading via mode — tiap tugas memuat subset; (2) mode = referensi, bukan konten; (3) inti yang selalu termuat didefinisikan sekali — mode hanya menyatakan delta; (4) **tanpa duplikasi lintas `core`/`layers`/`systems`** (§4.3); (5) lapisan mulai sebagai README ringkas; (6) `generated/` & `temp/` dibuat saat dipakai; (7) size budget per file.

Size budget (batas lunak): `01-core/*` ≤ ~200 baris; `layers/*` ≤ ~150; `systems/*/system.md` ≤ ~200; `modes/*` ≤ ~40; `knowledge/*` append-only. File yang melewati budget dipecah menjadi sub-file di folder yang sama.

---

## 9. Resistensi Halusinasi (Struktural)

`knowledge/` adalah ledger kebenaran tunggal (§6). Jalur promosi status:

```
            (evidence ditemukan)        (manusia konfirmasi)
 assumption ───────────────────► inferred ───────────────────► confirmed
     │                              │                              │
     ▼ (salah/tak relevan)          ▼ (salah)                      ▼ (usang/drift)
  unknown / deprecated          unknown                  inferred / deprecated
```

Status hanya naik melalui transisi tercatat; naik ke `confirmed` mewajibkan entri di `confirmations.md`.

Kontrak operasi AI (ditulis di `00-meta/conventions.md`): (1) jangan menaikkan status — boleh mengusulkan saja; (2) jangan menyajikan `inferred`/`assumption` sebagai fakta; (3) saat menemui `unknown`, berhenti & tanya atau catat — dilarang menebak; (4) inferensi baru masuk `inferred.md`/`generated/`, tidak pernah langsung ke file `source: human`; (5) tanpa `evidence`, status maksimal `assumption`; (6) jangan mengarang arsitektur, API, service, database, integrasi, kepemilikan, atau aturan bisnis.

---

## 10. Siklus Hidup Konteks

```
CREATE ──► EVIDENCED ──► CONFIRMED ──► MAINTAINED ──► (DRIFT?) ──► DEPRECATED ──► PRUNED
```

Keputusan kunci: **`confirmed` tidak permanen.** Konteks dikonfirmasi relatif terhadap satu titik riwayat kode. Karena tiap file `confirmed`/`inferred` membawa `evidence` yang menunjuk path kode, **perubahan kode pada path itu otomatis menurunkan `confirmed` → `inferred`** — diatur oleh `governance.demote_confirmed_on_evidence_change`. Pemicu re-review lain: `updated` lebih tua dari `staleness_days`.

Siklus berbeda per tipe: `temp/*` (satu sesi → dihapus); `generated/*` (sampai diregenerasi → ditimpa); entri `inferred`/`assumption`/`unknown` (sampai diselesaikan); `core`/`layer`/`system` (panjang, dipelihara → `deprecated`); ADR (permanen → `superseded`, tidak pernah dihapus).

---

## 11. Skalabilitas

**Skala lebar** — lebih banyak lapisan atau sistem = menambah folder bersebelahan; aditif O(1), tanpa reorganisasi.

**Skala dalam** — saat file melewati size budget, ia dipecah menjadi sub-file di folder yang sama; `id` & front-matter pola tetap.

**Skala baca (paling penting)** — biaya token sebuah tugas AI dibatasi oleh *mode*, bukan oleh total ukuran konteks. Monorepo dengan 3 unit dan 50 unit sama murahnya dibaca untuk tugas pada satu unit, karena mode hanya memuat `systems/<unit-itu>/` + konteks bersama.

**Skala tier** — Minimal → Standard → Advanced bersifat murni aditif; naik tier hanya menambah file, tanpa migrasi.

---

## 12. Dukungan Lintas Skenario

**Existing project init** — didukung penuh. Scan kode mengisi `layers/` & `systems/` dengan `status: inferred` + `evidence`; gap masuk `unknowns.md`. Tidak ada yang otomatis menjadi `confirmed`.

**New project generation** — didukung penuh. Konteks dibangun dari `knowledge/decisions/` & `assumptions.md`; file lapisan/sistem dihasilkan dengan `status: assumption` sampai implementasi memvalidasinya.

**Spec-Driven Development masa depan (titik ekstensi)** — struktur sudah memodelkan "intent sebelum kode" lewat `knowledge/decisions/` & `assumptions.md`. SDD slot masuk sebagai zona `specs/` baru atau mode `spec` — tanpa mengubah apa pun yang ada. Tidak dirancang sekarang.

**Workflow agent masa depan (titik ekstensi)** — agent membutuhkan: `modes/` untuk memilih konteks; disiplin `status`/`evidence` agar agent tidak berhalusinasi; `00-meta/agent-contract.md` (tier Advanced) sebagai kontrak baca/tulis agent. Implementasi agent di luar cakupan.

---

## 13. Skema Lengkap Tiap File Konteks

`forge.config.yaml` — `forge_version`, `tier`, `layers_enabled`, `systems` (daftar `name` + `type`), `loading` (`default_mode`, `respect_size_budget`), `size_budget`, `governance` (`staleness_days`, `require_evidence_for`, `demote_confirmed_on_evidence_change`).

`00-meta/context-manifest.md` — indeks file, urutan & aturan pemuatan, lapisan & sistem aktif, mode tersedia, aturan validasi (§16).

`00-meta/conventions.md` — penamaan & ID, skema front-matter, kosakata status, **definisi inti yang selalu termuat** (§7.1), kontrak operasi AI (§9, NORMATIF), jalur promosi status, siklus hidup, kebijakan staleness.

`00-meta/glossary.md` *(opsional)* — daftar `istilah — definisi kanonik — status`.

`01-core/product.md` — ringkasan, domain & masalah, pengguna & pemangku kepentingan, batas sistem (IN/OUT), istilah inti.

`01-core/architecture.md` — gaya arsitektur, komponen utama, alur data tingkat tinggi, integrasi eksternal, batasan arsitektural.

`01-core/principles.md` & `constraints.md` *(opsional)* — prinsip & standar engineering; batasan compliance/performa/biaya/keamanan/legacy.

**`layers/<layer>/README.md`** — placeholder lapisan: `## Kapan diisi` (saat init untuk proyek yang punya lapisan ini; hapus folder bila tidak punya); `## Bagaimana berkembang` (init membuat `<layer>.md` → brownfield `inferred`+evidence / greenfield `assumption`+ADR → dipecah saat melewati budget); `## Yang tidak boleh sekarang` (jangan membuat file konten sebelum init).

**`systems/README.md`** — placeholder: menjelaskan bahwa tiap unit implementasi mendapat folder `systems/<nama>/` yang dibuat saat init, dengan `system.md`, serta perbedaan single-service vs monorepo (§4.4–4.5).

**`systems/<nama-sistem>/system.md`** — `type: system`, `system_type: <tipe>`. Body: `## Tujuan & Tanggung Jawab` · `## Tipe & Runtime` (deskriptif) · `## Antarmuka Publik` (status wajib per entri) · `## Dependensi` (unit lain via `id`; eksternal) · `## Lapisan yang Disentuh` (referensi `layers/*` — TIDAK menyalin standar) · `## Konteks Spesifik Implementasi` · `## Unknown & Asumsi Sistem`.

`knowledge/decisions/ADR-NNNN-*.md` — `# ADR-NNNN: Judul`, status, tanggal, pengambil keputusan, konteks, keputusan, alternatif, konsekuensi, evidence. Append-only.

`knowledge/assumptions.md` / `unknowns.md` / `inferred.md` / `confirmations.md` — tabel ledger masing-masing (kolom: lihat §6).

`modes/<mode>.md` — skema §7.2, hanya deklarasi delta, ≤ ~40 baris.

`CLAUDE.md` — adapter minimal: baca manifest → conventions → muat `00-meta/*` & `01-core/*` → pilih mode → muat delta mode.

---

## 14. Dibuat Sekarang vs Dihasilkan Saat Init

### 14.1 Dibuat sekarang — kerangka fondasi

`.forge/forge.config.yaml`; `00-meta/{context-manifest,conventions,glossary}.md`; `01-core/{product,architecture,principles,constraints}.md` (**template kosong**: heading + front-matter `status: unknown`); `layers/<layer>/README.md` (×5, konten final); `systems/README.md` (placeholder, konten final); `knowledge/decisions/ADR-0000-template.md`; `knowledge/{assumptions,unknowns,inferred,confirmations}.md` (header tabel, tanpa entri); `modes/{planning,implementation,review,testing}.md`; `CLAUDE.md`.

### 14.2 Dihasilkan saat Context Initialization (fase berikutnya)

**Isi** `01-core/*` (fakta nyata); `layers/<layer>/<layer>.md` & sub-file (konten lapisan, README tetap); `systems/<nama-sistem>/system.md` per unit implementasi nyata; entri di keempat file ledger `knowledge/`; ADR nyata (`ADR-0001` dst); isi `generated/` & `temp/` (folder dibuat saat dipakai).

> Dokumen ini hanya *mendefinisikan* kedua daftar. Pembuatan file nyata adalah fase Context Initialization, di luar cakupan fase saat ini.

---

## 15. Tiga Tingkatan Struktur

Struktur identik di tiga tier; yang berbeda hanya cakupan aktivasi. Naik tier = menambah file, tanpa migrasi.

**Minimal (~8 file)** — `forge.config.yaml`; `00-meta/{context-manifest,conventions}.md`; `01-core/{product,architecture}.md`; `knowledge/{decisions/ADR-0000-template.md, assumptions.md, unknowns.md}`; `CLAUDE.md`. Tanpa `layers/`, `systems/`, `modes/` — untuk titik awal/eksperimen.

**Standard (~22–28 file) — rekomendasi** — Minimal + `glossary.md` + `01-core/{principles,constraints}.md` + `layers/<5>/README.md` + `systems/README.md` + `knowledge/{inferred,confirmations}.md` + `modes/<4>`. Repo single-service maupun monorepo memakai tier ini. Pohon penuh → §2.4.

**Advanced (~38+ file)** — Standard + `layers/{observability,security}/README.md` + banyak unit di `systems/` (monorepo) + `modes/{security,documentation}.md` + `00-meta/{lifecycle,agent-contract}.md`.

| Dimensi | Minimal | Standard | Advanced |
|---|---|---|---|
| `layers/` | – | 5 README | + observability, security |
| `systems/` | – | README (unit diisi saat init) | multi-unit (monorepo) |
| `modes/` | – (muat penuh) | 4 mode | + security, documentation |
| Kesiapan agent | – | – | kontrak agent |

---

## 16. Tata Kelola & Validasi

Invarian yang dapat dicek mekanis (oleh CI di fase mendatang; di sini hanya *aturannya*): setiap file punya front-matter valid; setiap file terdaftar di manifest; setiap `id` unik; `confirmed`/`inferred` wajib ber-`evidence`; file `source: human` tidak ditulis AI; tak ada `systems/*` atau `layers/*` menyalin konten `01-core/`; tak ada `systems/*` menyalin standar `layers/*` (§4.3); **tak ada file `modes/*` mendaftar `00-meta/*` atau `01-core/*`** (§7.1 — inti hanya delta); tiap entri `unknowns`/`assumptions` punya pemilik & status; file melewati size budget memicu peringatan; `updated` melewati `staleness_days` memicu review; perubahan kode di path `evidence` menurunkan `confirmed` → `inferred`; ADR `accepted` immutable.

---

## 17. Struktur Final yang Direkomendasikan

**Rekomendasi: adopsi tier Standard sebagai default**, dengan struktur penuh di §2.4.

Alasan: Minimal terlalu tipis untuk proyek produksi (tanpa `layers/`/`systems/`/`modes/`); Advanced berisiko over-engineering bila diadopsi dini. Standard adalah titik seimbang: tiga zona konteks yang terpisah tegas (§4), numbering ringan yang tepat, lapisan sebagai placeholder hemat-token, pemisahan enam keadaan pengetahuan (§6), loading mode fungsional (§7), ledger anti-halusinasi (§9), siklus hidup terkelola (§10), skalabilitas tiga sumbu (§11), dukungan single-service & monorepo dengan struktur sama (§4.4–4.5), dengan jumlah file terkendali dan jalur tumbuh tanpa migrasi.

Tujuh keputusan struktural yang harus dipertahankan di tier mana pun:

1. Namespace tunggal `.forge/context/` dengan dua sumbu pemisahan ortogonal.
2. Numbering ringan hanya pada `00-meta` & `01-core`.
3. Tiga zona terpisah — `01-core/` (global), `layers/` (horizontal), `systems/` (vertikal) — tanpa duplikasi lintas zona.
4. `systems/` = unit implementasi nyata; satu struktur untuk single-service & monorepo.
5. Lapisan mulai sebagai `README.md` placeholder.
6. Enam keadaan pengetahuan dipisah secara fisik & metadata (§6).
7. `modes/` hanya mendeklarasikan delta — inti yang selalu termuat tidak diulang; `status` + `evidence` di setiap file.

---

## 18. Di Luar Cakupan Fase Ini

Sengaja **tidak** ada: pembuatan file/folder nyata (fase Context Initialization); logika analisis repo; generator proyek baru; workflow SDD, orchestration agent, otomasi MR/PR; pipeline CI/CD, deployment, runtime; kode aplikasi & pilihan bahasa/framework. Desain ini hanya menyediakan *fondasi*.

---

## Lampiran A — Telusur ke 13 Pertanyaan Awal

| # | Pertanyaan | Dijawab di |
|---|---|---|
| 1 | Struktur root terbaik | §2 |
| 2 | Pemisahan konteks | §3, §4, §6 |
| 3 | Konteks yang selalu ada | §14.1 |
| 4 | Konteks opsional | §15 |
| 5 | Konteks yang dihasilkan saat init | §14.2 |
| 6 | Token-efficient, modular, scalable, maintainable, aman, future-proof | §1, §8, §11, §16 |
| 7 | Selective loading per workflow | §7, §8 |
| 8 | Pencegahan halusinasi | §6, §9 |
| 9 | Existing vs new project | §12 |
| 10–12 | Struktur Minimal / Standard / Advanced | §15 |
| 13 | Struktur final & alasan | §17 |

## Lampiran B — Changelog v0.4 → v0.5

| Perubahan | Rincian |
|---|---|
| `profiles/` → `modes/` | Penamaan lebih natural — AI bekerja dalam "mode planning", "mode review", dst. `type: profile` → `type: mode`; `id: profile.x` → `id: mode.x`. |
| `base.md` dihapus | `base.md` hanya mendaftar ulang `00-meta/*` + `01-core/*`. Inti itu sudah dijamin selalu termuat oleh konvensi numbering (§2.3) + urutan bootstrap (§8) — jadi redundan. |
| `extends` dihapus | Mekanisme pewarisan antar-profil tidak lagi diperlukan setelah `base.md` hilang. Mode kini deklarasi datar berisi *delta* saja. |
| Inti termuat didefinisikan sekali | "Inti yang selalu termuat" kini didefinisikan satu kali di `00-meta/conventions.md` (§7.1). |
| Validasi baru | Validator menolak file `modes/*` yang mendaftar `00-meta/*` atau `01-core/*` (§16). |

## Lampiran C — Langkah Berikutnya (di luar fase ini)

Konfirmasi pemilik (naikkan `status` `decision` → `confirmed`); fase Context Initialization membuat kerangka §14.1 lalu mengisi konten §14.2; tulis ADR-0001 yang merekam adopsi arsitektur ini; implementasikan validator manifest (§16) sebagai cek CI ringan.
