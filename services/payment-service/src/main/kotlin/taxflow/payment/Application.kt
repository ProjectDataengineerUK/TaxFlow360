package taxflow.payment

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*
import org.springframework.web.server.ResponseStatusException
import java.math.BigDecimal
import java.math.RoundingMode
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

@SpringBootApplication
class Application

fun main(args: Array<String>) = runApplication<Application>(*args)

enum class PaymentMethod { PIX, CARD, BOLETO, TRANSFER }
enum class PaymentStatus { SIMULATED, REVERSED, REFUNDED }

data class SplitRequest(
    val transactionId: String,
    val idempotencyKey: String,
    val grossAmount: BigDecimal,
    val taxAmount: BigDecimal,
    val method: PaymentMethod,
    val installments: Int = 1,
)

data class SplitInstallment(
    val number: Int,
    val grossAmount: BigDecimal,
    val taxAuthorityAmount: BigDecimal,
    val merchantAmount: BigDecimal,
)

data class SplitSimulation(
    val id: UUID,
    val transactionId: String,
    val fingerprint: String,
    val grossAmount: BigDecimal,
    val taxAuthorityAmount: BigDecimal,
    val merchantAmount: BigDecimal,
    val installmentAmounts: List<BigDecimal>,
    val installmentAllocations: List<SplitInstallment>,
    val method: PaymentMethod,
    val status: PaymentStatus,
    val reversedAmount: BigDecimal = BigDecimal("0.00"),
    val refundedAmount: BigDecimal = BigDecimal("0.00"),
)

fun allocate(total: BigDecimal, weights: List<BigDecimal>): List<BigDecimal> {
    require(total.signum() >= 0 && weights.isNotEmpty() && weights.all { it >= BigDecimal.ZERO })
    val denominator = weights.sumOf { it }
    require(denominator > BigDecimal.ZERO)
    val normalized = total.setScale(2, RoundingMode.HALF_EVEN)
    val allocated = weights.map {
        normalized.multiply(it).divide(denominator, 2, RoundingMode.HALF_EVEN)
    }.toMutableList()
    allocated[allocated.lastIndex] = allocated.last().add(normalized.subtract(allocated.sumOf { it }))
    check(allocated.sumOf { it } == normalized)
    return allocated
}

class PaymentEngine {
    private val simulations = ConcurrentHashMap<Pair<UUID, String>, SplitSimulation>()

    fun simulate(tenant: UUID, request: SplitRequest): SplitSimulation {
        require(request.transactionId.isNotBlank() && request.idempotencyKey.isNotBlank())
        require(request.grossAmount.signum() >= 0 && request.taxAmount.signum() >= 0)
        require(request.taxAmount <= request.grossAmount)
        require(request.installments in 1..48)
        val gross = request.grossAmount.setScale(2, RoundingMode.HALF_EVEN)
        val tax = request.taxAmount.setScale(2, RoundingMode.HALF_EVEN)
        require(tax <= gross)
        val fingerprint = fingerprint(request.copy(grossAmount = gross, taxAmount = tax))
        val key = tenant to request.idempotencyKey
        simulations[key]?.let {
            require(it.fingerprint == fingerprint) { "idempotency key already used with different input" }
            return it
        }
        val weights = List(request.installments) { BigDecimal.ONE }
        val grossParts = allocate(gross, weights)
        val taxParts = allocate(tax, weights)
        val allocations = grossParts.indices.map { index ->
            SplitInstallment(index + 1, grossParts[index], taxParts[index], grossParts[index] - taxParts[index])
        }
        val created = SplitSimulation(UUID.randomUUID(), request.transactionId, fingerprint, gross, tax, gross - tax,
            grossParts, allocations, request.method, PaymentStatus.SIMULATED)
        val previous = simulations.putIfAbsent(key, created)
        if (previous != null) {
            require(previous.fingerprint == fingerprint) { "idempotency key already used with different input" }
            return previous
        }
        return created
    }

    fun change(tenant: UUID, id: UUID, status: PaymentStatus): SplitSimulation {
        require(status != PaymentStatus.SIMULATED)
        val entry = simulations.entries.find { it.key.first == tenant && it.value.id == id }
            ?: throw NoSuchElementException("simulation not found")
        if (entry.value.status == status) return entry.value
        require(entry.value.status == PaymentStatus.SIMULATED) { "terminal payment status cannot be changed" }
        val updated = when (status) {
            PaymentStatus.REVERSED -> entry.value.copy(status = status, reversedAmount = entry.value.grossAmount)
            PaymentStatus.REFUNDED -> entry.value.copy(status = status, refundedAmount = entry.value.grossAmount)
            PaymentStatus.SIMULATED -> error("unreachable")
        }
        simulations[entry.key] = updated
        return updated
    }

    private fun fingerprint(request: SplitRequest): String {
        val value = listOf(request.transactionId, request.grossAmount.toPlainString(), request.taxAmount.toPlainString(),
            request.method, request.installments).joinToString("|")
        return MessageDigest.getInstance("SHA-256").digest(value.toByteArray()).joinToString("") { "%02x".format(it) }
    }
}

@RestController
@RequestMapping("/v1/payments")
class PaymentController(private val engine: PaymentEngine = PaymentEngine()) {
    @PostMapping("/splits")
    fun split(@RequestHeader("X-Tenant-Id") tenant: UUID, @RequestBody request: SplitRequest) = try {
        engine.simulate(tenant, request)
    } catch (error: IllegalArgumentException) {
        throw ResponseStatusException(HttpStatus.BAD_REQUEST, error.message)
    }

    @PostMapping("/{id}/reversal")
    fun reverse(@RequestHeader("X-Tenant-Id") tenant: UUID, @PathVariable id: UUID) =
        change(tenant, id, PaymentStatus.REVERSED)

    @PostMapping("/{id}/refund")
    fun refund(@RequestHeader("X-Tenant-Id") tenant: UUID, @PathVariable id: UUID) =
        change(tenant, id, PaymentStatus.REFUNDED)

    private fun change(tenant: UUID, id: UUID, status: PaymentStatus) = try {
        engine.change(tenant, id, status)
    } catch (_: NoSuchElementException) {
        throw ResponseStatusException(HttpStatus.NOT_FOUND)
    } catch (error: IllegalArgumentException) {
        throw ResponseStatusException(HttpStatus.CONFLICT, error.message)
    }
}

@org.springframework.context.annotation.Configuration
class PaymentConfiguration {
    @org.springframework.context.annotation.Bean
    fun paymentEngine() = PaymentEngine()
}
