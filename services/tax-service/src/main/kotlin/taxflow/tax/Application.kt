package taxflow.tax

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*
import org.springframework.web.server.ResponseStatusException
import taxflow.tax.domain.*
import java.math.BigDecimal
import java.time.Instant
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

@SpringBootApplication
class Application

fun main(args: Array<String>) = runApplication<Application>(*args)

data class CalculateRequest(
    val transactionId: String,
    val occurredAt: Instant,
    val baseAmount: BigDecimal,
    val ruleId: String,
)

data class CalculationResponse(
    val calculationId: UUID,
    val transactionId: String,
    val result: TaxResult,
    val eventId: UUID,
)

class TaxEngine(
    private val calculator: TaxCalculator = TaxCalculator(),
    private val allowedOfficialHosts: Set<String> = setOf("gov.br", "www.gov.br", "planalto.gov.br", "www.planalto.gov.br"),
) {
    private val rules = ConcurrentHashMap<String, MutableList<TaxRule>>()
    private val results = ConcurrentHashMap<Pair<UUID, String>, CalculationResponse>()
    private val simulations = ConcurrentHashMap<Pair<UUID, String>, SimulationResult>()

    fun publish(rule: TaxRule) {
        require(rule.status == RuleStatus.APPROVED) { "only approved rules can be published" }
        rule.sources.forEach { it.requireOfficialHost(allowedOfficialHosts) }
        val catalog = rules.computeIfAbsent(rule.id) { mutableListOf() }
        synchronized(catalog) {
            require(catalog.none { it.version == rule.version }) { "rule version already exists" }
            val ambiguous = catalog.any {
                it.status == RuleStatus.APPROVED && it.component == rule.component && it.priority == rule.priority &&
                    overlaps(it.validFrom, it.validUntil, rule.validFrom, rule.validUntil) && it.predicate == rule.predicate
            }
            require(!ambiguous) { "overlapping approved rules with equal precedence" }
            catalog.add(rule)
        }
    }

    fun calculate(tenant: UUID, request: CalculateRequest): CalculationResponse =
        results.computeIfAbsent(tenant to request.transactionId) {
            val rule = rules[request.ruleId]?.singleOrNull { it.appliesAt(request.occurredAt) }
                ?: throw RuleResolutionException("exactly one approved effective rule is required")
            CalculationResponse(UUID.randomUUID(), request.transactionId,
                calculator.calculate(request.baseAmount, rule, request.occurredAt), UUID.randomUUID())
        }

    fun simulate(tenant: UUID, request: SimulationRequest): SimulationResult {
        require(request.idempotencyKey.isNotBlank() && request.transactionId.isNotBlank())
        require(request.scenarios.isNotEmpty() && request.scenarios.size <= 3)
        val fingerprint = simulationFingerprint(tenant, request)
        val key = tenant to request.idempotencyKey
        simulations[key]?.let {
            require(it.fingerprint == fingerprint) { "idempotency key already used with different input" }
            return it
        }
        val catalog = rules.values.flatten().filter { it.version == request.ruleSetVersion }
        val scenarioResults = request.scenarios.sortedBy { it.name }.map { scenario ->
            val components = when (scenario) {
                ScenarioType.CURRENT -> listOf(TaxComponent.CURRENT)
                ScenarioType.TRANSITION -> listOf(TaxComponent.CURRENT, TaxComponent.CBS, TaxComponent.IBS)
                ScenarioType.CBS_IBS -> listOf(TaxComponent.CBS, TaxComponent.IBS)
            }
            val selected = components.map { selectRule(catalog, request.facts, it) }
            ScenarioResult(scenario, calculator.calculateComponents(request.baseAmount, selected, request.facts))
        }
        val current = scenarioResults.firstOrNull { it.scenario == ScenarioType.CURRENT }?.result?.taxAmount
            ?: scenarioResults.first().result.taxAmount
        val deltas = scenarioResults.associate { it.scenario to it.result.taxAmount.subtract(current) }
        val created = SimulationResult(UUID.nameUUIDFromBytes(fingerprint.toByteArray()), tenant,
            request.transactionId, fingerprint, request.ruleSetVersion, scenarioResults, deltas, request.facts.effectiveAt)
        val previous = simulations.putIfAbsent(key, created)
        if (previous != null) {
            require(previous.fingerprint == fingerprint) { "idempotency key already used with different input" }
            return previous
        }
        return created
    }

    fun simulation(tenant: UUID, id: UUID): SimulationResult = simulations.values.singleOrNull {
        it.tenantId == tenant && it.simulationId == id
    } ?: throw NoSuchElementException("simulation not found")

    private fun overlaps(aFrom: Instant, aUntil: Instant?, bFrom: Instant, bUntil: Instant?): Boolean =
        (aUntil == null || bFrom < aUntil) && (bUntil == null || aFrom < bUntil)
}

@RestController
@RequestMapping("/v1/tax")
class TaxController(private val engine: TaxEngine = TaxEngine()) {
    @PostMapping("/rules")
    @ResponseStatus(HttpStatus.CREATED)
    fun rule(@RequestHeader("X-Tenant-Id") tenant: UUID, @RequestBody rule: TaxRule): TaxRule = try {
        engine.publish(rule)
        rule
    } catch (error: IllegalArgumentException) {
        throw ResponseStatusException(HttpStatus.BAD_REQUEST, error.message)
    }

    @PostMapping("/calculations")
    fun calculate(@RequestHeader("X-Tenant-Id") tenant: UUID, @RequestBody body: CalculateRequest) = try {
        engine.calculate(tenant, body)
    } catch (error: RuleResolutionException) {
        throw ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY, error.message)
    }

    @PostMapping("/simulations")
    @ResponseStatus(HttpStatus.CREATED)
    fun simulate(@RequestHeader("X-Tenant-Id") tenant: UUID, @RequestBody body: SimulationRequest) = try {
        engine.simulate(tenant, body)
    } catch (error: RuleResolutionException) {
        throw ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY, error.message)
    } catch (error: IllegalArgumentException) {
        throw ResponseStatusException(HttpStatus.CONFLICT, error.message)
    }

    @GetMapping("/simulations/{id}")
    fun simulation(@RequestHeader("X-Tenant-Id") tenant: UUID, @PathVariable id: UUID) = try {
        engine.simulation(tenant, id)
    } catch (_: NoSuchElementException) {
        throw ResponseStatusException(HttpStatus.NOT_FOUND)
    }
}

@org.springframework.context.annotation.Configuration
class TaxConfiguration {
    @org.springframework.context.annotation.Bean
    fun taxEngine() = TaxEngine()
}
