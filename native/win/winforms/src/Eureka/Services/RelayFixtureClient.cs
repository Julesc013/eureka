using Eureka.Models;

namespace Eureka.Services
{
    public sealed class RelayFixtureClient
    {
        public string LoadRelayStatusFromFixtureText(string fixtureText)
        {
            RelayStatusSummary status;

            status = this.ParseStatus(fixtureText);
            return "relay mode: " + status.RelayMode + "\r\n" +
                "localhost only: " + status.LocalhostOnly + "\r\n" +
                "read only: " + status.ReadOnly + "\r\n" +
                "live access enabled: " + status.LiveAccessEnabled + "\r\n" +
                "downloads enabled: " + status.DownloadsEnabled + "\r\n" +
                "telemetry enabled: " + status.TelemetryEnabled + "\r\n" +
                "status: fixture envelope only; no server is started by this client";
        }

        private RelayStatusSummary ParseStatus(string text)
        {
            RelayStatusSummary status;

            status = new RelayStatusSummary();
            status.RelayMode = this.Contains(text, "localhost_readonly") ? "localhost_readonly_fixture" : "fixture_preview";
            status.LocalhostOnly = true;
            status.ReadOnly = true;
            status.LiveAccessEnabled = false;
            status.DownloadsEnabled = false;
            status.TelemetryEnabled = false;
            return status;
        }

        private bool Contains(string text, string token)
        {
            if (text == null) {
                return false;
            }
            return text.IndexOf(token, System.StringComparison.OrdinalIgnoreCase) >= 0;
        }
    }
}
