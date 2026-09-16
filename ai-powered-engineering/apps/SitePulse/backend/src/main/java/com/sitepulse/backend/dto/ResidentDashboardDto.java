package com.sitepulse.backend.dto;

import java.math.BigDecimal;
import java.util.List;

public record ResidentDashboardDto(
        String unitId,
        String unitName,
        BigDecimal totalDebt,
        boolean isOverdue,
        List<DuesSummaryDto> dues,
        String announcementTitle,
        String announcementBody
) {
    public record DuesSummaryDto(
            String id,
            String period,
            BigDecimal principal,
            BigDecimal delayPenalty,
            BigDecimal totalAmount,
            String dueDate,
            String status
    ) {}
}
