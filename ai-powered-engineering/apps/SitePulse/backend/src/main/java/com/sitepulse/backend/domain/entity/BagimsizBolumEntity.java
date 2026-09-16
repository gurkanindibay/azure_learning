package com.sitepulse.backend.domain.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "bagimsiz_bolumler", uniqueConstraints = {
    @UniqueConstraint(name = "uq_blok_daire", columnNames = {"blok_id", "daire_no"})
})
public class BagimsizBolumEntity {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "blok_id", length = 36, nullable = false)
    private String blokId;

    @Column(name = "daire_no", nullable = false)
    private Integer daireNo;

    @Column(nullable = false)
    private Integer kat;

    @Column(name = "arsa_payi", nullable = false)
    private Integer arsaPayi;

    @Column(name = "malik_id", length = 36, nullable = false)
    private String malikId;

    @Column(name = "kiraci_id", length = 36)
    private String kiraciId;

    @Version
    private Integer version;

    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    public BagimsizBolumEntity() {}

    public BagimsizBolumEntity(String id, String blokId, Integer daireNo, Integer kat, Integer arsaPayi, String malikId, String kiraciId) {
        this.id = id;
        this.blokId = blokId;
        this.daireNo = daireNo;
        this.kat = kat;
        this.arsaPayi = arsaPayi;
        this.malikId = malikId;
        this.kiraciId = kiraciId;
        this.createdAt = OffsetDateTime.now();
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getBlokId() { return blokId; }
    public void setBlokId(String blokId) { this.blokId = blokId; }

    public Integer getDaireNo() { return daireNo; }
    public void setDaireNo(Integer daireNo) { this.daireNo = daireNo; }

    public Integer getKat() { return kat; }
    public void setKat(Integer kat) { this.kat = kat; }

    public Integer getArsaPayi() { return arsaPayi; }
    public void setArsaPayi(Integer arsaPayi) { this.arsaPayi = arsaPayi; }

    public String getMalikId() { return malikId; }
    public void setMalikId(String malikId) { this.malikId = malikId; }

    public String getKiraciId() { return kiraciId; }
    public void setKiraciId(String kiraciId) { this.kiraciId = kiraciId; }

    public Integer getVersion() { return version; }
}
