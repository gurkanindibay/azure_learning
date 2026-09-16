package com.sitepulse.backend.service;

import com.sitepulse.backend.domain.entity.AidatBorcuEntity;
import com.sitepulse.backend.domain.entity.BorcDurumu;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/**
 * Spring Service implementing statutory delay fee calculations
 * per Kat Mülkiyeti Kanunu (KMK - Law 634, Article 20).
 */
@Service
public class AidatCalculationService {

    private static final BigDecimal MONTHLY_RATE = new BigDecimal("0.05"); // 5% monthly rate
    private static final BigDecimal DAYS_IN_MONTH = new BigDecimal("30");

    /**
     * Calculates the KMK Article 20 delay penalty pro-rated per day.
     * Penalty = Principal * 0.05 * (DaysOverdue / 30)
     */
    public AidatBorcuEntity calculateDelayPenalty(AidatBorcuEntity borc, LocalDate evaluationDate) {
        if (borc.getDurum() == BorcDurumu.ODENDI) {
            return borc;
        }

        if (!evaluationDate.isAfter(borc.getSonOdemeTarihi())) {
            borc.setDurum(BorcDurumu.BEKLIYOR);
            borc.setGecikmeTazminati(BigDecimal.ZERO);
            return borc;
        }

        long daysOverdue = ChronoUnit.DAYS.between(borc.getSonOdemeTarihi(), evaluationDate);
        if (daysOverdue <= 0) {
            borc.setDurum(BorcDurumu.BEKLIYOR);
            borc.setGecikmeTazminati(BigDecimal.ZERO);
            return borc;
        }

        BigDecimal days = BigDecimal.valueOf(daysOverdue);
        BigDecimal dailyRatio = days.divide(DAYS_IN_MONTH, 8, RoundingMode.HALF_UP);
        BigDecimal penalty = borc.getAnaPara()
                .multiply(MONTHLY_RATE)
                .multiply(dailyRatio)
                .setScale(2, RoundingMode.HALF_UP);

        borc.setDurum(BorcDurumu.GECIKMEDE);
        borc.setGecikmeTazminati(penalty);
        return borc;
    }
}
