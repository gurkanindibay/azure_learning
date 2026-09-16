package com.sitepulse.app.domain.model

/**
 * Represents an independent apartment or property unit (Bağımsız Bölüm) within a complex.
 */
data class Daire(
    val id: String,
    val siteAdi: String,
    val blok: String,
    val daireNo: Int,
    val kat: Int,
    val arsaPayi: Int, // e.g. 24/1000 share
    val malikAdi: String,
    val kiraciAdi: String? = null
) {
    val tamAd: String
        get() = "$siteAdi • $blok Blok D:$daireNo"
}
