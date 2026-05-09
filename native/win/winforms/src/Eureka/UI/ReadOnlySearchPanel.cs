using System.Windows.Forms;

namespace Eureka.UI
{
    public sealed class ReadOnlySearchPanel : UserControl
    {
        public ReadOnlySearchPanel(string fixtureText)
        {
            TextBox textBox;

            textBox = new TextBox();
            textBox.Multiline = true;
            textBox.ReadOnly = true;
            textBox.ScrollBars = ScrollBars.Both;
            textBox.Dock = DockStyle.Fill;
            textBox.Text = "Search fixture summary\r\n\r\n" + fixtureText;
            this.Controls.Add(textBox);
        }
    }
}
