package taxflow.tenant
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import java.util.UUID
class TenantRegistryTest {
 @Test fun `creates tenant and grants isolated role`() { val r=TenantRegistry(); val t=r.create(CreateTenant("ACME","12.345.678/0001-90")); val u=UUID.randomUUID(); r.grant(t.id,GrantRole(u,Role.FISCAL)); assertTrue(r.authorize(t.id,u,Role.FISCAL)); assertFalse(r.authorize(UUID.randomUUID(),u,Role.FISCAL)) }
}
