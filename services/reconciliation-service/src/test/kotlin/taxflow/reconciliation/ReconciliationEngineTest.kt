package taxflow.reconciliation
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxflow.reconciliation.domain.*
import java.math.BigDecimal
import java.time.Instant
import java.util.UUID

class ReconciliationEngineTest {
 private fun command(key:String="key",amounts:Map<Source,BigDecimal?> = Source.entries.associateWith{"10.00".toBigDecimal()})=
  ReconcileCommand("tx",key,amounts,setOf("f","e","p","s"),Instant.parse("2026-08-17T00:00:00Z"))
 @Test fun `matches four equal sources and deduplicates`() { val e=ReconciliationEngine(); val t=UUID.randomUUID(); val a=e.reconcile(t,command()); assertEquals(Status.MATCHED,a.status); assertEquals(a.id,e.reconcile(t,command()).id) }
 @Test fun `classifies missing and amount mismatch`() { val e=ReconciliationEngine(); val t=UUID.randomUUID(); val missing=command("missing",Source.entries.associateWith{if(it==Source.PAYMENT)null else "10".toBigDecimal()}); assertEquals(DivergenceType.MISSING_SOURCE,e.reconcile(t,missing).type); val mismatch=command("mismatch",Source.entries.associateWith{if(it==Source.ERP)"11".toBigDecimal() else "10".toBigDecimal()}); assertEquals(DivergenceType.AMOUNT_MISMATCH,e.reconcile(t,mismatch).type) }
 @Test fun `critical requires authorized human review`() { val e=ReconciliationEngine(); val t=UUID.randomUUID(); val c=command("critical",Source.entries.associateWith{if(it==Source.ERP)"20000".toBigDecimal() else BigDecimal.ZERO}); assertEquals(Status.PENDING_HUMAN_REVIEW,e.reconcile(t,c).status); assertThrows(IllegalArgumentException::class.java){e.review(t,"critical",UUID.randomUUID(),emptySet(),ReviewCommand(Status.RESOLVED,"evidence",setOf("x")))}; assertEquals(Status.RESOLVED,e.review(t,"critical",UUID.randomUUID(),setOf("RECONCILIATION_REVIEWER"),ReviewCommand(Status.RESOLVED,"checked",setOf("x"))).current) }
 @Test fun `rejects conflicting idempotency payload`() { val e=ReconciliationEngine(); val t=UUID.randomUUID(); e.reconcile(t,command()); assertThrows(IdempotencyConflict::class.java){e.reconcile(t,command(amounts=Source.entries.associateWith{"20".toBigDecimal()}))} }
}
