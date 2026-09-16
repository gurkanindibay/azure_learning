package com.sitepulse.backend.repository;

import com.sitepulse.backend.domain.entity.AidatBorcuEntity;
import com.sitepulse.backend.domain.entity.BorcDurumu;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AidatBorcuRepository extends JpaRepository<AidatBorcuEntity, String> {
    List<AidatBorcuEntity> findByBagimsizBolumId(String bagimsizBolumId);
    List<AidatBorcuEntity> findByBagimsizBolumIdAndDurumNot(String bagimsizBolumId, BorcDurumu durum);
}
