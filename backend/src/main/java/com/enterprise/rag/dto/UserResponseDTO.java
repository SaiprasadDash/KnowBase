
package com.enterprise.rag.dto;

import java.time.OffsetDateTime;
import java.util.UUID;

public record UserResponseDTO(
        UUID id,
        UUID tenantId,
        String fullName,
        String email,
        Boolean active,
        OffsetDateTime createdAt,
        OffsetDateTime updatedAt) {
}
