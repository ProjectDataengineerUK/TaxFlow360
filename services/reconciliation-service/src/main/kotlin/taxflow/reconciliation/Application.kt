package taxflow.reconciliation
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*
import taxflow.reconciliation.domain.*
import java.util.UUID

@SpringBootApplication class Application
fun main(args:Array<String>)=runApplication<Application>(*args)
@Configuration class ReconciliationConfiguration { @Bean fun reconciliationEngine()=ReconciliationEngine() }
@RestController @RequestMapping("/v1/reconciliations")
class ReconciliationController(private val engine:ReconciliationEngine) {
 @PostMapping @ResponseStatus(HttpStatus.CREATED)
 fun reconcile(@RequestHeader("X-Tenant-Id") tenant:UUID,@RequestBody command:ReconcileCommand)=engine.reconcile(tenant,command)
 @PostMapping("/{idempotencyKey}/reviews") @ResponseStatus(HttpStatus.CREATED)
 fun review(@RequestHeader("X-Tenant-Id") tenant:UUID,@RequestHeader("X-Actor-Id") actor:UUID,
  @RequestHeader("X-Roles") roles:String,@PathVariable idempotencyKey:String,@RequestBody command:ReviewCommand)=
  engine.review(tenant,idempotencyKey,actor,roles.split(',').map(String::trim).toSet(),command)
}
