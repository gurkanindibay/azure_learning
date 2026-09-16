package com.sitepulse.app.domain.usecase

import com.sitepulse.app.domain.model.AidatBorcu
import com.sitepulse.app.domain.model.BorcDurumu
import org.junit.Assert.assertEquals
import org.junit.Test
import java.math.BigDecimal
import java.time.LocalDate

class CalculateDuesUseCaseTest {

    private val useCase = CalculateDuesUseCase()

    @Test
    fun `when dues are overdue by 10 days, calculates exact 5 percent pro-rated KMK penalty`() {
        // Principal: ₺1400.00, Due: 15 Sep, Today: 25 Sep (10 days overdue)
        // 1400 * 0.05 * (10 / 30) = 23.333... -> ₺23.33
        // Total: ₺1423.33
        val dueDate = LocalDate.of(2026, 9, 15)
        val today = LocalDate.of(2026, 9, 25)

        val borc = AidatBorcu(
            id = "b-01",
            daireId = "d-14",
            donem = "Eylül 2026",
            anaPara = BigDecimal("1400.00"),
            sonOdemeTarihi = dueDate,
            durum = BorcDurumu.BEKLIYOR
        )

        val result = useCase.execute(borc, today)

        assertEquals(BorcDurumu.GECIKMEDE, result.durum)
        assertEquals(BigDecimal("23.33"), result.gecikmeTazminati)
        assertEquals(BigDecimal("1423.33"), result.toplamTutar)
    }

    @Test
    fun `when dues are not overdue, penalty remains zero`() {
        val dueDate = LocalDate.of(2026, 9, 30)
        val today = LocalDate.of(2026, 9, 25)

        val borc = AidatBorcu(
            id = "b-02",
            daireId = "d-14",
            donem = "Eylül 2026",
            anaPara = BigDecimal("1400.00"),
            sonOdemeTarihi = dueDate,
            durum = BorcDurumu.BEKLIYOR
        )

        val result = useCase.execute(borc, today)

        assertEquals(BorcDurumu.BEKLIYOR, result.durum)
        assertEquals(BigDecimal.ZERO, result.gecikmeTazminati)
        assertEquals(BigDecimal("1400.00"), result.toplamTutar)
    }
}
