package taxflow.payment

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import java.math.BigDecimal
import java.util.UUID

class PaymentEngineTest {
    @Test
    fun `split preserves gross tax merchant and residual cents`() {
        val engine = PaymentEngine()
        val tenant = UUID.randomUUID()
        val request = SplitRequest("tx", "key", BigDecimal("100.00"), BigDecimal("12.34"), PaymentMethod.PIX, 3)
        val result = engine.simulate(tenant, request)
        assertEquals(result.id, engine.simulate(tenant, request).id)
        assertEquals(result.grossAmount, result.taxAuthorityAmount + result.merchantAmount)
        assertEquals(result.grossAmount, result.installmentAllocations.sumOf { it.grossAmount })
        assertEquals(result.taxAuthorityAmount, result.installmentAllocations.sumOf { it.taxAuthorityAmount })
        result.installmentAllocations.forEach {
            assertEquals(it.grossAmount, it.taxAuthorityAmount + it.merchantAmount)
        }
    }

    @Test
    fun `idempotency key rejects different input`() {
        val engine = PaymentEngine()
        val tenant = UUID.randomUUID()
        engine.simulate(tenant, SplitRequest("tx", "key", BigDecimal("10"), BigDecimal("1"), PaymentMethod.CARD))
        assertThrows(IllegalArgumentException::class.java) {
            engine.simulate(tenant, SplitRequest("tx", "key", BigDecimal("11"), BigDecimal("1"), PaymentMethod.CARD))
        }
    }

    @Test
    fun `reversal and refund are terminal idempotent states`() {
        val tenant = UUID.randomUUID()
        val reversedEngine = PaymentEngine()
        val reversed = reversedEngine.simulate(tenant,
            SplitRequest("tx-r", "key-r", BigDecimal("10"), BigDecimal("1"), PaymentMethod.PIX))
        val firstReversal = reversedEngine.change(tenant, reversed.id, PaymentStatus.REVERSED)
        assertEquals(BigDecimal("10.00"), firstReversal.reversedAmount)
        assertEquals(firstReversal, reversedEngine.change(tenant, reversed.id, PaymentStatus.REVERSED))
        assertThrows(IllegalArgumentException::class.java) {
            reversedEngine.change(tenant, reversed.id, PaymentStatus.REFUNDED)
        }

        val refundedEngine = PaymentEngine()
        val refunded = refundedEngine.simulate(tenant,
            SplitRequest("tx-f", "key-f", BigDecimal("10"), BigDecimal("1"), PaymentMethod.PIX))
        assertEquals(BigDecimal("10.00"), refundedEngine.change(tenant, refunded.id, PaymentStatus.REFUNDED).refundedAmount)
    }

    @Test
    fun `zero split remains valid`() {
        val result = PaymentEngine().simulate(UUID.randomUUID(),
            SplitRequest("zero", "zero", BigDecimal.ZERO, BigDecimal.ZERO, PaymentMethod.TRANSFER, 2))
        assertEquals(listOf(BigDecimal("0.00"), BigDecimal("0.00")), result.installmentAmounts)
    }
}
