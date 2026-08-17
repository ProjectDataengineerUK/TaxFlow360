package taxflow.tax.domain

import java.net.URI
import java.time.Instant
import java.time.LocalDate

data class LegalSource(
    val sourceUrl: URI,
    val authority: String,
    val documentId: String,
    val provision: String,
    val publishedOn: LocalDate,
    val capturedAt: Instant,
    val contentSha256: String,
) {
    init {
        require(sourceUrl.scheme == "https") { "legal source must use HTTPS" }
        require(sourceUrl.userInfo == null && sourceUrl.host != null) { "legal source URL is not allowed" }
        require(authority.isNotBlank() && documentId.isNotBlank() && provision.isNotBlank())
        require(Regex("^[a-f0-9]{64}$").matches(contentSha256)) { "contentSha256 must be lowercase SHA-256" }
        require(!isIpLiteral(sourceUrl.host)) { "legal source host must not be an IP literal" }
    }

    fun requireOfficialHost(allowedHosts: Set<String>) {
        val normalized = sourceUrl.host.lowercase().trimEnd('.')
        require(allowedHosts.map { it.lowercase().trimEnd('.') }.any { normalized == it }) {
            "legal source host is not an approved official authority"
        }
    }

    private fun isIpLiteral(host: String): Boolean =
        host.contains(':') || Regex("^\\d{1,3}(\\.\\d{1,3}){3}$").matches(host)
}
