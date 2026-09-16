-- V1: Initial PostgreSQL Schema for SitePulse Residential Management

CREATE TABLE siteler (
    id VARCHAR(36) PRIMARY KEY,
    ad VARCHAR(150) NOT NULL,
    adres TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bloklar (
    id VARCHAR(36) PRIMARY KEY,
    site_id VARCHAR(36) NOT NULL REFERENCES siteler(id) ON DELETE CASCADE,
    blok_adi VARCHAR(50) NOT NULL,
    toplam_kat INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE kisiler (
    id VARCHAR(36) PRIMARY KEY,
    tc_kimlik VARCHAR(11) UNIQUE,
    ad_soyad VARCHAR(120) NOT NULL,
    telefon VARCHAR(20),
    eposta VARCHAR(120),
    kisi_tipi VARCHAR(20) NOT NULL -- 'KAT_MALIKI', 'KIRACI', 'SAKIN'
);

CREATE TABLE bagimsiz_bolumler (
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

CREATE TABLE aidat_borclari (
    id VARCHAR(36) PRIMARY KEY,
    bagimsiz_bolum_id VARCHAR(36) NOT NULL REFERENCES bagimsiz_bolumler(id) ON DELETE CASCADE,
    donem VARCHAR(50) NOT NULL, -- e.g. 'Eylül 2026'
    ana_para NUMERIC(15, 2) NOT NULL,
    son_odeme_tarihi DATE NOT NULL,
    durum VARCHAR(20) NOT NULL DEFAULT 'BEKLIYOR', -- 'BEKLIYOR', 'GECIKMEDE', 'ODENDI'
    gecikme_tazminati NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    odenen_tutar NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    odeme_tarihi TIMESTAMP WITH TIME ZONE,
    version INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Immutable Ledger for payment transactions (Audit Log)
CREATE TABLE tahsilat_hareketleri (
    id VARCHAR(36) PRIMARY KEY,
    aidat_borcu_id VARCHAR(36) NOT NULL REFERENCES aidat_borclari(id),
    islem_tipi VARCHAR(30) NOT NULL, -- 'KREDI_KARTI_POS', 'HAVALE_EFT', 'KASA_NAKIT'
    odenen_tutar NUMERIC(15, 2) NOT NULL,
    referans_kodu VARCHAR(100),
    islem_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance indices for mobile queries
CREATE INDEX idx_aidat_bolum_durum ON aidat_borclari (bagimsiz_bolum_id, durum);
CREATE INDEX idx_aidat_son_odeme ON aidat_borclari (son_odeme_tarihi);
