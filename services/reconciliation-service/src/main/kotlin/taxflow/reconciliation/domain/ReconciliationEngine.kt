package taxflow.reconciliation.domain

import java.math.RoundingMode
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.time.Instant
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

class IdempotencyConflict: IllegalStateException("idempotency key reused with different content")

class ReconciliationEngine(private val policy:Policy=Policy("1.0.0","0.01".toBigDecimal(),"1000".toBigDecimal(),"10000".toBigDecimal())) {
 private val results=ConcurrentHashMap<Pair<UUID,String>,Result>()
 private val reviews=ConcurrentHashMap<UUID,List<Review>>()
 fun reconcile(tenant:UUID, command:ReconcileCommand):Result {
  require(command.amounts.keys.containsAll(Source.entries)); require(command.sourceEventIds.isNotEmpty())
  val fingerprint=sha256(listOf(tenant,command.transactionId,command.sourceEventIds.sorted(),policy.version,command.logicalCutoff).joinToString("|"))
  val key=tenant to command.idempotencyKey
  val existing=results[key]
  if(existing!=null) { if(existing.fingerprint!=fingerprint) throw IdempotencyConflict(); return existing }
  val missing=command.amounts.filterValues{it==null}.keys
  val values=command.amounts.values.filterNotNull().map{it.setScale(2,RoundingMode.HALF_EVEN)}
  val difference=if(values.isEmpty()) "0.00".toBigDecimal() else values.maxOrNull()!!.subtract(values.minOrNull()!!).abs()
  val type=when { missing.isNotEmpty()->DivergenceType.MISSING_SOURCE; difference.signum()==0->null; difference<=policy.tolerance->DivergenceType.ROUNDING_MISMATCH; else->DivergenceType.AMOUNT_MISMATCH }
  val severity=when { type==null||type==DivergenceType.ROUNDING_MISMATCH->null; difference>=policy.critical->Severity.CRITICAL; difference>=policy.high->Severity.HIGH; else->Severity.REVIEW }
  val status=when { severity==Severity.CRITICAL->Status.PENDING_HUMAN_REVIEW; type==null->Status.MATCHED; type==DivergenceType.ROUNDING_MISMATCH->Status.MATCHED_WITH_TOLERANCE; else->Status.DIVERGENT }
  val result=Result(UUID.nameUUIDFromBytes(fingerprint.toByteArray()),1,command.transactionId,status,type,severity,difference,fingerprint,policy.version,command.evidence)
  val raced=results.putIfAbsent(key,result); if(raced!=null && raced.fingerprint!=fingerprint) throw IdempotencyConflict(); return raced?:result
 }
 fun review(tenant:UUID,idempotencyKey:String,actor:UUID,roles:Set<String>,command:ReviewCommand):Review {
  require("RECONCILIATION_REVIEWER" in roles); require(command.justification.isNotBlank()); require(command.decision in setOf(Status.RESOLVED,Status.INVALIDATED))
  val result=results[tenant to idempotencyKey]?:throw NoSuchElementException("reconciliation not found")
  require(result.status==Status.PENDING_HUMAN_REVIEW||result.status==Status.DIVERGENT)
  val review=Review(result.id,result.status,command.decision,actor,command.justification,command.evidenceIds,Instant.now())
  reviews.compute(result.id){_,history->(history?:emptyList())+review}; return review
 }
 private fun sha256(value:String)=MessageDigest.getInstance("SHA-256").digest(value.toByteArray(StandardCharsets.UTF_8)).joinToString(""){"%02x".format(it)}
}
