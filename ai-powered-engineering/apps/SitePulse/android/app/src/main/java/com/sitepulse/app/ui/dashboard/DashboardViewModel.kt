package com.sitepulse.app.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sitepulse.app.domain.model.AidatBorcu
import com.sitepulse.app.domain.model.BorcDurumu
import com.sitepulse.app.domain.model.Daire
import com.sitepulse.app.domain.usecase.CalculateDuesUseCase
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.math.BigDecimal
import java.time.LocalDate

class DashboardViewModel(
    private val calculateDuesUseCase: CalculateDuesUseCase = CalculateDuesUseCase()
) : ViewModel() {

    private val _uiState = MutableStateFlow<DashboardUiState>(DashboardUiState.Loading)
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()

    init {
        loadDashboard()
    }

    fun loadDashboard() {
        viewModelScope.launch {
            val daire = Daire(
                id = "d-14",
                siteAdi = "Begonya Sitesi",
                blok = "A",
                daireNo = 14,
                kat = 4,
                arsaPayi = 24,
                malikAdi = "Ahmet Yılmaz",
                kiraciAdi = "Zeynep Kaya"
            )

            // Overdue dues scenario (10 days overdue per Spec-001)
            val baseBorc = AidatBorcu(
                id = "b-101",
                daireId = "d-14",
                donem = "Eylül 2026",
                anaPara = BigDecimal("1400.00"),
                sonOdemeTarihi = LocalDate.of(2026, 9, 15),
                durum = BorcDurumu.BEKLIYOR
            )

            val evaluatedBorc = calculateDuesUseCase.execute(baseBorc, LocalDate.of(2026, 9, 25))
            val isOverdue = evaluatedBorc.durum == BorcDurumu.GECIKMEDE

            _uiState.value = DashboardUiState.Success(
                aktifDaire = daire,
                borclar = listOf(evaluatedBorc),
                toplamBorc = evaluatedBorc.toplamTutar,
                duyuruBasligi = "Planlı Su Kesintisi Hakkında",
                duyuruMetni = "İSKİ ana hat yenilemesi sebebiyle 18 Eylül 10:00 - 14:00 arası su kesilecektir.",
                isOverdue = isOverdue
            )
        }
    }
}
