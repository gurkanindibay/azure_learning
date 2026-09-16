package com.sitepulse.backend.domain.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;

@Entity
@Table(name = "aidat_borclari", indexes = {
    @Index(name = "idx_aidat_bolum_durum", columnList = "bagimsiz_bolum_id, durum"),
    @Index(name = "idx_aidat_son_odeme", columnList = "son_odeme_tarihi")
})
public class AidatBorcuEntity {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "bagimsiz_bolum_id", length = 36, nullable = false)
    private String bagimsizBolumId;

    @Column(nullable = false, length = 50)
    private String donem;

    @Column(name = "ana_para", precision = 15, scale = 2, nullable = false)
    private BigDecimal anaPara;

    @Column(name = "son_odeme_tarihi", nullable = false)
    private LocalDate sonOdemeTarihi;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private BorcDurumu durum = BorcDurumu.BEKLIYOR;

    @Column(name = "gecikme_tazminati", precision = 15, scale = 2, nullable = false)
    private BigDecimal gecikmeTazminati = BigDecimal.ZERO;

    @Column(name = "odenen_tutar", precision = 15, scale = 2, nullable = false)
    private BigDecimal odenenTutar = BigDecimal.ZERO;

    @Version
    private Integer version;

    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    public AidatBorcuEntity() {}

    public AidatBorcuEntity(String id, String bagimsizBolumId, String donem, BigDecimal anaPara, LocalDate sonOdemeTarihi) {
        this.id = id;
        this.bagimsizBolumId = bagimsizBolumId;
        this.donem = donem;
        this.anaPara = anaPara;
        this.sonOdemeTarihi = sonOdemeTarihi;
        this.durum = BorcDurumu.BEKLIYOR;
        this.gecikmeTazminati = BigDecimal.ZERO;
        this.createdAt = OffsetDateTime.now();
    }

    public BigDecimal getToplamTutar() {
        return anaPara.add(gecikmeTazminati);
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getBagimsizBolumId() { return bagimsizBolumId; }
    public void setBagimsizBolumId(String bagimsizBolumId) { this.bagimsizBolumId = bagimsizBolumId; }

    public String getDonem() { return donem; }
    public void setDonem(String donem) { this.donem = donem; }

    public BigDecimal getAnaPara() { return anaPara; }
    public void setAnaPara(BigDecimal anaPara) { this.anaPara = anaPara; }

    public LocalDate getSonOdemeTarihi() { return sonOdemeTarihi; }
    public void setSonOdemeTarihi(LocalDate sonOdemeTarihi) { this.sonOdemeTarihi = sonOdemeTarihi; }

    public BorcDurumu getDurum() { return durum; }
    public void setDurum(BorcDurumu durum) { this.durum = durum; }

    public BigDecimal getGecikmeTazminati() { return gecikmeTazminati; }
    public void setGecikmeTazminati(BigDecimal gecikmeTazminati) { this.gecikmeTazminati = gecikmeTazminati; }
}
