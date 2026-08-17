package taxflow.tax.domain

import java.math.BigDecimal
import java.math.RoundingMode
import java.time.Instant

data class CalculationLine(
    val component: TaxComponent,
    val expression: String,
    val baseAmount: BigDecimal,
    val rate: BigDecimal,
    val value: BigDecimal,
    val ruleId: String,
    val ruleVersion: String,
    val sourceDocumentIds: List<String>,
)

data class TaxResult(
    val baseAmount: BigDecimal,
    val taxAmount: BigDecimal,
    val netAmount: BigDecimal,
    val ruleId: String,
    val ruleVersion: String,
    val memory: List<CalculationLine>,
)

class TaxCalculator {
    fun calculate(base: BigDecimal, rule: TaxRule, occurredAt: Instant): TaxResult {
        require(rule.appliesAt(occurredAt)) { "rule is not effective at occurredAt" }
        return calculateComponents(base, listOf(rule), OperationFacts(occurredAt, "*", "*"), false)
    }

    fun calculateComponents(base: BigDecimal, rules: List<TaxRule>, facts: OperationFacts): TaxResult =
        calculateComponents(base, rules, facts, true)

    private fun calculateComponents(
        base: BigDecimal,
        rules: List<TaxRule>,
        facts: OperationFacts,
        validatePredicate: Boolean,
    ): TaxResult {
        require(base.signum() >= 0) { "baseAmount must be non-negative" }
        require(rules.isNotEmpty()) { "at least one tax component is required" }
        require(!validatePredicate || rules.all { it.matches(facts) }) { "rules must be approved, effective and matching" }
        require(rules.map { it.component }.distinct().size == rules.size) { "tax components must be unique" }
        val normalized = base.setScale(2, RoundingMode.HALF_EVEN)
        val memory = rules.sortedBy { it.component.name }.map { rule ->
            val amount = normalized.multiply(rule.rate).setScale(2, RoundingMode.HALF_EVEN)
            CalculationLine(rule.component, "base_amount * rate", normalized, rule.rate, amount,
                rule.id, rule.version, rule.sources.map { it.documentId })
        }
        val tax = memory.sumOf { it.value }.setScale(2, RoundingMode.HALF_EVEN)
        val primary = rules.first()
        return TaxResult(normalized, tax, normalized.subtract(tax), primary.id, primary.version, memory)
    }
}
