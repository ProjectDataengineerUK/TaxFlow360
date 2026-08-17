package taxflow.reconciliation.domain

import java.math.BigDecimal
import java.time.Instant
import java.util.UUID

enum class Source { FISCAL, ERP, PAYMENT, SPLIT }
enum class Status { MATCHED, MATCHED_WITH_TOLERANCE, DIVERGENT, PENDING_HUMAN_REVIEW, RESOLVED, INVALIDATED }
enum class DivergenceType { MISSING_SOURCE, AMOUNT_MISMATCH, RULE_MISMATCH, RATE_MISMATCH, BASE_MISMATCH, ROUNDING_MISMATCH, STATUS_MISMATCH, DUPLICATE, TIMING }
enum class Severity { REVIEW, HIGH, CRITICAL }
data class Evidence(val simulationIds:Set<String> = emptySet(), val ruleIds:Set<String> = emptySet(), val memoryIds:Set<String> = emptySet(), val officialSourceIds:Set<String> = emptySet())
data class Policy(val version:String, val tolerance:BigDecimal, val high:BigDecimal, val critical:BigDecimal)
data class ReconcileCommand(val transactionId:String, val idempotencyKey:String, val amounts:Map<Source,BigDecimal?>, val sourceEventIds:Set<String>, val logicalCutoff:Instant, val evidence:Evidence=Evidence())
data class Result(val id:UUID, val version:Long, val transactionId:String, val status:Status, val type:DivergenceType?, val severity:Severity?, val difference:BigDecimal, val fingerprint:String, val policyVersion:String, val evidence:Evidence)
data class ReviewCommand(val decision:Status, val justification:String, val evidenceIds:Set<String>)
data class Review(val resultId:UUID, val previous:Status, val current:Status, val actor:UUID, val justification:String, val evidenceIds:Set<String>, val decidedAt:Instant)
