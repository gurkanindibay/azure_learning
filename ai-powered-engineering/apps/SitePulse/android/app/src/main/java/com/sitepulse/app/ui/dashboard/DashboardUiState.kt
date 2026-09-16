package com.sitepulse.app.ui.dashboard

import com.sitepulse.app.domain.model.AidatBorcu
import com.sitepulse.app.domain.model.Daire
import java.math.BigDecimal

sealed interface DashboardUiState {
    object Loading : DashboardUiState

    data class Success(
        val aktifDaire: Daire,
        val borclar: List<AidatBorcu>,
        val toplamBorc: BigDecimal,
        val duyuruBasligi: String,
        val duyuruMetni: String,
        val isOverdue: Boolean
    ) : DashboardUiState

    data class Error(val message: String) : DashboardUiState
}
