using System.Windows.Forms;

namespace Eureka.UI
{
    public sealed class BlockedActionPanel : UserControl
    {
        public BlockedActionPanel(string blockedActionText)
        {
            TextBox textBox;

            textBox = new TextBox();
            textBox.Multiline = true;
            textBox.ReadOnly = true;
            textBox.ScrollBars = ScrollBars.Vertical;
            textBox.Dock = DockStyle.Fill;
            textBox.Text = blockedActionText;
            this.Controls.Add(textBox);
        }
    }
}
