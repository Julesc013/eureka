using System.Collections.Generic;

namespace Eureka.Models
{
    public sealed class SnapshotSummary
    {
        public SnapshotSummary()
        {
            this.Limitations = new List<string>();
            this.NoClaims = new List<string>();
        }

        public string SnapshotId { get; set; }
        public string Title { get; set; }
        public string SourcePosture { get; set; }
        public string EvidencePosture { get; set; }
        public string RightsPosture { get; set; }
        public string RiskPosture { get; set; }
        public string ActionPosture { get; set; }
        public IList<string> Limitations { get; private set; }
        public IList<string> NoClaims { get; private set; }
    }

    public sealed class RelayStatusSummary
    {
        public string RelayMode { get; set; }
        public bool ReadOnly { get; set; }
        public bool LocalhostOnly { get; set; }
        public bool LiveAccessEnabled { get; set; }
        public bool DownloadsEnabled { get; set; }
        public bool TelemetryEnabled { get; set; }
    }
}
