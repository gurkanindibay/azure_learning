package com.sitepulse.backend.repository;

import com.sitepulse.backend.domain.entity.BagimsizBolumEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface BagimsizBolumRepository extends JpaRepository<BagimsizBolumEntity, String> {
    List<BagimsizBolumEntity> findByBlokId(String blokId);
    List<BagimsizBolumEntity> findByMalikId(String malikId);
    List<BagimsizBolumEntity> findByKiraciId(String kiraciId);
}
