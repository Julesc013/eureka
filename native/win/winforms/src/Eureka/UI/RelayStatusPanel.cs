using System.Windows.Forms;

namespace Eureka.UI
{
    public sealed class RelayStatusPanel : UserControl
    {
        public RelayStatusPanel(string statusText)
        {
            TextBox textBox;

            textBox = new TextBox();
            textBox.Multiline = true;
            textBox.ReadOnly = true;
            textBox.ScrollBars = ScrollBars.Vertical;
            textBox.Dock = DockStyle.Fill;
            textBox.Text = statusText;
            this.Controls.Add(textBox);
        }
    }
}
