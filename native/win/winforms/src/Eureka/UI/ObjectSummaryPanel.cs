using System.Windows.Forms;

namespace Eureka.UI
{
    public sealed class ObjectSummaryPanel : UserControl
    {
        public ObjectSummaryPanel(string summaryText)
        {
            TextBox textBox;

            textBox = new TextBox();
            textBox.Multiline = true;
            textBox.ReadOnly = true;
            textBox.ScrollBars = ScrollBars.Both;
            textBox.Dock = DockStyle.Fill;
            textBox.Text = summaryText;
            this.Controls.Add(textBox);
        }
    }
}
