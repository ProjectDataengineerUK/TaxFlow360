package taxflow.tax.domain

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import java.math.BigDecimal
import java.net.URI
import java.time.Instant
import java.time.LocalDate
import java.util.UUID

class TaxCalculatorTest {
    private val at = Instant.parse("2027-01-01T00:00:00Z")
    private val source = LegalSource(URI("https://www.gov.br/receitafederal/reference"),
        "Receita Federal do Brasil", "synthetic-reference", "test provision", LocalDate.parse("2026-01-01"),
        at, "a".repeat(64))

    @Test
    fun `calculates components with half even and complete memory`() {
        val current = rule("CURRENT", TaxComponent.CURRENT, "0.10")
        val cbs = rule("CBS", TaxComponent.CBS, "0.009")
        val result = TaxCalculator().calculateComponents(BigDecimal("100.00"), listOf(current, cbs), facts())
        assertEquals(BigDecimal("10.90"), result.taxAmount)
        assertEquals(2, result.memory.size)
        assertEquals(listOf("synthetic-reference"), result.memory.first().sourceDocumentIds)
    }

    @Test
    fun `selects only one approved effective highest priority rule`() {
        val low = rule("CBS-low", TaxComponent.CBS, "0.01", priority = 1)
        val high = rule("CBS-high", TaxComponent.CBS, "0.02", priority = 2)
        assertEquals(high, selectRule(listOf(low, high), facts(), TaxComponent.CBS))
        assertThrows(RuleResolutionException::class.java) {
            selectRule(listOf(high, high.copy(id = "CBS-tie")), facts(), TaxComponent.CBS)
        }
    }

    @Test
    fun `approved rule requires distinct approver and official source`() {
        assertThrows(IllegalArgumentException::class.java) {
            TaxRule("CBS", "1", at, null, BigDecimal("0.10"), "basis", "same", "same", RuleStatus.APPROVED)
        }
        assertThrows(IllegalArgumentException::class.java) {
            source.requireOfficialHost(setOf("evil.example"))
        }
    }

    @Test
    fun `simulation fingerprint is deterministic and tenant scoped`() {
        val request = SimulationRequest("tx", "key", BigDecimal("100.00"), facts(), "1", setOf(ScenarioType.CURRENT))
        assertEquals(simulationFingerprint(UUID(0, 1), request), simulationFingerprint(UUID(0, 1), request))
        require(simulationFingerprint(UUID(0, 1), request) != simulationFingerprint(UUID(0, 2), request))
    }

    private fun facts() = OperationFacts(at, "BR", "SALE")

    private fun rule(id: String, component: TaxComponent, rate: String, priority: Int = 0) =
        TaxRule(id, "1", at, null, BigDecimal(rate), "synthetic legal basis", "author", "approver",
            RuleStatus.APPROVED, component, priority, RulePredicate("BR", "SALE"), listOf(source))
}
