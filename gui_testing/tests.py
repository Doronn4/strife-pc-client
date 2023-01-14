import wx

app = wx.App()
frame = wx.Frame(None, title="Font Preview")

# Create a panel
panel = wx.Panel(frame)

# Create a vertical sizer
sizer = wx.BoxSizer(wx.VERTICAL)

# Create an instance of the FontEnumerator
fe = wx.FontEnumerator()

# Enumerate the fonts
fe.EnumerateFacenames()

# Get the list of fonts
fonts = fe.GetFacenames()

# Create a label for each font
for font in fonts:
    label = wx.StaticText(panel, label=font)
    label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=font))
    sizer.Add(label, 0, wx.ALL, 5)

# Set the sizer for the panel
panel.SetSizer(sizer)

frame.Show()
app.MainLoop()
