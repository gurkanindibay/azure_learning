-- SitePulse Seed Test Data for Local Development & Testing

-- 1. Create Tables (matches Flyway V1)
CREATE TABLE IF NOT EXISTS siteler (
    id VARCHAR(36) PRIMARY KEY,
    ad VARCHAR(150) NOT NULL,
    adres TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bloklar (
    id VARCHAR(36) PRIMARY KEY,
    site_id VARCHAR(36) NOT NULL REFERENCES siteler(id) ON DELETE CASCADE,
    blok_adi VARCHAR(50) NOT NULL,
    toplam_kat INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kisiler (
    id VARCHAR(36) PRIMARY KEY,
    tc_kimlik VARCHAR(11) UNIQUE,
    ad_soyad VARCHAR(120) NOT NULL,
    telefon VARCHAR(20),
    eposta VARCHAR(120),
    kisi_tipi VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS bagimsiz_bolumler (
    id VARCHAR(36) PRIMARY KEY,
    blok_id VARCHAR(36) NOT NULL REFERENCES bloklar(id) ON DELETE CASCADE,
    daire_no INT NOT NULL,
    kat INT NOT NULL,
    arsa_payi INT NOT NULL DEFAULT 1,
    malik_id VARCHAR(36) NOT NULL REFERENCES kisiler(id),
    kiraci_id VARCHAR(36) REFERENCES kisiler(id),
    version INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_blok_daire UNIQUE (blok_id, daire_no)
);

CREATE TABLE IF NOT EXISTS aidat_borclari (
    id VARCHAR(36) PRIMARY KEY,
    bagimsiz_bolum_id VARCHAR(36) NOT NULL REFERENCES bagimsiz_bolumler(id) ON DELETE CASCADE,
    donem VARCHAR(50) NOT NULL,
    ana_para NUMERIC(15, 2) NOT NULL,
    son_odeme_tarihi DATE NOT NULL,
    durum VARCHAR(20) NOT NULL DEFAULT 'BEKLIYOR',
    gecikme_tazminati NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    odenen_tutar NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    odeme_tarihi TIMESTAMP WITH TIME ZONE,
    version INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tahsilat_hareketleri (
    id VARCHAR(36) PRIMARY KEY,
    aidat_borcu_id VARCHAR(36) NOT NULL REFERENCES aidat_borclari(id),
    islem_tipi VARCHAR(30) NOT NULL,
    odenen_tutar NUMERIC(15, 2) NOT NULL,
    referans_kodu VARCHAR(100),
    islem_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Insert Seed Data
INSERT INTO siteler (id, ad, adres) 
VALUES ('site-01', 'Begonya Sitesi', 'Ataşehir, İstanbul')
ON CONFLICT (id) DO NOTHING;

INSERT INTO bloklar (id, site_id, blok_adi, toplam_kat) 
VALUES 
  ('blok-A', 'site-01', 'A Blok', 12),
  ('blok-B', 'site-01', 'B Blok', 10)
ON CONFLICT (id) DO NOTHING;

INSERT INTO kisiler (id, tc_kimlik, ad_soyad, telefon, eposta, kisi_tipi) 
VALUES 
  ('kisi-01', '12345678901', 'Ahmet Yılmaz', '05321112233', 'ahmet@example.com', 'KAT_MALIKI'),
  ('kisi-02', '98765432109', 'Zeynep Kaya', '05423334455', 'zeynep@example.com', 'KIRACI'),
  ('kisi-03', '55555555555', 'Mehmet Demir', '05559998877', 'mehmet@example.com', 'KAT_MALIKI')
ON CONFLICT (id) DO NOTHING;

INSERT INTO bagimsiz_bolumler (id, blok_id, daire_no, kat, arsa_payi, malik_id, kiraci_id) 
VALUES 
  ('d-14', 'blok-A', 14, 4, 24, 'kisi-01', 'kisi-02'),
  ('d-03', 'blok-B', 3, 1, 18, 'kisi-03', NULL)
ON CONFLICT (id) DO NOTHING;

-- Seed Dues matching SPEC-001 (₺1400.00 base, 10 days overdue relative to mid-September)
INSERT INTO aidat_borclari (id, bagimsiz_bolum_id, donem, ana_para, son_odeme_tarihi, durum, gecikme_tazminati) 
VALUES 
  ('borc-101', 'd-14', 'Eylül 2026', 1400.00, '2026-09-15', 'GECIKMEDE', 23.33),
  ('borc-102', 'd-03', 'Eylül 2026', 1100.00, '2026-09-30', 'BEKLIYOR', 0.00)
ON CONFLICT (id) DO NOTHING;
