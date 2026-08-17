package taxflow.tax.domain

import java.math.BigDecimal
import java.time.Instant

enum class RuleStatus { DRAFT, APPROVED }
enum class TaxComponent { CURRENT, CBS, IBS }

data class OperationFacts(
    val effectiveAt: Instant,
    val jurisdiction: String,
    val operationType: String,
    val productCode: String? = null,
)

data class RulePredicate(
    val jurisdiction: String? = null,
    val operationType: String? = null,
    val productCode: String? = null,
) {
    fun matches(facts: OperationFacts): Boolean =
        (jurisdiction == null || jurisdiction == facts.jurisdiction) &&
            (operationType == null || operationType == facts.operationType) &&
            (productCode == null || productCode == facts.productCode)
}

data class TaxRule(
    val id: String,
    val version: String,
    val validFrom: Instant,
    val validUntil: Instant?,
    val rate: BigDecimal,
    val legalBasis: String,
    val authorId: String,
    val approverId: String?,
    val status: RuleStatus,
    val component: TaxComponent = TaxComponent.CURRENT,
    val priority: Int = 0,
    val predicate: RulePredicate = RulePredicate(),
    val sources: List<LegalSource> = emptyList(),
) {
    init {
        require(id.isNotBlank() && version.isNotBlank())
        require(rate >= BigDecimal.ZERO && rate <= BigDecimal.ONE)
        require(legalBasis.isNotBlank())
        require(validUntil == null || validUntil > validFrom)
        require(status != RuleStatus.APPROVED || (approverId != null && approverId != authorId)) {
            "approved rule requires a distinct approver"
        }
        require(status != RuleStatus.APPROVED || sources.isNotEmpty()) {
            "approved rule requires an official legal source"
        }
    }

    fun appliesAt(at: Instant): Boolean =
        status == RuleStatus.APPROVED && !at.isBefore(validFrom) && (validUntil == null || at.isBefore(validUntil))

    fun matches(facts: OperationFacts): Boolean = appliesAt(facts.effectiveAt) && predicate.matches(facts)
}

class RuleResolutionException(message: String) : IllegalArgumentException(message)

fun selectRule(rules: List<TaxRule>, facts: OperationFacts, component: TaxComponent): TaxRule {
    val candidates = rules.filter { it.component == component && it.matches(facts) }
    val priority = candidates.maxOfOrNull { it.priority }
        ?: throw RuleResolutionException("no approved effective rule for $component")
    return candidates.filter { it.priority == priority }.singleOrNull()
        ?: throw RuleResolutionException("ambiguous approved effective rules for $component")
}
