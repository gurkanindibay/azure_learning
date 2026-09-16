package com.sitepulse.backend.service;

import com.sitepulse.backend.domain.entity.AidatBorcuEntity;
import com.sitepulse.backend.domain.entity.BorcDurumu;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.assertEquals;

class AidatCalculationServiceTest {

    private final AidatCalculationService service = new AidatCalculationService();

    @Test
    void whenOverdueBy10Days_thenCalculatesExact5PercentProRatedPenalty() {
        // Principal: ₺1400.00, Due: 15 Sep 2026, Evaluation: 25 Sep 2026 (10 days)
        // 1400 * 0.05 * (10 / 30) = 23.3333... -> ₺23.33
        // Total: ₺1423.33
        LocalDate dueDate = LocalDate.of(2026, 9, 15);
        LocalDate evalDate = LocalDate.of(2026, 9, 25);

        AidatBorcuEntity borc = new AidatBorcuEntity(
                "b-01", "d-14", "Eylül 2026",
                new BigDecimal("1400.00"), dueDate
        );

        AidatBorcuEntity result = service.calculateDelayPenalty(borc, evalDate);

        assertEquals(BorcDurumu.GECIKMEDE, result.getDurum());
        assertEquals(new BigDecimal("23.33"), result.getGecikmeTazminati());
        assertEquals(new BigDecimal("1423.33"), result.getToplamTutar());
    }

    @Test
    void whenNotOverdue_thenPenaltyRemainsZero() {
        LocalDate dueDate = LocalDate.of(2026, 9, 30);
        LocalDate evalDate = LocalDate.of(2026, 9, 25);

        AidatBorcuEntity borc = new AidatBorcuEntity(
                "b-02", "d-14", "Eylül 2026",
                new BigDecimal("1400.00"), dueDate
        );

        AidatBorcuEntity result = service.calculateDelayPenalty(borc, evalDate);

        assertEquals(BorcDurumu.BEKLIYOR, result.getDurum());
        assertEquals(BigDecimal.ZERO, result.getGecikmeTazminati());
        assertEquals(new BigDecimal("1400.00"), result.getToplamTutar());
    }
}
