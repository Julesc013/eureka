using System;
using System.Reflection;

namespace Eureka.Services
{
    public sealed class DiagnosticsService
    {
        public string BuildDiagnosticsText()
        {
            Assembly assembly;

            assembly = Assembly.GetExecutingAssembly();
            return "Eureka WinForms read-only proof\r\n" +
                "assembly: " + assembly.GetName().Name + "\r\n" +
                "version: " + assembly.GetName().Version + "\r\n" +
                "framework: .NET Framework 4.8\r\n" +
                "scope: local fixture display over snapshot, relay, and action contracts\r\n" +
                "network: disabled by policy\r\n" +
                "writes: no persistent user state\r\n" +
                "telemetry: disabled\r\n" +
                "generated at runtime note: " + DateTime.UtcNow.ToString("u");
        }
    }
}
