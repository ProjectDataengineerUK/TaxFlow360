package taxflow.tenant

import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*
import org.springframework.web.server.ResponseStatusException
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

@SpringBootApplication
class Application

fun main(args: Array<String>) = runApplication<Application>(*args)

enum class Role { ADMIN, FISCAL, FINANCE, ACCOUNTANT, BANK, CONSULTANT, AUDITOR }
data class CreateTenant(@field:NotBlank val legalName: String, @field:NotBlank val companyTaxId: String)
data class Tenant(val id: UUID, val legalName: String, val companyTaxId: String, val active: Boolean = true)
data class GrantRole(val userId: UUID, val role: Role)
data class TenantPrincipal(val tenantId: UUID, val userId: UUID)

class TenantRegistry {
    private val tenants = ConcurrentHashMap<UUID, Tenant>()
    private val roles = ConcurrentHashMap<Pair<UUID, UUID>, MutableSet<Role>>()
    fun create(command: CreateTenant, ownerUserId: UUID? = null): Tenant = Tenant(UUID.randomUUID(), command.legalName.trim(), command.companyTaxId.filter(Char::isDigit)).also {
        require(it.companyTaxId.length == 14) { "companyTaxId must contain 14 digits" }
        tenants[it.id] = it
        if (ownerUserId != null) grant(it.id, GrantRole(ownerUserId, Role.ADMIN))
    }
    fun find(id: UUID): Tenant = tenants[id] ?: throw NoSuchElementException("tenant not found")
    fun grant(tenantId: UUID, command: GrantRole): Set<Role> {
        find(tenantId)
        return roles.computeIfAbsent(tenantId to command.userId) { ConcurrentHashMap.newKeySet() }.apply { add(command.role) }.toSet()
    }
    fun authorize(tenantId: UUID, userId: UUID, role: Role) = roles[tenantId to userId]?.contains(role) == true
    fun authorize(principal: TenantPrincipal, resourceTenantId: UUID, requiredRole: Role) {
        require(principal.tenantId == resourceTenantId) { "cross-tenant access denied" }
        require(authorize(resourceTenantId, principal.userId, requiredRole)) { "required role not granted" }
    }
}

@RestController
@RequestMapping("/v1/tenants")
class TenantController(private val registry: TenantRegistry = TenantRegistry()) {
    @PostMapping @ResponseStatus(HttpStatus.CREATED)
    fun create(@RequestHeader("X-User-Id") ownerUserId: UUID, @Valid @RequestBody body: CreateTenant) = try {
        registry.create(body, ownerUserId)
    } catch (e: IllegalArgumentException) {
        throw ResponseStatusException(HttpStatus.BAD_REQUEST, e.message)
    }
    @GetMapping("/{id}")
    fun get(
        @PathVariable id: UUID,
        @RequestHeader("X-Tenant-Id") context: UUID,
        @RequestHeader("X-User-Id") userId: UUID,
    ): Tenant {
        val hasTenantRole = Role.entries.any { registry.authorize(context, userId, it) }
        if (id != context || !hasTenantRole) throw ResponseStatusException(HttpStatus.FORBIDDEN, "tenant access denied")
        return try { registry.find(id) } catch (_: NoSuchElementException) { throw ResponseStatusException(HttpStatus.NOT_FOUND) }
    }
    @PostMapping("/{id}/roles")
    fun grant(
        @PathVariable id: UUID,
        @RequestHeader("X-Tenant-Id") context: UUID,
        @RequestHeader("X-User-Id") userId: UUID,
        @Valid @RequestBody body: GrantRole,
    ): Set<Role> {
        try {
            registry.authorize(TenantPrincipal(context, userId), id, Role.ADMIN)
        } catch (error: IllegalArgumentException) {
            throw ResponseStatusException(HttpStatus.FORBIDDEN, error.message)
        }
        return registry.grant(id, body)
    }
}

@org.springframework.context.annotation.Configuration
class TenantConfiguration { @org.springframework.context.annotation.Bean fun tenantRegistry() = TenantRegistry() }
