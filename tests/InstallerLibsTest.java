package test;

import com.elium.launcher.GameInstaller;
import com.elium.launcher.Net;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/** Библиотеки из install_profile.json установщика NeoForge: что и куда качать. */
public class InstallerLibsTest {
    private static int failed = 0;

    static void check(String what, boolean ok) {
        if (!ok) { System.out.println("FAIL " + what); failed++; }
    }

    public static void main(String[] args) throws Exception {
        Path jar = Path.of(System.getenv("TEMP"), "opencode", "neo-inst", "neoforge-installer.jar");
        if (!Files.exists(jar)) jar = Path.of("C:\\Users\\User\\AppData\\Local\\Temp\\opencode\\neo-inst\\neoforge-installer.jar");
        if (!Files.exists(jar)) {
            System.out.println("FAIL: нет установщика " + jar);
            System.exit(1);
        }
        Path libs = Files.createTempDirectory("libs");
        List<Net.Task> tasks = GameInstaller.installerLibraryTasks(jar, libs);

        check("больше 60 библиотек (было " + tasks.size() + ")", tasks.size() > 60);
        check("есть loader 4.0.44", tasks.stream().anyMatch(t ->
                t.target().equals(libs.resolve("net/neoforged/fancymodloader/loader/4.0.44/loader-4.0.44.jar"))));
        check("есть installertools 2.1.2", tasks.stream().anyMatch(t ->
                t.target().equals(libs.resolve("net/neoforged/installertools/installertools/2.1.2/installertools-2.1.2.jar"))));
        check("у всех есть sha1", tasks.stream().allMatch(t -> t.sha1() != null && t.sha1().length() == 40));
        check("все цели внутри libraries", tasks.stream().allMatch(t -> t.target().normalize().startsWith(libs)));
        check("у всех есть зеркало", tasks.stream().allMatch(t ->
                !com.elium.launcher.Mirrors.alternatives(t.url()).isEmpty()));

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
    }
}
