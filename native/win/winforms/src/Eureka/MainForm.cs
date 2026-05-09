using System;
using System.Windows.Forms;
using Eureka.Services;
using Eureka.UI;

namespace Eureka
{
    public sealed class MainForm : Form
    {
        private readonly SnapshotFixtureLoader snapshotLoader;
        private readonly RelayFixtureClient relayClient;
        private readonly ActionManifestRenderer actionRenderer;
        private readonly DiagnosticsService diagnosticsService;

        public MainForm(string[] args)
        {
            this.snapshotLoader = new SnapshotFixtureLoader();
            this.relayClient = new RelayFixtureClient();
            this.actionRenderer = new ActionManifestRenderer();
            this.diagnosticsService = new DiagnosticsService();
            this.Text = "Eureka WinForms Read-Only Proof";
            this.Width = 980;
            this.Height = 680;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BuildTabs(args);
        }

        private void BuildTabs(string[] args)
        {
            TabControl tabs;
            string fixtureText;
            string relayText;

            fixtureText = this.snapshotLoader.LoadFixtureTextFromArguments(args);
            relayText = this.relayClient.LoadRelayStatusFromFixtureText(fixtureText);

            tabs = new TabControl();
            tabs.Dock = DockStyle.Fill;
            tabs.TabPages.Add(this.BuildPage("Search", new ReadOnlySearchPanel(fixtureText)));
            tabs.TabPages.Add(this.BuildPage("Object", new ObjectSummaryPanel(fixtureText)));
            tabs.TabPages.Add(this.BuildPage("Relay", new RelayStatusPanel(relayText)));
            tabs.TabPages.Add(this.BuildPage("Blocked", new BlockedActionPanel(this.actionRenderer.RenderBlockedActions())));
            tabs.TabPages.Add(this.BuildPage("Diagnostics", new ObjectSummaryPanel(this.diagnosticsService.BuildDiagnosticsText())));
            this.Controls.Add(tabs);
        }

        private TabPage BuildPage(string title, Control control)
        {
            TabPage page;

            page = new TabPage(title);
            control.Dock = DockStyle.Fill;
            page.Controls.Add(control);
            return page;
        }
    }
}
