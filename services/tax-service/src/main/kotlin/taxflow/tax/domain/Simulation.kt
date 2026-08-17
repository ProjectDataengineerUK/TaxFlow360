package taxflow.tax.domain

import java.math.BigDecimal
import java.security.MessageDigest
import java.time.Instant
import java.util.UUID

enum class ScenarioType { CURRENT, TRANSITION, CBS_IBS }
data class ScenarioResult(val scenario: ScenarioType, val result: TaxResult)

data class SimulationRequest(
    val transactionId: String,
    val idempotencyKey: String,
    val baseAmount: BigDecimal,
    val facts: OperationFacts,
    val ruleSetVersion: String,
    val scenarios: Set<ScenarioType>,
)

data class SimulationResult(
    val simulationId: UUID,
    val tenantId: UUID,
    val transactionId: String,
    val fingerprint: String,
    val ruleSetVersion: String,
    val scenarios: List<ScenarioResult>,
    val deltasFromCurrent: Map<ScenarioType, BigDecimal>,
    val createdAt: Instant,
)

fun simulationFingerprint(tenantId: UUID, request: SimulationRequest): String {
    val canonical = listOf(tenantId, request.transactionId, request.baseAmount.toPlainString(),
        request.facts.effectiveAt, request.facts.jurisdiction, request.facts.operationType,
        request.facts.productCode ?: "", request.ruleSetVersion,
        request.scenarios.sortedBy { it.name }.joinToString(",")).joinToString("|")
    return MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray())
        .joinToString("") { "%02x".format(it) }
}
