package com.sitepulse.app.domain.usecase

import com.sitepulse.app.domain.model.AidatBorcu
import com.sitepulse.app.domain.model.BorcDurumu
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDate
import java.time.temporal.ChronoUnit

/**
 * Calculates accurate dues balances, including Kat Mülkiyeti Kanunu (KMK)
 * Article 20 statutory delay penalty (5% per month, pro-rated daily).
 */
class CalculateDuesUseCase {

    companion object {
        private val MONTHLY_PENALTY_RATE = BigDecimal("0.05") // %5 aylık gecikme tazminatı
        private val DAYS_IN_MONTH = BigDecimal("30")
    }

    fun execute(borc: AidatBorcu, today: LocalDate): AidatBorcu {
        if (borc.durum == BorcDurumu.ODENDI) {
            return borc
        }

        if (!today.isAfter(borc.sonOdemeTarihi)) {
            return borc.copy(durum = BorcDurumu.BEKLIYOR, gecikmeTazminati = BigDecimal.ZERO)
        }

        val daysOverdue = ChronoUnit.DAYS.between(borc.sonOdemeTarihi, today)
        if (daysOverdue <= 0) {
            return borc.copy(durum = BorcDurumu.BEKLIYOR, gecikmeTazminati = BigDecimal.ZERO)
        }

        // Delay = Principal * 0.05 * (daysOverdue / 30)
        val dailyRatio = BigDecimal(daysOverdue).divide(DAYS_IN_MONTH, 8, RoundingMode.HALF_UP)
        val penalty = borc.anaPara
            .multiply(MONTHLY_PENALTY_RATE)
            .multiply(dailyRatio)
            .setScale(2, RoundingMode.HALF_UP)

        return borc.copy(
            durum = BorcDurumu.GECIKMEDE,
            gecikmeTazminati = penalty
        )
    }
}
