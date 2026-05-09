namespace Eureka.Services
{
    public sealed class ActionManifestRenderer
    {
        public string RenderBlockedActions()
        {
            return "Blocked current actions\r\n" +
                "- download: blocked by native no-download policy\r\n" +
                "- mirror: blocked by native no-download policy\r\n" +
                "- install: blocked by native no-execute policy\r\n" +
                "- execute: blocked by native no-execute policy\r\n" +
                "- emulate: blocked by native no-execute policy\r\n\r\n" +
                "Safe alternatives\r\n" +
                "- view local snapshot fixture metadata\r\n" +
                "- inspect relay fixture envelope text\r\n" +
                "- cite or export descriptive manifests\r\n\r\n" +
                "No rights clearance, malware safety, installability, or compatibility certification is claimed.";
        }
    }
}
