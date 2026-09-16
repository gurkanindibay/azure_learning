package com.sitepulse.backend.controller;

import com.sitepulse.backend.domain.entity.AidatBorcuEntity;
import com.sitepulse.backend.domain.entity.BagimsizBolumEntity;
import com.sitepulse.backend.domain.entity.BorcDurumu;
import com.sitepulse.backend.dto.ResidentDashboardDto;
import com.sitepulse.backend.repository.AidatBorcuRepository;
import com.sitepulse.backend.repository.BagimsizBolumRepository;
import com.sitepulse.backend.service.AidatCalculationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/v1/residents")
@CrossOrigin(origins = "*")
public class ResidentDashboardController {

    private final BagimsizBolumRepository bagimsizBolumRepository;
    private final AidatBorcuRepository aidatBorcuRepository;
    private final AidatCalculationService calculationService;

    public ResidentDashboardController(
            BagimsizBolumRepository bagimsizBolumRepository,
            AidatBorcuRepository aidatBorcuRepository,
            AidatCalculationService calculationService
    ) {
        this.bagimsizBolumRepository = bagimsizBolumRepository;
        this.aidatBorcuRepository = aidatBorcuRepository;
        this.calculationService = calculationService;
    }

    @GetMapping("/{unitId}/dashboard")
    public ResponseEntity<ResidentDashboardDto> getDashboardSummary(@PathVariable String unitId) {
        BagimsizBolumEntity unit = bagimsizBolumRepository.findById(unitId)
                .orElse(new BagimsizBolumEntity(unitId, "b-A", 14, 4, 24, "m-01", "k-01"));

        List<AidatBorcuEntity> rawDues = aidatBorcuRepository.findByBagimsizBolumIdAndDurumNot(unitId, BorcDurumu.ODENDI);
        LocalDate today = LocalDate.now();

        List<AidatBorcuEntity> evaluatedDues = rawDues.stream()
                .map(borc -> calculationService.calculateDelayPenalty(borc, today))
                .toList();

        BigDecimal totalDebt = evaluatedDues.stream()
                .map(AidatBorcuEntity::getToplamTutar)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        boolean isOverdue = evaluatedDues.stream()
                .anyMatch(b -> b.getDurum() == BorcDurumu.GECIKMEDE);

        List<ResidentDashboardDto.DuesSummaryDto> duesDtos = evaluatedDues.stream()
                .map(b -> new ResidentDashboardDto.DuesSummaryDto(
                        b.getId(),
                        b.getDonem(),
                        b.getAnaPara(),
                        b.getGecikmeTazminati(),
                        b.getToplamTutar(),
                        b.getSonOdemeTarihi().toString(),
                        b.getDurum().name()
                ))
                .toList();

        ResidentDashboardDto response = new ResidentDashboardDto(
                unit.getId(),
                "Begonya Sitesi • A Blok D:" + unit.getDaireNo(),
                totalDebt,
                isOverdue,
                duesDtos,
                "Planlı Su Kesintisi Hakkında",
                "İSKİ ana hat yenilemesi sebebiyle 18 Eylül 10:00 - 14:00 arası su kesilecektir."
        );

        return ResponseEntity.ok(response);
    }
}
