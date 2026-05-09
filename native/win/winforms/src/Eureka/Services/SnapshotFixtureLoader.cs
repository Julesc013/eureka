using System;
using System.IO;

namespace Eureka.Services
{
    public sealed class SnapshotFixtureLoader
    {
        public string LoadFixtureTextFromArguments(string[] args)
        {
            string path;

            path = this.FindFixtureArgument(args);
            if (String.IsNullOrEmpty(path)) {
                return this.BuildEmbeddedFallbackFixture();
            }
            return this.LoadLocalFixtureText(path);
        }

        public string LoadLocalFixtureText(string path)
        {
            string fullPath;

            if (String.IsNullOrEmpty(path)) {
                return this.BuildEmbeddedFallbackFixture();
            }
            fullPath = Path.GetFullPath(path);
            if (!File.Exists(fullPath)) {
                return this.BuildEmbeddedFallbackFixture();
            }
            return File.ReadAllText(fullPath);
        }

        private string FindFixtureArgument(string[] args)
        {
            int index;

            if (args == null) {
                return String.Empty;
            }
            index = 0;
            while (index < args.Length) {
                if (String.Equals(args[index], "--fixture", StringComparison.OrdinalIgnoreCase) && index + 1 < args.Length) {
                    return args[index + 1];
                }
                index = index + 1;
            }
            return String.Empty;
        }

        private string BuildEmbeddedFallbackFixture()
        {
            return "schema_version: snapshot_fixture.v0\r\n" +
                "title: Eureka fixture snapshot\r\n" +
                "source posture: fixture only\r\n" +
                "evidence posture: example or reviewed local refs only\r\n" +
                "rights posture: no rights clearance claimed\r\n" +
                "risk posture: no malware safety claimed\r\n" +
                "action posture: descriptive action manifests only\r\n" +
                "limitations: read-only proof; no live access; no downloads; no execution\r\n";
        }
    }
}
