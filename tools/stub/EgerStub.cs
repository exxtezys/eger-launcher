using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Windows.Forms;

static class EgerStub
{
    const string Build = "__BUILD__";

    [STAThread]
    static int Main()
    {
        try
        {
            string root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Eger", "launcher");
            string dir = Path.Combine(root, Build);
            string exe = Path.Combine(dir, "EgerLauncher.exe");
            if (!File.Exists(Path.Combine(dir, ".ok")))
            {
                Unpack(root, dir);
            }
            Process.Start(new ProcessStartInfo(exe) { UseShellExecute = false, WorkingDirectory = dir });
            return 0;
        }
        catch (Exception e)
        {
            MessageBox.Show("Не удалось запустить лаунчер:\n" + e.Message, "Егерь", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    static void Unpack(string root, string dir)
    {
        string tmp = dir + ".tmp";
        if (Directory.Exists(tmp)) Directory.Delete(tmp, true);
        Directory.CreateDirectory(tmp);
        using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("app.zip"))
        using (ZipArchive zip = new ZipArchive(s, ZipArchiveMode.Read))
        {
            zip.ExtractToDirectory(tmp);
        }
        if (Directory.Exists(dir)) Directory.Delete(dir, true);
        Directory.Move(tmp, dir);
        File.WriteAllText(Path.Combine(dir, ".ok"), Build);

        foreach (string old in Directory.GetDirectories(root))
        {
            if (old.Equals(dir, StringComparison.OrdinalIgnoreCase)) continue;
            try
            {
                Directory.Delete(old, true);
            }
            catch (IOException e)
            {
                Debug.WriteLine("old launcher build still in use: " + old + " " + e.Message);
            }
            catch (UnauthorizedAccessException e)
            {
                Debug.WriteLine("old launcher build locked: " + old + " " + e.Message);
            }
        }
    }
}
