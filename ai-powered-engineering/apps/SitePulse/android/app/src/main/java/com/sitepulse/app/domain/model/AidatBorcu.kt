package com.sitepulse.app.domain.model

import java.math.BigDecimal
import java.time.LocalDate

enum class BorcDurumu {
    ODENDI,
    BEKLIYOR,
    GECIKMEDE
}

/**
 * Represents a monthly dues obligation (Aidat Tahakkuku).
 * Strict BigDecimal usage to prevent floating-point rounding errors per Constitution.
 */
data class AidatBorcu(
    val id: String,
    val daireId: String,
    val donem: String, // e.g. "Eylül 2026"
    val anaPara: BigDecimal,
    val sonOdemeTarihi: LocalDate,
    val durum: BorcDurumu,
    val gecikmeTazminati: BigDecimal = BigDecimal.ZERO
) {
    val toplamTutar: BigDecimal
        get() = anaPara.add(gecikmeTazminati)
}
